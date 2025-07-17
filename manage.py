#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import django
from django.core.management import call_command

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'internship_portal.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
    
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "internship_portal.settings")
    django.setup()
    
    from django.contrib.auth import get_user_model
    from django.db.utils import OperationalError
    # from django.core.management import call_command

    try:
        call_command('migrate')
        User = get_user_model()

        if not User.objects.filter(email="kun.darling.25@gmail.com").exists():
            User.objects.create_superuser(
                username="recruiter_verifier",
                email="kun.darling.25@gmail.com",
                password="admin@123789",
                first_name="recruiter",
                last_name="verifier",
                role="admin"
            )
            print("Superuser created.")
        else:
            print("Superuser already exists.")
    except OperationalError:
        print("⚠️ Migration or DB connection failed.")