from django.db import migrations


def clear_categories_and_products(apps, schema_editor):
    # ZARARSIZLANTIRILDI: Taomlar va kategoriyalar o'chirilMAYDI
    # Eski kod barcha mahsulotlarni o'chirib yuborardi
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0004_alter_banner_image'),
    ]

    operations = [
        migrations.RunPython(clear_categories_and_products, reverse_code=migrations.RunPython.noop),
    ]
