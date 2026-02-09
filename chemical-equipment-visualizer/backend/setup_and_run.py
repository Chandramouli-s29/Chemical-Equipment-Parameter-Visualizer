#!/usr/bin/env python3
"""
Setup and run script for the Django backend.
This script will:
1. Run migrations
2. Create the default admin user (admin / admin)
3. Start the development server
"""

import os
import sys
import subprocess


def run_command(command, description):
    """Run a shell command and print the result."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"❌ Failed: {description}")
        sys.exit(1)
    print(f"✅ Success: {description}")
    return result


def main():
    """Main setup and run function."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║     Chemical Equipment Visualizer - Backend Setup           ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Check if we're in the backend directory
    if not os.path.exists('manage.py'):
        print("❌ Error: Please run this script from the backend directory")
        print("   cd backend")
        sys.exit(1)
    
    # Run migrations
    run_command('python manage.py migrate', 'Running database migrations...')
    
    # Check if admin user exists, if not create it
    print(f"\n{'='*60}")
    print("Checking/Creating admin user...")
    print(f"{'='*60}")
    
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chemical_equipment_visualizer.settings')
    django.setup()
    
    from django.contrib.auth.models import User
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        print("✅ Created admin user: admin / admin")
    else:
        print("✅ Admin user already exists: admin / admin")
    
    print(f"\n{'='*60}")
    print("Starting Django development server...")
    print(f"{'='*60}")
    print("\n🌐 API will be available at: http://localhost:8000/api/")
    print("📊 Admin panel: http://localhost:8000/admin/")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Start the server
    subprocess.run('python manage.py runserver', shell=True)


if __name__ == '__main__':
    main()
