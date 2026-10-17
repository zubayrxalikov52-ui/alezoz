from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategoriya nomi")
    name_uz = models.CharField(max_length=100, blank=True, verbose_name="O'zbekcha nomi")
    name_ru = models.CharField(max_length=100, blank=True, verbose_name="Ruscha nomi")
    icon = models.CharField(max_length=10, default='🍽️', verbose_name="Emoji")
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class MenuItem(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='items', verbose_name="Kategoriya"
    )
    name = models.CharField(max_length=200, verbose_name="Taom nomi")
    name_uz = models.CharField(max_length=200, blank=True)
    name_ru = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True, verbose_name="Tavsif")
    description_uz = models.TextField(blank=True)
    description_ru = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Narxi (so'm)")
    image = models.ImageField(upload_to='menu/', blank=True, null=True, verbose_name="Rasm")
    image_url = models.URLField(blank=True, verbose_name="Rasm URL (ixtiyoriy)")

    is_available = models.BooleanField(default=True, verbose_name="Mavjud")
    is_popular = models.BooleanField(default=False, verbose_name="Mashhur")
    is_new = models.BooleanField(default=False, verbose_name="Yangi")
    is_spicy = models.BooleanField(default=False, verbose_name="Achchiq")
    is_vegetarian = models.BooleanField(default=False, verbose_name="Vegetarian")

    calories = models.PositiveIntegerField(blank=True, null=True, verbose_name="Kaloriya")
    prep_time_minutes = models.PositiveSmallIntegerField(default=15, verbose_name="Tayyorlash vaqti (daqiqa)")
    weight_grams = models.PositiveIntegerField(blank=True, null=True, verbose_name="Vazni (gramm)")

    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Menyu elementi'
        verbose_name_plural = 'Menyu elementlari'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return f"{self.name} — {self.price:,} so'm"

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        return self.image_url or '/static/about-dish.png'

    def to_dict(self):
        return {
            'id': self.pk,
            'name': self.name,
            'description': self.description,
            'price': int(self.price),
            'image': self.display_image,
            'category': self.category.name,
            'category_id': self.category_id,
            'is_available': self.is_available,
            'is_popular': self.is_popular,
            'is_new': self.is_new,
            'is_spicy': self.is_spicy,
            'is_vegetarian': self.is_vegetarian,
            'calories': self.calories,
            'prep_time_minutes': self.prep_time_minutes,
            'weight_grams': self.weight_grams,
        }


class Banner(models.Model):
    """Admin tomonidan qo'shiladigan banner rasmlari — menyu tepasida ko'rinadi."""
    title = models.CharField(max_length=200, blank=True, verbose_name="Nomi (ixtiyoriy)")
    image = models.ImageField(upload_to='banners/', blank=True, null=True, verbose_name="Banner rasmi")
    image_url = models.URLField(blank=True, verbose_name="Rasm URL (ixtiyoriy)")
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Banner'
        verbose_name_plural = 'Bannerlar'
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.title or f"Banner #{self.pk}"

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        return self.image_url or ''

    def to_dict(self):
        return {
            'id': self.pk,
            'title': self.title,
            'image': self.display_image,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
        }


class ContactMessage(models.Model):
    name = models.CharField(max_length=150, verbose_name="Ismi")
    phone = models.CharField(max_length=50, verbose_name="Telefon")
    subject = models.CharField(max_length=200, blank=True, default="Umumiy", verbose_name="Mavzu")
    message = models.TextField(verbose_name="Xabar")
    is_read = models.BooleanField(default=False, verbose_name="O'qilgan")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yuborilgan vaqt")

    class Meta:
        verbose_name = 'Aloqa xabari'
        verbose_name_plural = 'Aloqa xabarlari'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.phone}): {self.subject}"

    def to_dict(self):
        return {
            'id': self.pk,
            'name': self.name,
            'phone': self.phone,
            'subject': self.subject,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
        }

