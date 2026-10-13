from django.db import models


class TelegramProfile(models.Model):
    LANGUAGE_UZBEK = 'uz'
    LANGUAGE_RUSSIAN = 'ru'
    LANGUAGE_CHOICES = [
        (LANGUAGE_UZBEK, "O'zbekcha"),
        (LANGUAGE_RUSSIAN, 'Русский'),
    ]

    chat_id = models.CharField(max_length=50, unique=True)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, blank=True)
    pending_tracking_code = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return self.chat_id
