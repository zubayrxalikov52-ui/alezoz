from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
import random


class CustomUser(AbstractUser):
    """Extended user model for both Admins and Chefs."""
    ROLE_ADMIN = 'admin'
    ROLE_CHEF = 'chef'
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Administrator'),
        (ROLE_CHEF, 'Oshpaz (Chef)'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_CHEF)
    telegram_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="Telegram Chat ID")
    full_name = models.CharField(max_length=150, blank=True, verbose_name="To'liq ismi")
    is_2fa_required = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    @property
    def is_chef(self):
        return self.role == self.ROLE_CHEF

    def get_display_name(self):
        return self.full_name or self.get_full_name() or self.username


class VerificationCode(models.Model):
    """2FA Verification Codes for Admin and Chef login."""
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='verification_codes'
    )
    code = models.CharField(max_length=6)
    attempts = models.PositiveSmallIntegerField(default=0)
    max_attempts = models.PositiveSmallIntegerField(default=3)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tasdiqlash kodi'
        verbose_name_plural = 'Tasdiqlash kodlari'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.code} ({'Ishlatilgan' if self.is_used else 'Faol'})"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired and self.attempts < self.max_attempts

    @classmethod
    def generate_for_user(cls, user, expire_seconds=180):
        """Invalidate old codes and generate a new one."""
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        code = f"{random.randint(100000, 999999)}"
        return cls.objects.create(
            user=user,
            code=code,
            expires_at=timezone.now() + timedelta(seconds=expire_seconds),
            max_attempts=3,
        )

    def verify(self, submitted_code):
        """Returns True if code matches and is valid."""
        if not self.is_valid:
            return False, "Kod muddati tugagan yoki allaqachon ishlatilgan"
        if self.code != submitted_code.strip():
            self.attempts += 1
            self.save(update_fields=['attempts'])
            remaining = self.max_attempts - self.attempts
            if remaining <= 0:
                self.is_used = True
                self.save(update_fields=['is_used'])
                return False, "Urinishlar soni tugadi. Qaytadan login qiling."
            return False, f"Kod noto'g'ri! Qolgan urinishlar: {remaining}"
        self.is_used = True
        self.save(update_fields=['is_used'])
        return True, "OK"
