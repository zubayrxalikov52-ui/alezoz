"""Management command: python manage.py run_bot — starts Telegram polling."""
import sys
import time
import logging
import requests
from django.core.management.base import BaseCommand
from django.conf import settings

# Force safe encoding on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Telegram botni polling rejimda ishga tushirish'

    def handle(self, *args, **options):
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        if not token:
            self.stderr.write("[XATO] TELEGRAM_BOT_TOKEN sozlanmagan!")
            return

        self.stdout.write(self.style.SUCCESS("[BOT] Telegram bot polling rejimida ishga tushdi..."))
        offset = None

        while True:
            try:
                url = f"https://api.telegram.org/bot{token}/getUpdates"
                params = {'timeout': 20, 'offset': offset}
                resp = requests.get(url, params=params, timeout=25)

                if resp.status_code == 409:
                    logger.warning("Telegram polling conflict: another instance running. Retrying in 5s...")
                    time.sleep(5)
                    continue

                resp.raise_for_status()
                data = resp.json()

                if not data.get('ok'):
                    logger.error(f"Telegram API error: {data}")
                    time.sleep(3)
                    continue

                updates = data.get('result', [])
                for update in updates:
                    offset = update['update_id'] + 1
                    try:
                        from apps.telegram_bot.views import _handle_update
                        _handle_update(update)
                    except Exception as e:
                        logger.exception(f"Update handling error: {e}")

            except requests.RequestException as e:
                logger.error(f"Polling network error: {e}")
                time.sleep(3)
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING("\n[BOT] Bot to'xtatildi."))
                break
            except Exception as e:
                logger.exception(f"Unexpected polling loop error: {e}")
                time.sleep(3)
