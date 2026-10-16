from django.apps import AppConfig


class TelegramBotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.telegram_bot'
    verbose_name = 'Telegram Bot'
    _bot_started = False

    def ready(self):
        """Start the bot polling in a background thread when server starts."""
        import os
        import threading
        from django.core.management import call_command

        # Only run in the main process (not during migrations, manage commands, etc.)
        # When RUN_MAIN is true, it means it's the auto-reloaded worker thread.
        enable_bot = os.environ.get('ENABLE_BOT_POLLING', 'true').lower() in ('true', '1', 'yes')
        if enable_bot and os.environ.get('RUN_MAIN') == 'true' and not self.__class__._bot_started:
            self.__class__._bot_started = True

            def run_bot():
                try:
                    call_command('run_bot')
                except Exception as e:
                    print(f"Botni ishga tushirishda xatolik: {e}")

            bot_thread = threading.Thread(target=run_bot, daemon=True)
            bot_thread.start()
