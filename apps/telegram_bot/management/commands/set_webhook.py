"""Management command: python manage.py set_webhook --url <WEBHOOK_URL>"""
import requests
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Telegram bot Webhook manzilini o‘rnatish yoki o‘chirish'

    def add_arguments(self, parser):
        parser.add_argument('--url', type=str, help='Webhook URL manzili (masalan: https://my-cafe.up.railway.app/api/telegram/webhook/)')
        parser.add_argument('--delete', action='store_true', help='Webhookni o‘chirish (pollingga o‘tish uchun)')
        parser.add_argument('--info', action='store_true', help='Hozirgi webhook holatini ko‘rish')

    def handle(self, *args, **options):
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        if not token:
            self.stderr.write("❌ TELEGRAM_BOT_TOKEN sozlanmagan!")
            return

        if options.get('delete'):
            url = f"https://api.telegram.org/bot{token}/deleteWebhook"
            resp = requests.post(url).json()
            if resp.get('ok'):
                self.stdout.write(self.style.SUCCESS("✅ Webhook muvaffaqiyatli o'chirildi! Endi polling (run_bot) ishlatishingiz mumkin."))
            else:
                self.stderr.write(f"❌ Xatolik: {resp}")
            return

        if options.get('info'):
            url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
            resp = requests.get(url).json()
            self.stdout.write(f"Webhook ma'lumotlari: {resp}")
            return

        webhook_url = options.get('url')
        if not webhook_url:
            self.stderr.write("❌ --url ko'rsatilishi shart! Masalan: python manage.py set_webhook --url https://example.com/api/telegram/webhook/")
            return

        url = f"https://api.telegram.org/bot{token}/setWebhook"
        resp = requests.post(url, json={'url': webhook_url}).json()
        if resp.get('ok'):
            self.stdout.write(self.style.SUCCESS(f"✅ Webhook muvaffaqiyatli o'rnatildi: {webhook_url}"))
        else:
            self.stderr.write(f"❌ Xatolik yuz berdi: {resp}")
