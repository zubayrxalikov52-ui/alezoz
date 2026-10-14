import uuid
from django.db import models
from apps.menu.models import MenuItem


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_PREPARING = 'preparing'
    STATUS_READY = 'ready'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Kutilmoqda'),
        (STATUS_CONFIRMED, 'Tasdiqlandi'),
        (STATUS_PREPARING, 'Tayyorlanmoqda'),
        (STATUS_READY, 'Tayyor'),
        (STATUS_DELIVERED, 'Yetkazildi'),
        (STATUS_CANCELLED, 'Bekor qilindi'),
    ]

    STATUS_ICONS = {
        STATUS_PENDING: '⏳',
        STATUS_CONFIRMED: '✅',
        STATUS_PREPARING: '👨‍🍳',
        STATUS_READY: '🔔',
        STATUS_DELIVERED: '🎉',
        STATUS_CANCELLED: '❌',
    }

    ORDER_TYPE_DINE_IN = 'dine_in'
    ORDER_TYPE_TAKEAWAY = 'takeaway'
    ORDER_TYPE_DELIVERY = 'delivery'

    ORDER_TYPE_CHOICES = [
        (ORDER_TYPE_DINE_IN, 'Restoranda yeyish'),
        (ORDER_TYPE_TAKEAWAY, 'Olib ketish'),
        (ORDER_TYPE_DELIVERY, 'Yetkazib berish'),
    ]

    PAYMENT_CASH = 'cash'
    PAYMENT_CARD = 'card'
    PAYMENT_CLICK = 'click'
    PAYMENT_PAYME = 'payme'

    PAYMENT_CHOICES = [
        (PAYMENT_CASH, 'Naqd pul'),
        (PAYMENT_CARD, 'Karta'),
        (PAYMENT_CLICK, 'Click'),
        (PAYMENT_PAYME, "Payme"),
    ]

    order_number = models.CharField(max_length=20, unique=True, editable=False)
    tracking_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    # Customer info
    customer_name = models.CharField(max_length=150, verbose_name="Mijoz ismi")
    customer_phone = models.CharField(max_length=20, verbose_name="Telefon raqami")
    customer_notes = models.TextField(blank=True, verbose_name="Izoh")

    confirmation_code = models.CharField(max_length=6, blank=True)
    telegram_chat_id = models.CharField(max_length=50, blank=True)
    telegram_username = models.CharField(max_length=100, blank=True, verbose_name="Telegram username")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Order type
    order_type = models.CharField(
        max_length=20, choices=ORDER_TYPE_CHOICES,
        default=ORDER_TYPE_DINE_IN, verbose_name="Buyurtma turi"
    )
    table_number = models.CharField(max_length=10, blank=True, verbose_name="Stol raqami")
    delivery_address = models.TextField(blank=True, verbose_name="Yetkazish manzili")

    # Payment
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_CHOICES,
        default=PAYMENT_CASH, verbose_name="To'lov usuli"
    )
    is_paid = models.BooleanField(default=False, verbose_name="To'langan")

    # Status
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default=STATUS_PENDING, verbose_name="Holat"
    )
    status_history = models.JSONField(default=list, blank=True)

    # Pricing
    subtotal = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=0, default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    # Chef assignment
    assigned_chef = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_orders',
        limit_choices_to={'role': 'chef'}, verbose_name="Tayinlangan oshpaz"
    )

    class Meta:
        verbose_name = 'Buyurtma'
        verbose_name_plural = 'Buyurtmalar'
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.order_number} — {self.customer_name} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self.order_number:
            import random
            self.order_number = f"ORD{random.randint(10000, 99999)}"
        super().save(*args, **kwargs)

    @property
    def status_icon(self):
        return self.STATUS_ICONS.get(self.status, '❓')

    @property
    def is_code_expired(self):
        """Returns True if order confirmation code is older than 10 minutes (600s)."""
        from django.utils import timezone
        from datetime import timedelta
        if not self.created_at:
            return False
        return timezone.now() > self.created_at + timedelta(minutes=10)

    def update_status(self, new_status, note=''):
        from django.utils import timezone
        old_status = self.status
        self.status = new_status
        history = self.status_history or []
        history.append({
            'from': old_status,
            'to': new_status,
            'note': note,
            'at': timezone.now().isoformat(),
        })
        self.status_history = history
        if new_status == self.STATUS_CONFIRMED:
            self.confirmed_at = timezone.now()
        elif new_status == self.STATUS_DELIVERED:
            self.delivered_at = timezone.now()
        self.save(update_fields=['status', 'status_history', 'confirmed_at', 'delivered_at', 'updated_at'])

    @property
    def chef_status(self):
        return {
            self.STATUS_PENDING: 'New',
            self.STATUS_CONFIRMED: 'Accepted',
            self.STATUS_PREPARING: 'Preparing',
            self.STATUS_READY: 'Ready',
            self.STATUS_DELIVERED: 'Delivered',
            self.STATUS_CANCELLED: 'Cancelled',
        }.get(self.status, self.status)

    def to_dict(self):
        from django.conf import settings
        bot_username = getattr(settings, 'TELEGRAM_BOT_USERNAME', 'alezozmilliycafebot')
        return {
            'id': self.pk,
            'order_number': self.order_number,
            'tracking_code': str(self.tracking_code),
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'customer_notes': self.customer_notes,
            'comment': self.customer_notes,
            'order_type': self.order_type,
            'order_type_display': self.get_order_type_display(),
            'table_number': self.table_number,
            'delivery_address': self.delivery_address,
            'payment_method': self.payment_method,
            'payment_method_display': self.get_payment_method_display(),
            'is_paid': self.is_paid,
            'status': self.status,
            'chef_status': self.chef_status,
            'status_display': self.get_status_display(),
            'status_icon': self.status_icon,
            'subtotal': int(self.subtotal),
            'delivery_fee': int(self.delivery_fee),
            'total': int(self.total),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'latitude': str(self.latitude) if self.latitude else None,
            'longitude': str(self.longitude) if self.longitude else None,
            'telegram_username': self.telegram_username,
            'telegram_chat_id': self.telegram_chat_id,
            'has_telegram_chat': bool(self.telegram_chat_id),
            'bot_username': bot_username,
            'bot_start_url': f"https://t.me/{bot_username}?start={self.tracking_code}",
            'items': [item.to_dict() for item in self.items.select_related('menu_item').all()],
        }


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(
        MenuItem, on_delete=models.SET_NULL, null=True, related_name='order_items'
    )
    name = models.CharField(max_length=200)  # Snapshot name
    price = models.DecimalField(max_digits=10, decimal_places=0)  # Snapshot price
    quantity = models.PositiveSmallIntegerField(default=1)
    total = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'Buyurtma elementi'
        verbose_name_plural = 'Buyurtma elementlari'

    def __str__(self):
        return f"{self.name} x{self.quantity}"

    def save(self, *args, **kwargs):
        self.total = self.price * self.quantity
        super().save(*args, **kwargs)

    def to_dict(self):
        return {
            'id': self.pk,
            'menu_item_id': self.menu_item_id,
            'name': self.name,
            'product_name': self.name,
            'price': int(self.price),
            'quantity': self.quantity,
            'total': int(self.total),
            'notes': self.notes,
        }
