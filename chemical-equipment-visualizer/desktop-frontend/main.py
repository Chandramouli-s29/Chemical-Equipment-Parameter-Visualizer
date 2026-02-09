#!/usr/bin/env python3
"""
Chemical Equipment Visualizer - Desktop Application
PyQt5 Frontend with Matplotlib for data visualization
"""

import sys
import requests
import base64
import json
from datetime import datetime
from typing import Optional, Dict, List, Any

import pandas as pd
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QStackedWidget, QFrame, QSplitter,
    QTabWidget, QGroupBox, QGridLayout, QHeaderView, QProgressBar,
    QDialog, QFormLayout, QDialogButtonBox, QComboBox, QTextEdit,
    QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor

# API Configuration
API_BASE_URL = "http://localhost:8000/api"


class APIClient:
    """Client for communicating with Django backend API."""
    
    def __init__(self):
        self.auth_token: Optional[str] = None
        self.session = requests.Session()
    
    def login(self, username: str, password: str) -> bool:
        """Authenticate with the backend."""
        try:
            auth_str = base64.b64encode(f"{username}:{password}".encode()).decode()
            headers = {"Authorization": f"Basic {auth_str}"}
            response = self.session.get(f"{API_BASE_URL}/datasets/", headers=headers, timeout=5)
            
            if response.status_code == 200:
                self.auth_token = auth_str
                return True
            return False
        except requests.RequestException:
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers with authentication."""
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Basic {self.auth_token}"
        return headers
    
    def get_datasets(self) -> List[Dict[str, Any]]:
        """Get all datasets."""
        response = self.session.get(
            f"{API_BASE_URL}/datasets/",
            headers=self.get_headers(),
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def upload_csv(self, file_path: str, name: str) -> Dict[str, Any]:
        """Upload a CSV file."""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'name': name}
            response = self.session.post(
                f"{API_BASE_URL}/datasets/upload_csv/",
                files=files,
                data=data,
                headers=self.get_headers(),
                timeout=30
            )
        response.raise_for_status()
        return response.json()
    
    def get_summary(self, dataset_id: int) -> Dict[str, Any]:
        """Get summary statistics for a dataset."""
        response = self.session.get(
            f"{API_BASE_URL}/datasets/{dataset_id}/summary/",
            headers=self.get_headers(),
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def get_data(self, dataset_id: int) -> List[Dict[str, Any]]:
        """Get all data items for a dataset."""
        response = self.session.get(
            f"{API_BASE_URL}/datasets/{dataset_id}/data/",
            headers=self.get_headers(),
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def get_chart_data(self, dataset_id: int) -> Dict[str, Any]:
        """Get chart data for visualization."""
        response = self.session.get(
            f"{API_BASE_URL}/datasets/{dataset_id}/chart_data/",
            headers=self.get_headers(),
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def download_pdf(self, dataset_id: int, save_path: str) -> bool:
        """Download PDF report."""
        response = self.session.get(
            f"{API_BASE_URL}/datasets/{dataset_id}/generate_pdf/",
            headers=self.get_headers(),
            timeout=30,
            stream=True
        )
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    
    def delete_dataset(self, dataset_id: int) -> bool:
        """Delete a dataset."""
        response = self.session.delete(
            f"{API_BASE_URL}/datasets/{dataset_id}/",
            headers=self.get_headers(),
            timeout=10
        )
        return response.status_code == 204


class LoginDialog(QDialog):
    """Login dialog for authentication."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login - Chemical Equipment Visualizer")
        self.setFixedSize(400, 300)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Chemical Equipment Visualizer")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1e40af; margin-bottom: 10px;")
        layout.addWidget(title)
        
        subtitle = QLabel("Please sign in to continue")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #64748b; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        # Form
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setText("admin")
        form_layout.addRow("Username:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setText("admin")
        form_layout.addRow("Password:", self.password_input)
        
        layout.addLayout(form_layout)
        
        # Info label
        info = QLabel("Default: admin / admin")
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("color: #94a3b8; font-size: 12px; margin: 10px 0;")
        layout.addWidget(info)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                background-color: white;
                min-width: 200px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton[text="OK"] {
                background-color: #3b82f6;
                color: white;
                border: none;
            }
            QPushButton[text="OK"]:hover {
                background-color: #2563eb;
            }
            QPushButton[text="Cancel"] {
                background-color: #e2e8f0;
                color: #475569;
                border: none;
            }
        """)
    
    def get_credentials(self) -> tuple:
        return self.username_input.text(), self.password_input.text()


class ChartWidget(QWidget):
    """Widget for displaying matplotlib charts."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.figure.patch.set_facecolor('#f8fafc')
        self.canvas = FigureCanvas(self.figure)
        
        layout.addWidget(self.canvas)
    
    def plot_type_distribution(self, type_distribution: Dict[str, int]):
        """Plot pie chart for equipment type distribution."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        labels = list(type_distribution.keys())
        sizes = list(type_distribution.values())
        # A longer colors list to cover many labels
        colors = [
            '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#0ea5e9', '#f97316',
            '#06b6d4', '#84cc16', '#ef65a6', '#60a5fa', '#34d399', '#f43f5e', '#fb923c', '#a78bfa'
        ]
        
        # Draw a larger pie by increasing the figure size for this chart and placing the legend outside
        self.figure.set_size_inches(10, 8)
        ax.clear()

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=None,                # omit wedge labels to avoid crowding
            autopct='%1.1f%%',
            startangle=90,
            colors=colors[:len(labels)],
            pctdistance=0.75,
            wedgeprops={'linewidth': 0.6, 'edgecolor': 'white'}
        )

        # Create a clear legend outside the pie
        ax.legend(
            wedges,
            labels,
            title='Equipment Types',
            loc='center left',
            bbox_to_anchor=(1.02, 0.5),
            fontsize=9,
            frameon=False
        )

        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')

        ax.set_title('Equipment Type Distribution', fontsize=16, fontweight='bold', pad=20)
        ax.axis('equal')
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_avg_parameters(self, chart_data: Dict[str, Any]):
        """Plot bar chart for average parameters by type."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        labels = chart_data.get('labels', [])
        avg_flowrate = [chart_data.get('avg_flowrate_by_type', {}).get(t, 0) for t in labels]
        avg_pressure = [chart_data.get('avg_pressure_by_type', {}).get(t, 0) for t in labels]
        avg_temperature = [chart_data.get('avg_temperature_by_type', {}).get(t, 0) for t in labels]
        
        x = range(len(labels))
        width = 0.25
        
        ax.bar([i - width for i in x], avg_flowrate, width, label='Flowrate', color='#3b82f6')
        ax.bar(x, avg_pressure, width, label='Pressure', color='#f59e0b')
        ax.bar([i + width for i in x], avg_temperature, width, label='Temperature', color='#ef4444')
        
        ax.set_xlabel('Equipment Type', fontweight='bold')
        ax.set_ylabel('Average Value', fontweight='bold')
        ax.set_title('Average Parameters by Equipment Type', fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_count_by_type(self, chart_data: Dict[str, Any]):
        """Plot line chart for equipment count by type with clearer labels and annotations."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        labels = chart_data.get('labels', [])
        counts = chart_data.get('type_counts', [])
        
        # Use numeric x positions for better control over ticks and annotations
        x = list(range(len(labels)))
        ax.plot(x, counts, marker='o', linewidth=2, markersize=6, color='#10b981')
        ax.fill_between(x, counts, alpha=0.25, color='#10b981')
        
        ax.set_xlabel('Equipment Type', fontweight='bold')
        ax.set_ylabel('Count', fontweight='bold')
        ax.set_title('Equipment Count by Type', fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        
        # Rotate and shorten x tick labels to avoid overlap
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
        plt = None
        try:
            import matplotlib.pyplot as _plt
            plt = _plt
        except Exception:
            pass

        # Add boxed annotations and stagger to reduce collisions
        texts = []
        if counts:
            y_max = max(counts)
        else:
            y_max = 0

        # Add boxed annotations; keep them close to markers and avoid pushing above axis top
        texts = []
        for i, v in enumerate(counts):
            # If this point is at the maximum, place label slightly below to avoid going over the top
            if v >= y_max:
                y = v - 0.15
                va = 'top'
            else:
                y = v + 0.12
                va = 'bottom'

            # Ensure the label is not negative
            if y < 0:
                y = v + 0.12
                va = 'bottom'

            txt = ax.text(i, y, str(v), ha='center', va=va, fontsize=9, fontweight='bold',
                          bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='none', alpha=0.9),
                          clip_on=True)
            texts.append(txt)

        # If adjustText is available, try to improve placement
        try:
            from adjustText import adjust_text
            adjust_text(texts, only_move={'points': 'y', 'texts': 'y'}, ax=ax)
        except Exception:
            # fallback (already staggered)
            pass

        self.figure.tight_layout()
        self.canvas.draw()
    
    def clear(self):
        """Clear the chart."""
        self.figure.clear()
        self.canvas.draw()


class DataTableWidget(QWidget):
    """Widget for displaying equipment data in a table."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            'Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'
        ])
        
        # Style the table
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #f1f5f9;
                padding: 10px;
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #e2e8f0;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f1f5f9;
            }
            QTableWidget::item:selected {
                background-color: #dbeafe;
            }
        """)
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.table)
    
    def set_data(self, data: List[Dict[str, Any]]):
        """Set table data."""
        self.table.setRowCount(len(data))
        
        for row_idx, item in enumerate(data):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(item.get('equipment_name', ''))))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(item.get('equipment_type', ''))))
            
            flowrate = item.get('flowrate')
            self.table.setItem(row_idx, 2, QTableWidgetItem(f"{flowrate:.2f}" if flowrate is not None else '-'))
            
            pressure = item.get('pressure')
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"{pressure:.2f}" if pressure is not None else '-'))
            
            temperature = item.get('temperature')
            self.table.setItem(row_idx, 4, QTableWidgetItem(f"{temperature:.2f}" if temperature is not None else '-'))
        
        self.table.resizeRowsToContents()
    
    def clear(self):
        """Clear the table."""
        self.table.setRowCount(0)


class SummaryCardsWidget(QWidget):
    """Widget for displaying summary statistics cards."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(15)
        
        # Create summary cards
        self.cards = {}
        card_configs = [
            ('total', 'Total Equipment', '#3b82f6', '#eff6ff'),
            ('types', 'Equipment Types', '#10b981', '#f0fdf4'),
            ('flowrate', 'Avg Flowrate', '#f59e0b', '#fffbeb'),
            ('pressure', 'Avg Pressure', '#ef4444', '#fef2f2'),
            ('temperature', 'Avg Temperature', '#8b5cf6', '#faf5ff'),
        ]
        
        for key, title, color, bg_color in card_configs:
            card = self.create_card(title, color, bg_color)
            self.cards[key] = card
            layout.addWidget(card)
    
    def create_card(self, title: str, color: str, bg_color: str) -> QFrame:
        """Create a summary card."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {color}33;
                border-radius: 10px;
                padding: 15px;
                min-width: 150px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: 600;")
        layout.addWidget(title_label)
        
        value_label = QLabel("-")
        value_label.setStyleSheet(f"color: #1e293b; font-size: 24px; font-weight: bold;")
        value_label.setObjectName("value")
        layout.addWidget(value_label)
        
        return card
    
    def update_values(self, summary: Dict[str, Any]):
        """Update card values from summary data."""
        values = {
            'total': str(summary.get('total_count', 0)),
            'types': str(len(summary.get('type_distribution', {}))),
            'flowrate': f"{summary.get('avg_flowrate', 0):.1f}" if summary.get('avg_flowrate') else '-',
            'pressure': f"{summary.get('avg_pressure', 0):.1f}" if summary.get('avg_pressure') else '-',
            'temperature': f"{summary.get('avg_temperature', 0):.1f}" if summary.get('avg_temperature') else '-',
        }
        
        for key, value in values.items():
            card = self.cards.get(key)
            if card:
                value_label = card.findChild(QLabel, "value")
                if value_label:
                    value_label.setText(value)
    
    def clear(self):
        """Clear all card values."""
        for card in self.cards.values():
            value_label = card.findChild(QLabel, "value")
            if value_label:
                value_label.setText("-")


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.current_dataset_id: Optional[int] = None
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        self.setWindowTitle("Chemical Equipment Visualizer")
        self.setMinimumSize(1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Content area with sidebar and main content
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Sidebar
        sidebar = self.create_sidebar()
        content_splitter.addWidget(sidebar)
        
        # Main content
        self.main_content = self.create_main_content()
        content_splitter.addWidget(self.main_content)
        
        content_splitter.setSizes([250, 950])
        content_splitter.setHandleWidth(1)
        
        main_layout.addWidget(content_splitter)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def create_header(self) -> QFrame:
        """Create application header."""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #0f172a;
                padding: 0px;
            }
        """)
        header.setFixedHeight(60)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # Logo and title
        title_layout = QHBoxLayout()
        
        icon_label = QLabel("⚗️")
        icon_label.setStyleSheet("font-size: 24px;")
        title_layout.addWidget(icon_label)
        
        title = QLabel("Chemical Equipment Visualizer")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: white;")
        title_layout.addWidget(title)
        
        subtitle = QLabel("| Data Analytics Platform")
        subtitle.setStyleSheet("color: #94a3b8; margin-left: 10px;")
        title_layout.addWidget(subtitle)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94a3b8;
                border: 1px solid #334155;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1e293b;
                color: white;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)
        
        return header
    
    def create_sidebar(self) -> QFrame:
        """Create sidebar with navigation."""
        sidebar = QFrame()
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-right: 1px solid #e2e8f0;
            }
        """)
        sidebar.setFixedWidth(250)
        
        layout = QVBoxLayout(sidebar)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 20, 15, 20)
        
        # Navigation buttons
        nav_label = QLabel("NAVIGATION")
        nav_label.setStyleSheet("color: #64748b; font-size: 11px; font-weight: bold; padding: 5px;")
        layout.addWidget(nav_label)
        
        self.upload_btn = self.create_nav_button("📤 Upload Data", True)
        self.upload_btn.clicked.connect(lambda: self.switch_view('upload'))
        layout.addWidget(self.upload_btn)
        
        self.data_btn = self.create_nav_button("📊 Data & Charts", False)
        self.data_btn.clicked.connect(lambda: self.switch_view('data'))
        self.data_btn.setEnabled(False)
        layout.addWidget(self.data_btn)
        
        self.history_btn = self.create_nav_button("📜 History", True)
        self.history_btn.clicked.connect(lambda: self.switch_view('history'))
        layout.addWidget(self.history_btn)
        
        layout.addStretch()
        
        # Connection status
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #dcfce7;
                border: 1px solid #86efac;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        status_layout = QHBoxLayout(status_frame)
        status_layout.setSpacing(8)
        
        status_dot = QLabel("●")
        status_dot.setStyleSheet("color: #22c55e; font-size: 12px;")
        status_layout.addWidget(status_dot)
        
        status_text = QLabel("Connected")
        status_text.setStyleSheet("color: #166534; font-size: 12px; font-weight: 500;")
        status_layout.addWidget(status_text)
        
        layout.addWidget(status_frame)
        
        return sidebar
    
    def create_nav_button(self, text: str, enabled: bool) -> QPushButton:
        """Create navigation button."""
        btn = QPushButton(text)
        btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 12px 15px;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
                color: #475569;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
                color: #1e293b;
            }
            QPushButton:disabled {
                color: #94a3b8;
            }
            QPushButton[active="true"] {
                background-color: #dbeafe;
                color: #1d4ed8;
            }
        """)
        btn.setEnabled(enabled)
        btn.setCursor(Qt.PointingHandCursor if enabled else Qt.ArrowCursor)
        return btn
    
    def create_main_content(self) -> QStackedWidget:
        """Create main content area with stacked widgets."""
        stack = QStackedWidget()
        
        # Upload view
        self.upload_view = self.create_upload_view()
        stack.addWidget(self.upload_view)
        
        # Data view
        self.data_view = self.create_data_view()
        stack.addWidget(self.data_view)
        
        # History view
        self.history_view = self.create_history_view()
        stack.addWidget(self.history_view)
        
        return stack
    
    def create_upload_view(self) -> QWidget:
        """Create upload view."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Upload Equipment Data")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #1e293b; margin-bottom: 10px;")
        layout.addWidget(title)
        
        subtitle = QLabel("Upload a CSV file containing equipment data for analysis")
        subtitle.setStyleSheet("color: #64748b; margin-bottom: 30px;")
        layout.addWidget(subtitle)
        
        # Upload area
        upload_frame = QFrame()
        upload_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px dashed #cbd5e1;
                border-radius: 12px;
                padding: 40px;
            }
            QFrame:hover {
                border-color: #3b82f6;
                background-color: #f8fafc;
            }
        """)
        upload_frame.setCursor(Qt.PointingHandCursor)
        upload_frame.mousePressEvent = lambda e: self.select_file()
        
        upload_layout = QVBoxLayout(upload_frame)
        upload_layout.setAlignment(Qt.AlignCenter)
        
        upload_icon = QLabel("📁")
        upload_icon.setStyleSheet("font-size: 48px;")
        upload_icon.setAlignment(Qt.AlignCenter)
        upload_layout.addWidget(upload_icon)
        
        upload_text = QLabel("Click to select a CSV file")
        upload_text.setFont(QFont("Arial", 14))
        upload_text.setStyleSheet("color: #1e293b; margin-top: 15px;")
        upload_text.setAlignment(Qt.AlignCenter)
        upload_layout.addWidget(upload_text)
        
        upload_hint = QLabel("Supports CSV files with columns: Equipment Name, Type, Flowrate, Pressure, Temperature")
        upload_hint.setStyleSheet("color: #94a3b8; font-size: 12px; margin-top: 10px;")
        upload_hint.setAlignment(Qt.AlignCenter)
        upload_layout.addWidget(upload_hint)
        
        layout.addWidget(upload_frame)
        
        # Selected file info
        self.file_info_label = QLabel("")
        self.file_info_label.setStyleSheet("color: #10b981; margin-top: 20px;")
        self.file_info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.file_info_label)
        
        # Dataset name input
        self.dataset_name_input = QLineEdit()
        self.dataset_name_input.setPlaceholderText("Enter dataset name (optional)")
        self.dataset_name_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
                margin-top: 20px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
        """)
        self.dataset_name_input.hide()
        layout.addWidget(self.dataset_name_input)
        
        # Upload button
        self.upload_action_btn = QPushButton("Upload & Analyze")
        self.upload_action_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:disabled {
                background-color: #94a3b8;
            }
        """)
        self.upload_action_btn.clicked.connect(self.upload_file)
        self.upload_action_btn.hide()
        layout.addWidget(self.upload_action_btn)
        
        layout.addStretch()
        
        return widget
    
    def create_data_view(self) -> QWidget:
        """Create data and charts view."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_layout = QHBoxLayout()
        
        self.data_title = QLabel("Equipment Data")
        self.data_title.setFont(QFont("Arial", 18, QFont.Bold))
        self.data_title.setStyleSheet("color: #1e293b;")
        title_layout.addWidget(self.data_title)
        
        title_layout.addStretch()
        
        # Download PDF button
        self.download_pdf_btn = QPushButton("📥 Download PDF Report")
        self.download_pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.download_pdf_btn.clicked.connect(self.download_pdf)
        title_layout.addWidget(self.download_pdf_btn)
        
        layout.addLayout(title_layout)
        
        # Summary cards
        self.summary_cards = SummaryCardsWidget()
        layout.addWidget(self.summary_cards)
        
        # Tabs for charts and table
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f1f5f9;
                padding: 10px 20px;
                margin-right: 5px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: #3b82f6;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #e2e8f0;
            }
        """)
        
        # Charts tab
        charts_widget = QWidget()
        charts_layout = QVBoxLayout(charts_widget)
        
        chart_tabs = QTabWidget()
        
        # Type distribution chart
        self.chart_type_dist = ChartWidget()
        chart_tabs.addTab(self.chart_type_dist, "Type Distribution")
        
        # Average parameters chart
        self.chart_avg_params = ChartWidget()
        chart_tabs.addTab(self.chart_avg_params, "Average Parameters")
        
        # Count by type chart
        self.chart_count = ChartWidget()
        chart_tabs.addTab(self.chart_count, "Count by Type")
        
        charts_layout.addWidget(chart_tabs)
        tabs.addTab(charts_widget, "📊 Charts")
        
        # Data table tab
        self.data_table = DataTableWidget()
        tabs.addTab(self.data_table, "📋 Data Table")
        
        layout.addWidget(tabs)
        
        return widget
    
    def create_history_view(self) -> QWidget:
        """Create history view."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Dataset History")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #1e293b; margin-bottom: 10px;")
        layout.addWidget(title)
        
        subtitle = QLabel("View and manage your recently uploaded datasets (last 5)")
        subtitle.setStyleSheet("color: #64748b; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        # History list
        self.history_list = QVBoxLayout()
        self.history_list.setSpacing(10)
        
        history_container = QWidget()
        history_container.setLayout(self.history_list)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(history_container)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        layout.addWidget(scroll)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #475569;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        refresh_btn.clicked.connect(self.load_history)
        layout.addWidget(refresh_btn)
        
        return widget
    
    def apply_styles(self):
        """Apply global styles."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8fafc;
            }
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
    
    def switch_view(self, view_name: str):
        """Switch between views."""
        if view_name == 'upload':
            self.main_content.setCurrentIndex(0)
        elif view_name == 'data':
            self.main_content.setCurrentIndex(1)
        elif view_name == 'history':
            self.load_history()
            self.main_content.setCurrentIndex(2)
    
    def select_file(self):
        """Open file dialog to select CSV file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            self.selected_file_path = file_path
            file_name = file_path.split('/')[-1]
            self.file_info_label.setText(f"Selected: {file_name}")
            self.dataset_name_input.setText(file_name.replace('.csv', ''))
            self.dataset_name_input.show()
            self.upload_action_btn.show()
    
    def upload_file(self):
        """Upload selected file to backend."""
        if not hasattr(self, 'selected_file_path'):
            QMessageBox.warning(self, "Warning", "Please select a file first")
            return
        
        name = self.dataset_name_input.text() or "Unnamed Dataset"
        
        try:
            self.statusBar().showMessage("Uploading...")
            result = self.api_client.upload_csv(self.selected_file_path, name)
            
            self.current_dataset_id = result['dataset_id']
            
            QMessageBox.information(
                self,
                "Success",
                f"File uploaded successfully!\nDataset ID: {self.current_dataset_id}"
            )
            
            # Load the dataset data
            self.load_dataset_data(self.current_dataset_id)
            
            # Enable data view button
            self.data_btn.setEnabled(True)
            
            # Switch to data view
            self.switch_view('data')
            
            # Reset upload form
            self.file_info_label.setText("")
            self.dataset_name_input.hide()
            self.upload_action_btn.hide()
            delattr(self, 'selected_file_path')
            
            self.statusBar().showMessage("Upload complete", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Upload failed: {str(e)}")
            self.statusBar().showMessage("Upload failed", 3000)
    
    def load_dataset_data(self, dataset_id: int):
        """Load dataset data and update views."""
        try:
            self.statusBar().showMessage("Loading data...")
            
            # Get summary
            summary = self.api_client.get_summary(dataset_id)
            self.summary_cards.update_values(summary)
            
            # Get chart data
            chart_data = self.api_client.get_chart_data(dataset_id)
            
            # Update charts
            self.chart_type_dist.plot_type_distribution(chart_data.get('type_distribution', {}))
            self.chart_avg_params.plot_avg_parameters(chart_data)
            self.chart_count.plot_count_by_type(chart_data)
            
            # Get data items
            data_items = self.api_client.get_data(dataset_id)
            self.data_table.set_data(data_items)
            
            self.statusBar().showMessage("Data loaded", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {str(e)}")
            self.statusBar().showMessage("Failed to load data", 3000)
    
    def load_history(self):
        """Load and display dataset history."""
        # Clear existing items
        while self.history_list.count():
            item = self.history_list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        try:
            datasets = self.api_client.get_datasets()
            
            if not datasets:
                no_data = QLabel("No datasets found. Upload a CSV file to get started.")
                no_data.setStyleSheet("color: #94a3b8; padding: 40px;")
                no_data.setAlignment(Qt.AlignCenter)
                self.history_list.addWidget(no_data)
                return
            
            for dataset in datasets:
                item_widget = self.create_history_item(dataset)
                self.history_list.addWidget(item_widget)
            
        except Exception as e:
            error_label = QLabel(f"Failed to load history: {str(e)}")
            error_label.setStyleSheet("color: #ef4444; padding: 20px;")
            self.history_list.addWidget(error_label)
    
    def create_history_item(self, dataset: Dict[str, Any]) -> QFrame:
        """Create a history item widget."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 15px;
            }
            QFrame:hover {
                border-color: #3b82f6;
                background-color: #f8fafc;
            }
        """)
        
        layout = QHBoxLayout(frame)
        layout.setSpacing(15)
        
        # Icon
        icon = QLabel("📄")
        icon.setStyleSheet("font-size: 24px;")
        layout.addWidget(icon)
        
        # Info
        info_layout = QVBoxLayout()
        
        name = QLabel(dataset['name'])
        name.setFont(QFont("Arial", 12, QFont.Bold))
        name.setStyleSheet("color: #1e293b;")
        info_layout.addWidget(name)
        
        date_str = dataset['uploaded_at'].replace('T', ' ').replace('Z', '')
        date = QLabel(f"📅 {date_str}")
        date.setStyleSheet("color: #64748b; font-size: 11px;")
        info_layout.addWidget(date)
        
        count = QLabel(f"📊 {dataset.get('item_count', 0)} items")
        count.setStyleSheet("color: #64748b; font-size: 11px;")
        info_layout.addWidget(count)
        
        layout.addLayout(info_layout, 1)
        
        # Buttons
        view_btn = QPushButton("View")
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        view_btn.clicked.connect(lambda: self.view_dataset(dataset['id']))
        layout.addWidget(view_btn)
        
        delete_btn = QPushButton("🗑️")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #fee2e2;
                color: #ef4444;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #fecaca;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_dataset(dataset['id']))
        layout.addWidget(delete_btn)
        
        return frame
    
    def view_dataset(self, dataset_id: int):
        """View a specific dataset."""
        self.current_dataset_id = dataset_id
        self.load_dataset_data(dataset_id)
        self.data_btn.setEnabled(True)
        self.switch_view('data')
    
    def delete_dataset(self, dataset_id: int):
        """Delete a dataset."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this dataset?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if self.api_client.delete_dataset(dataset_id):
                    QMessageBox.information(self, "Success", "Dataset deleted")
                    self.load_history()
                else:
                    QMessageBox.critical(self, "Error", "Failed to delete dataset")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete: {str(e)}")
    
    def download_pdf(self):
        """Download PDF report for current dataset."""
        if not self.current_dataset_id:
            QMessageBox.warning(self, "Warning", "No dataset selected")
            return
        
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF Report",
            f"equipment_report_{self.current_dataset_id}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if save_path:
            try:
                self.statusBar().showMessage("Generating PDF...")
                if self.api_client.download_pdf(self.current_dataset_id, save_path):
                    QMessageBox.information(self, "Success", f"PDF saved to:\n{save_path}")
                self.statusBar().showMessage("PDF downloaded", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to download PDF: {str(e)}")
                self.statusBar().showMessage("PDF download failed", 3000)
    
    def logout(self):
        """Logout and close application."""
        reply = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.close()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Show login dialog
    login_dialog = LoginDialog()
    
    if login_dialog.exec_() == QDialog.Accepted:
        username, password = login_dialog.get_credentials()
        
        # Create main window
        main_window = MainWindow()
        
        # Authenticate
        if main_window.api_client.login(username, password):
            main_window.show()
            sys.exit(app.exec_())
        else:
            QMessageBox.critical(
                None,
                "Authentication Failed",
                "Invalid username or password.\nPlease check that the backend server is running."
            )
            sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
