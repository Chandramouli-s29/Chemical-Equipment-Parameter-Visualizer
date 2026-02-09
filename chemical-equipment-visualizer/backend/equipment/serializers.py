from rest_framework import serializers
from .models import EquipmentDataset, EquipmentItem


class EquipmentItemSerializer(serializers.ModelSerializer):
    """Serializer for EquipmentItem model."""
    
    class Meta:
        model = EquipmentItem
        fields = ['id', 'equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature']


class EquipmentDatasetSerializer(serializers.ModelSerializer):
    """Serializer for EquipmentDataset model."""
    items = EquipmentItemSerializer(many=True, read_only=True)
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = EquipmentDataset
        fields = ['id', 'name', 'uploaded_at', 'summary_data', 'item_count', 'items']
    
    def get_item_count(self, obj):
        return obj.items.count()


class DataSummarySerializer(serializers.Serializer):
    """Serializer for data summary statistics."""
    total_count = serializers.IntegerField()
    avg_flowrate = serializers.FloatField(allow_null=True)
    avg_pressure = serializers.FloatField(allow_null=True)
    avg_temperature = serializers.FloatField(allow_null=True)
    min_flowrate = serializers.FloatField(allow_null=True)
    max_flowrate = serializers.FloatField(allow_null=True)
    min_pressure = serializers.FloatField(allow_null=True)
    max_pressure = serializers.FloatField(allow_null=True)
    min_temperature = serializers.FloatField(allow_null=True)
    max_temperature = serializers.FloatField(allow_null=True)
    type_distribution = serializers.DictField()


class CSVUploadSerializer(serializers.Serializer):
    """Serializer for CSV file upload."""
    file = serializers.FileField()
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)
