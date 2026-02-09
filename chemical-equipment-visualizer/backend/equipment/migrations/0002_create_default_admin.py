# Data migration to create default admin user

from django.db import migrations
from django.contrib.auth.models import User


def create_admin_user(apps, schema_editor):
    """Create default admin user."""
    User = apps.get_model('auth', 'User')
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin'
        )
        print("\n✓ Default admin user created: admin / admin")


def delete_admin_user(apps, schema_editor):
    """Delete default admin user."""
    User = apps.get_model('auth', 'User')
    User.objects.filter(username='admin').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_admin_user, delete_admin_user),
    ]
