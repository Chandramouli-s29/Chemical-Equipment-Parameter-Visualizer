from django.db import models
from django.contrib.auth.models import User
import json


class EquipmentDataset(models.Model):
    """Model to store uploaded equipment datasets (last 5)."""
    name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    csv_file = models.FileField(upload_to='datasets/')
    summary_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.name} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
    
    def save(self, *args, **kwargs):
        # Keep only last 5 datasets for this user
        super().save(*args, **kwargs)
        if self.uploaded_by:
            datasets = EquipmentDataset.objects.filter(uploaded_by=self.uploaded_by)
        else:
            datasets = EquipmentDataset.objects.all()
        
        if datasets.count() > 5:
            # Delete oldest datasets
            for old_dataset in datasets[5:]:
                old_dataset.delete()


class EquipmentItem(models.Model):
    """Model to store individual equipment items."""
    dataset = models.ForeignKey(EquipmentDataset, on_delete=models.CASCADE, related_name='items')
    equipment_name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=100)
    flowrate = models.FloatField(null=True, blank=True)
    pressure = models.FloatField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.equipment_name} ({self.equipment_type})"
