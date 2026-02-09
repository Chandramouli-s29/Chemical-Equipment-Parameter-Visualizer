from django.contrib import admin
from .models import EquipmentDataset, EquipmentItem


class EquipmentItemInline(admin.TabularInline):
    model = EquipmentItem
    extra = 0
    readonly_fields = ['equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature']


@admin.register(EquipmentDataset)
class EquipmentDatasetAdmin(admin.ModelAdmin):
    list_display = ['name', 'uploaded_at', 'uploaded_by', 'item_count']
    list_filter = ['uploaded_at', 'uploaded_by']
    search_fields = ['name']
    readonly_fields = ['uploaded_at', 'summary_data']
    inlines = [EquipmentItemInline]
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'


@admin.register(EquipmentItem)
class EquipmentItemAdmin(admin.ModelAdmin):
    list_display = ['equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature', 'dataset']
    list_filter = ['equipment_type', 'dataset']
    search_fields = ['equipment_name', 'equipment_type']
