# Generated initial migration

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
from django.contrib.auth.models import User


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EquipmentDataset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('csv_file', models.FileField(upload_to='datasets/')),
                ('summary_data', models.JSONField(blank=True, default=dict)),
                ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-uploaded_at'],
            },
        ),
        migrations.CreateModel(
            name='EquipmentItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('equipment_name', models.CharField(max_length=255)),
                ('equipment_type', models.CharField(max_length=100)),
                ('flowrate', models.FloatField(blank=True, null=True)),
                ('pressure', models.FloatField(blank=True, null=True)),
                ('temperature', models.FloatField(blank=True, null=True)),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='equipment.equipmentdataset')),
            ],
        ),
    ]
