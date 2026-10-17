from django.core.management.base import BaseCommand
from apps.accounts.models import CustomUser
from apps.menu.models import Category, MenuItem
import sqlite3
import os


class Command(BaseCommand):
    help = 'Seed default categories, dishes, and staff accounts into Django database'

    def handle(self, *args, **options):
        from django.conf import settings

        # 1. Admin User
        admin_tg = getattr(settings, 'ADMIN_TELEGRAM_ID', '') or '7319624771'
        admin_user, created = CustomUser.objects.get_or_create(
            username='Alezozadmin',
            defaults={
                'full_name': 'Bosh Administrator',
                'role': CustomUser.ROLE_ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'telegram_id': admin_tg,
                'is_2fa_required': True,
            }
        )
        if created or not admin_user.check_password('Alezoztashkent'):
            admin_user.set_password('Alezoztashkent')
            admin_user.role = CustomUser.ROLE_ADMIN
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.telegram_id = admin_tg
            admin_user.save()
        else:
            admin_user.telegram_id = admin_tg
            admin_user.save()
        self.stdout.write(self.style.SUCCESS(f"Admin user ready: {admin_user.username} (TG: {admin_tg})"))

        # 2. Chef User
        chef_tg = getattr(settings, 'CHEF_TELEGRAM_ID', '') or getattr(settings, 'CHEF_TELEGRAM_IDS', '') or '7319624771'
        chef_user, created = CustomUser.objects.get_or_create(
            username='Alezozchef',
            defaults={
                'full_name': 'Bosh Oshpaz',
                'role': CustomUser.ROLE_CHEF,
                'is_staff': False,
                'is_superuser': False,
                'telegram_id': chef_tg,
                'is_2fa_required': True,
            }
        )
        if created or not chef_user.check_password('Alezoztashkent'):
            chef_user.set_password('Alezoztashkent')
            chef_user.role = CustomUser.ROLE_CHEF
            chef_user.telegram_id = chef_tg
            chef_user.save()
        else:
            chef_user.telegram_id = chef_tg
            chef_user.save()
        self.stdout.write(self.style.SUCCESS(f"Chef user ready: {chef_user.username} (TG: {chef_tg})"))

        # 3. Default Banner
        from apps.menu.models import Banner
        if Banner.objects.count() == 0:
            Banner.objects.create(
                title="Maxsus Kombo & Aksiya",
                image_url="https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=1200&q=80",
                sort_order=0,
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS("Default banner created!"))

        self.stdout.write(self.style.SUCCESS("Staff verification completed successfully!"))

