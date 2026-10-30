import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.accounts.models import CustomUser
from apps.menu.models import Category, MenuItem, Banner


class Command(BaseCommand):
    help = 'Seed default categories, dishes, and staff accounts into Django database'

    def handle(self, *args, **options):
        # 1. Admin User
        admin_tg = getattr(settings, 'ADMIN_TELEGRAM_ID', '') or '7987528056'
        admin_user = CustomUser.objects.filter(username='Alezozadmin').first()
        if not admin_user:
            admin_user = CustomUser.objects.create(
                username='Alezozadmin',
                full_name='Bosh Administrator',
                role=CustomUser.ROLE_ADMIN,
                is_staff=True,
                is_superuser=True,
                telegram_id=admin_tg,
                is_2fa_required=True,
            )
            admin_user.set_password('Alezoztashkent')
            admin_user.save()
        else:
            admin_user.set_password('Alezoztashkent')
            admin_user.role = CustomUser.ROLE_ADMIN
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.telegram_id = admin_tg
            admin_user.save()
        self.stdout.write(self.style.SUCCESS(f"Admin user ready: {admin_user.username} (TG: {admin_tg})"))

        # 2. Chef User
        chef_tg = getattr(settings, 'CHEF_TELEGRAM_ID', '') or getattr(settings, 'CHEF_TELEGRAM_IDS', '') or '7319624771'
        chef_user = CustomUser.objects.filter(username='Alezozchef').first()
        if not chef_user:
            chef_user = CustomUser.objects.create(
                username='Alezozchef',
                full_name='Bosh Oshpaz',
                role=CustomUser.ROLE_CHEF,
                is_staff=False,
                is_superuser=False,
                telegram_id=chef_tg,
                is_2fa_required=True,
            )
            chef_user.set_password('Alezoztashkent')
            chef_user.save()
        else:
            chef_user.set_password('Alezoztashkent')
            chef_user.role = CustomUser.ROLE_CHEF
            chef_user.telegram_id = chef_tg
            chef_user.save()
        self.stdout.write(self.style.SUCCESS(f"Chef user ready: {chef_user.username} (TG: {chef_tg})"))

        # 3. Default Banner
        if Banner.objects.count() == 0:
            Banner.objects.create(
                title="Maxsus Kombo & Aksiya",
                image_url="https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=1200&q=80",
                sort_order=0,
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS("Default banner created!"))

        # 4. Load Categories and MenuItems from seed_menu.json
        json_file = os.path.join(os.path.dirname(__file__), 'seed_menu.json')
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Categories
                cat_map = {}
                for cat_data in data.get('categories', []):
                    cat_obj = Category.objects.filter(slug=cat_data['slug']).first()
                    if not cat_obj:
                        cat_obj = Category.objects.create(
                            slug=cat_data['slug'],
                            name=cat_data['name'],
                            name_uz=cat_data.get('name_uz') or cat_data['name'],
                            name_ru=cat_data.get('name_ru') or '',
                            icon=cat_data.get('icon') or '🍽️',
                            sort_order=cat_data.get('sort_order', 0),
                            is_active=cat_data.get('is_active', True),
                        )
                    cat_map[cat_data['slug']] = cat_obj

                # MenuItems
                items_created = 0
                for item_data in data.get('items', []):
                    cat = cat_map.get(item_data['category_slug']) or Category.objects.filter(slug=item_data['category_slug']).first()
                    if not cat:
                        cat = Category.objects.first()

                    existing = MenuItem.objects.filter(name=item_data['name'], category=cat).first()
                    if not existing:
                        MenuItem.objects.create(
                            name=item_data['name'],
                            category=cat,
                            name_uz=item_data.get('name_uz') or item_data['name'],
                            name_ru=item_data.get('name_ru') or '',
                            description=item_data.get('description') or '',
                            price=item_data['price'],
                            is_promo=item_data.get('is_promo', False),
                            promo_price=item_data.get('promo_price'),
                            image=item_data.get('image') or '',
                            image_url=item_data.get('image_url') or '',
                            is_available=item_data.get('is_available', True),
                            is_popular=item_data.get('is_popular', False),
                            sort_order=item_data.get('sort_order', 0),
                        )
                        items_created += 1

                self.stdout.write(self.style.SUCCESS(f"Categories ready: {len(cat_map)}, New MenuItems created: {items_created}, Total items in DB: {MenuItem.objects.count()}"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Seeding error: {e}"))

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
