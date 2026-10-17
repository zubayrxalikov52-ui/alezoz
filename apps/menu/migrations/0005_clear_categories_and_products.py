from django.db import migrations


def clear_categories_and_products(apps, schema_editor):
    Category = apps.get_model('menu', 'Category')
    MenuItem = apps.get_model('menu', 'MenuItem')
    # Delete all menu items and categories
    MenuItem.objects.all().delete()
    Category.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0004_alter_banner_image'),
    ]

    operations = [
        migrations.RunPython(clear_categories_and_products, reverse_code=migrations.RunPython.noop),
    ]
