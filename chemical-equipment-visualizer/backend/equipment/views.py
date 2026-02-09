import pandas as pd
import numpy as np
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import EquipmentDataset, EquipmentItem
from .serializers import (
    EquipmentDatasetSerializer, 
    EquipmentItemSerializer, 
    DataSummarySerializer,
    CSVUploadSerializer
)


class EquipmentDatasetViewSet(viewsets.ModelViewSet):
    """ViewSet for EquipmentDataset model."""
    queryset = EquipmentDataset.objects.all()
    serializer_class = EquipmentDatasetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return datasets for the current user."""
        user = self.request.user
        if user.is_authenticated:
            return EquipmentDataset.objects.filter(uploaded_by=user)
        return EquipmentDataset.objects.none()
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_csv(self, request):
        """Upload and parse CSV file."""
        serializer = CSVUploadSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        csv_file = serializer.validated_data['file']
        name = serializer.validated_data.get('name', csv_file.name)
        
        try:
            # Read CSV file (try normal read; we'll attempt a fallback if columns missing)
            try:
                df = pd.read_csv(csv_file)
            except Exception:
                try:
                    csv_file.seek(0)
                except Exception:
                    pass
                df = pd.read_csv(csv_file, sep=None, engine='python')

            # Keep original columns for diagnostics
            original_columns = list(df.columns)

            # Conservative mapping for common header variants -> canonical names
            canonical_map = {
                'equipment name': 'Equipment Name',
                'equipment_name': 'Equipment Name',
                'name': 'Equipment Name',
                'type': 'Type',
                'equipment type': 'Type',
                'equipment_type': 'Type',
                'flowrate': 'Flowrate',
                'flow_rate': 'Flowrate',
                'flow rate': 'Flowrate',
                'flow': 'Flowrate',
                'pressure': 'Pressure',
                'pres': 'Pressure',
                'temperature': 'Temperature',
                'temp': 'Temperature'
            }

            rename_map = {}
            for col in original_columns:
                key = str(col).strip().lower()
                if key in canonical_map:
                    rename_map[col] = canonical_map[key]

            if rename_map:
                df = df.rename(columns=rename_map)

            # Validate required columns
            required_columns = ['Equipment Name', 'Type']
            missing_columns = [col for col in required_columns if col not in df.columns]

            # If missing, try a more flexible parse (autodetect delimiter) and remap once
            if missing_columns:
                try:
                    csv_file.seek(0)
                except Exception:
                    pass
                try:
                    df = pd.read_csv(csv_file, sep=None, engine='python')
                    original_columns = list(df.columns)
                    rename_map = {}
                    for col in original_columns:
                        key = str(col).strip().lower()
                        if key in canonical_map:
                            rename_map[col] = canonical_map[key]
                    if rename_map:
                        df = df.rename(columns=rename_map)
                    missing_columns = [col for col in required_columns if col not in df.columns]
                except Exception:
                    pass

            if missing_columns:
                return Response(
                    {'error': f'Missing required columns: {", ".join(missing_columns)}',
                     'received_columns': original_columns},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create dataset
            dataset = EquipmentDataset.objects.create(
                name=name,
                uploaded_by=request.user,
                csv_file=csv_file
            )
            
            # Create equipment items
            for _, row in df.iterrows():
                EquipmentItem.objects.create(
                    dataset=dataset,
                    equipment_name=str(row.get('Equipment Name', '')),
                    equipment_type=str(row.get('Type', '')),
                    flowrate=self._parse_float(row.get('Flowrate')),
                    pressure=self._parse_float(row.get('Pressure')),
                    temperature=self._parse_float(row.get('Temperature'))
                )
            
            # Calculate and store summary
            summary = self._calculate_summary(df)
            # Ensure summary contains only native Python types (no numpy/pandas types)
            def _to_builtin(obj):
                if isinstance(obj, dict):
                    return {k: _to_builtin(v) for k, v in obj.items()}
                if isinstance(obj, list):
                    return [_to_builtin(v) for v in obj]
                if isinstance(obj, (np.integer,)):
                    return int(obj)
                if isinstance(obj, (np.floating,)):
                    return float(obj)
                if isinstance(obj, (np.bool_,)):
                    return bool(obj)
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                return obj

            summary = _to_builtin(summary)
            dataset.summary_data = summary
            dataset.save()
            
            return Response({
                'message': 'File uploaded successfully',
                'dataset_id': dataset.id,
                'summary': summary
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Error processing file: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get summary statistics for a dataset."""
        dataset = self.get_object()
        
        if dataset.summary_data:
            return Response(dataset.summary_data)
        
        # Calculate summary from items
        items = dataset.items.all()
        df = pd.DataFrame([{
            'Equipment Name': item.equipment_name,
            'Type': item.equipment_type,
            'Flowrate': item.flowrate,
            'Pressure': item.pressure,
            'Temperature': item.temperature
        } for item in items])
        
        summary = self._calculate_summary(df)
        return Response(summary)
    
    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """Get all data items for a dataset."""
        dataset = self.get_object()
        items = dataset.items.all()
        serializer = EquipmentItemSerializer(items, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def chart_data(self, request, pk=None):
        """Get chart data for visualization."""
        dataset = self.get_object()
        items = dataset.items.all()
        
        # Type distribution
        type_counts = {}
        flowrate_by_type = {}
        pressure_by_type = {}
        temperature_by_type = {}
        
        for item in items:
            eq_type = item.equipment_type
            
            # Count by type
            type_counts[eq_type] = type_counts.get(eq_type, 0) + 1
            
            # Flowrate by type
            if item.flowrate is not None:
                if eq_type not in flowrate_by_type:
                    flowrate_by_type[eq_type] = []
                flowrate_by_type[eq_type].append(item.flowrate)
            
            # Pressure by type
            if item.pressure is not None:
                if eq_type not in pressure_by_type:
                    pressure_by_type[eq_type] = []
                pressure_by_type[eq_type].append(item.pressure)
            
            # Temperature by type
            if item.temperature is not None:
                if eq_type not in temperature_by_type:
                    temperature_by_type[eq_type] = []
                temperature_by_type[eq_type].append(item.temperature)
        
        # Calculate averages
        avg_flowrate = {k: sum(v)/len(v) for k, v in flowrate_by_type.items() if v}
        avg_pressure = {k: sum(v)/len(v) for k, v in pressure_by_type.items() if v}
        avg_temperature = {k: sum(v)/len(v) for k, v in temperature_by_type.items() if v}
        
        return Response({
            'type_distribution': type_counts,
            'avg_flowrate_by_type': avg_flowrate,
            'avg_pressure_by_type': avg_pressure,
            'avg_temperature_by_type': avg_temperature,
            'labels': list(type_counts.keys()),
            'type_counts': list(type_counts.values())
        })
    
    @action(detail=True, methods=['get'])
    def generate_pdf(self, request, pk=None):
        """Generate PDF report for a dataset."""
        dataset = self.get_object()
        items = dataset.items.all()
        
        # Create PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="equipment_report_{dataset.id}.pdf"'
        
        doc = SimpleDocTemplate(response, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1a5276'),
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        elements.append(Paragraph("Chemical Equipment Report", title_style))
        elements.append(Spacer(1, 20))
        
        # Dataset info
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=10
        )
        elements.append(Paragraph(f"<b>Dataset:</b> {dataset.name}", info_style))
        elements.append(Paragraph(f"<b>Uploaded:</b> {dataset.uploaded_at.strftime('%Y-%m-%d %H:%M')}", info_style))
        elements.append(Paragraph(f"<b>Total Items:</b> {items.count()}", info_style))
        elements.append(Spacer(1, 20))
        
        # Summary Statistics
        elements.append(Paragraph("Summary Statistics", styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        summary = dataset.summary_data or self._calculate_summary_from_items(items)
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Equipment', str(summary.get('total_count', 0))],
            ['Average Flowrate', f"{summary.get('avg_flowrate', 0):.2f}" if summary.get('avg_flowrate') else 'N/A'],
            ['Average Pressure', f"{summary.get('avg_pressure', 0):.2f}" if summary.get('avg_pressure') else 'N/A'],
            ['Average Temperature', f"{summary.get('avg_temperature', 0):.2f}" if summary.get('avg_temperature') else 'N/A'],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        
        # Type Distribution
        if summary.get('type_distribution'):
            elements.append(Paragraph("Equipment Type Distribution", styles['Heading2']))
            elements.append(Spacer(1, 10))
            
            type_data = [['Equipment Type', 'Count']]
            for eq_type, count in summary['type_distribution'].items():
                type_data.append([eq_type, str(count)])
            
            type_table = Table(type_data, colWidths=[3*inch, 3*inch])
            type_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(type_table)
            elements.append(Spacer(1, 20))
        
        # Equipment Details Table
        elements.append(Paragraph("Equipment Details", styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        detail_data = [['Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']]
        for item in items[:50]:  # Limit to first 50 items
            detail_data.append([
                item.equipment_name[:25],
                item.equipment_type,
                f"{item.flowrate:.2f}" if item.flowrate else 'N/A',
                f"{item.pressure:.2f}" if item.pressure else 'N/A',
                f"{item.temperature:.2f}" if item.temperature else 'N/A'
            ])
        
        if items.count() > 50:
            detail_data.append(['...', '...', '...', '...', f'({items.count() - 50} more items)'])
        
        detail_table = Table(detail_data, colWidths=[2*inch, 1.2*inch, 1*inch, 1*inch, 1*inch])
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(detail_table)
        
        # Build PDF
        doc.build(elements)
        
        return response
    
    def _parse_float(self, value):
        """Parse value to float, return None if not possible."""
        if pd.isna(value) or value is None or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _calculate_summary(self, df):
        """Calculate summary statistics from DataFrame."""
        summary = {
            'total_count': len(df),
            'avg_flowrate': None,
            'avg_pressure': None,
            'avg_temperature': None,
            'min_flowrate': None,
            'max_flowrate': None,
            'min_pressure': None,
            'max_pressure': None,
            'min_temperature': None,
            'max_temperature': None,
            'type_distribution': {}
        }
        
        # Flowrate statistics
        if 'Flowrate' in df.columns:
            flowrate = pd.to_numeric(df['Flowrate'], errors='coerce').dropna()
            if len(flowrate) > 0:
                summary['avg_flowrate'] = round(flowrate.mean(), 2)
                summary['min_flowrate'] = round(flowrate.min(), 2)
                summary['max_flowrate'] = round(flowrate.max(), 2)
        
        # Pressure statistics
        if 'Pressure' in df.columns:
            pressure = pd.to_numeric(df['Pressure'], errors='coerce').dropna()
            if len(pressure) > 0:
                summary['avg_pressure'] = round(pressure.mean(), 2)
                summary['min_pressure'] = round(pressure.min(), 2)
                summary['max_pressure'] = round(pressure.max(), 2)
        
        # Temperature statistics
        if 'Temperature' in df.columns:
            temperature = pd.to_numeric(df['Temperature'], errors='coerce').dropna()
            if len(temperature) > 0:
                summary['avg_temperature'] = round(temperature.mean(), 2)
                summary['min_temperature'] = round(temperature.min(), 2)
                summary['max_temperature'] = round(temperature.max(), 2)
        
        # Type distribution
        if 'Type' in df.columns:
            type_counts = df['Type'].value_counts().to_dict()
            summary['type_distribution'] = {str(k): int(v) for k, v in type_counts.items()}
        
        return summary
    
    def _calculate_summary_from_items(self, items):
        """Calculate summary from EquipmentItem queryset."""
        df = pd.DataFrame([{
            'Equipment Name': item.equipment_name,
            'Type': item.equipment_type,
            'Flowrate': item.flowrate,
            'Pressure': item.pressure,
            'Temperature': item.temperature
        } for item in items])
        
        return self._calculate_summary(df)


class EquipmentItemViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for EquipmentItem model."""
    queryset = EquipmentItem.objects.all()
    serializer_class = EquipmentItemSerializer
    permission_classes = [IsAuthenticated]
