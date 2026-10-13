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

        # 3. Categories & Products from restaurant.db or default
        categories_data = [
            ('all', 'Barchasi', '▦', 0),
            ('food', 'Taomlar', '🍽', 1),
            ('salad', 'Salatlar', '🥗', 2),
            ('snack', 'Snacklar', '🍟', 3),
            ('drink', 'Ichimliklar', '🥤', 4),
            ('dessert', 'Desertlar', '🍰', 5),
        ]

        cat_map = {}
        for slug, name, icon, order in categories_data:
            cat, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'icon': icon, 'sort_order': order, 'is_active': True}
            )
            cat_map[slug] = cat

        # Load from restaurant.db if present
        rest_db = 'restaurant.db'
        if os.path.exists(rest_db):
            conn = sqlite3.connect(rest_db)
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM products").fetchall()
            conn.close()

            added = 0
            for r in rows:
                c_slug = r['category_slug']
                cat = cat_map.get(c_slug, cat_map.get('food'))
                item, itm_created = MenuItem.objects.get_or_create(
                    name=r['name'],
                    category=cat,
                    defaults={
                        'description': r['description'] or '',
                        'price': r['price'],
                        'image_url': r['image'] or '',
                        'is_available': bool(r['is_available']),
                        'is_popular': bool(r['is_featured']),
                    }
                )
                if itm_created:
                    added += 1
            self.stdout.write(self.style.SUCCESS(f"Imported {added} menu items from {rest_db}. Total items: {MenuItem.objects.count()}"))
        else:
            if MenuItem.objects.count() == 0:
                fixture_path = os.path.join(settings.BASE_DIR, 'apps', 'menu', 'fixtures', 'menu_items.json')
                if os.path.exists(fixture_path):
                    from django.core.management import call_command
                    call_command('loaddata', fixture_path)
                    self.stdout.write(self.style.SUCCESS(f"Loaded {MenuItem.objects.count()} items from fixture!"))
                else:
                    self.stdout.write(self.style.WARNING("No fixtures or restaurant.db found."))
            else:
                self.stdout.write(self.style.SUCCESS(f"MenuItems already exist ({MenuItem.objects.count()} items)."))

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
