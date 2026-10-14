import os
from unittest.mock import patch

from django.apps import apps
from django.test import SimpleTestCase, TestCase, override_settings

from apps.orders.models import Order
from apps.telegram_bot.models import TelegramProfile
from apps.telegram_bot.sender import notify_order_status_change
from apps.telegram_bot.views import _handle_update


class TelegramBotStartupTests(SimpleTestCase):
    def test_ready_starts_bot_only_once_per_process(self):
        app_config = apps.get_app_config('telegram_bot')

        with patch.dict(os.environ, {'RUN_MAIN': 'true'}, clear=False):
            with patch('threading.Thread') as mock_thread:
                app_config.ready()
                app_config.ready()

        self.assertEqual(mock_thread.call_count, 1)


class TelegramLanguageTests(TestCase):
    def test_start_sends_code_immediately_without_extra_prompts(self):
        order = Order.objects.create(
            order_number='TEST-1001',
            customer_name='Test Customer',
            customer_phone='+998901234567',
            confirmation_code='123456',
            telegram_username='customer',
        )

        with patch('apps.telegram_bot.sender._send_message') as send_message:
            _handle_update({
                'message': {
                    'chat': {'id': 12345},
                    'from': {'username': 'customer'},
                    'text': f'/start {order.tracking_code}',
                },
            })

            profile = TelegramProfile.objects.get(chat_id='12345')
            order.refresh_from_db()
            self.assertEqual(order.telegram_chat_id, '12345')
            self.assertTrue(any(
                '123456' in str(call.args)
                for call in send_message.call_args_list
            ))

    @override_settings(ADMIN_TELEGRAM_ID='')
    def test_status_notification_uses_saved_language(self):
        order = Order.objects.create(
            order_number='TEST-1002',
            customer_name='Test Customer',
            customer_phone='+998901234567',
            telegram_chat_id='67890',
            status=Order.STATUS_CONFIRMED,
        )
        TelegramProfile.objects.create(chat_id='67890', language='ru')

        with patch('apps.telegram_bot.sender._send_message') as send_message:
            notify_order_status_change(order, Order.STATUS_PENDING)

        self.assertIn('Ваш заказ', send_message.call_args.args[1])

    @override_settings(ADMIN_TELEGRAM_ID='')
    def test_unchanged_status_does_not_send_duplicate_notification(self):
        order = Order.objects.create(
            order_number='TEST-1003',
            customer_name='Test Customer',
            customer_phone='+998901234567',
            telegram_chat_id='67891',
            status=Order.STATUS_CONFIRMED,
        )

        with patch('apps.telegram_bot.sender._send_message') as send_message:
            result = notify_order_status_change(order, Order.STATUS_CONFIRMED)

        self.assertFalse(result)
        send_message.assert_not_called()

    def test_first_start_without_order_prompts_language_and_then_speaks_uzbek(self):
        with patch('apps.telegram_bot.sender._send_message') as send_message:
            # 1. First /start -> must prompt for language
            _handle_update({
                'message': {
                    'chat': {'id': 99001},
                    'from': {'username': 'newuser'},
                    'text': '/start',
                },
            })
            profile = TelegramProfile.objects.get(chat_id='99001')
            self.assertEqual(profile.language, '')
            self.assertIn('Tilni tanlang', send_message.call_args.args[1])

            # 2. User chooses Uzbek
            _handle_update({
                'message': {
                    'chat': {'id': 99001},
                    'from': {'username': 'newuser'},
                    'text': "O'zbekcha",
                },
            })
            profile.refresh_from_db()
            self.assertEqual(profile.language, 'uz')
            self.assertTrue(any("O'zbekcha" in call.args[1] for call in send_message.call_args_list))

            # 3. Second /start -> must NOT ask for language again, must speak in Uzbek
            send_message.reset_mock()
            _handle_update({
                'message': {
                    'chat': {'id': 99001},
                    'from': {'username': 'newuser'},
                    'text': '/start',
                },
            })
            # Does not ask for language
            self.assertFalse(any('Tilni tanlang' in call.args[1] for call in send_message.call_args_list))
            # Speaks in Uzbek
            self.assertTrue(any('Assalomu alaykum' in call.args[1] for call in send_message.call_args_list))

    def test_first_start_without_order_prompts_language_and_then_speaks_russian(self):
        with patch('apps.telegram_bot.sender._send_message') as send_message:
            # 1. First /start -> prompt language
            _handle_update({
                'message': {
                    'chat': {'id': 99002},
                    'from': {'username': 'ruuser'},
                    'text': '/start',
                },
            })
            profile = TelegramProfile.objects.get(chat_id='99002')
            self.assertEqual(profile.language, '')

            # 2. User chooses Russian
            _handle_update({
                'message': {
                    'chat': {'id': 99002},
                    'from': {'username': 'ruuser'},
                    'text': 'Русский',
                },
            })
            profile.refresh_from_db()
            self.assertEqual(profile.language, 'ru')

            # 3. Second /start -> directly Russian
            send_message.reset_mock()
            _handle_update({
                'message': {
                    'chat': {'id': 99002},
                    'from': {'username': 'ruuser'},
                    'text': '/start',
                },
            })
            self.assertFalse(any('Tilni tanlang' in call.args[1] for call in send_message.call_args_list))
            self.assertTrue(any('Здравствуйте' in call.args[1] for call in send_message.call_args_list))

    def test_existing_profile_with_tracking_code_directly_sends_code_without_language_prompt(self):
        TelegramProfile.objects.create(chat_id='99003', language='uz')
        order = Order.objects.create(
            order_number='TEST-9903',
            customer_name='Anvar',
            customer_phone='+998901112233',
            confirmation_code='654321',
        )

        with patch('apps.telegram_bot.sender._send_message') as send_message:
            _handle_update({
                'message': {
                    'chat': {'id': 99003},
                    'text': f'/start {order.tracking_code}',
                },
            })
            # Should directly send confirmation code in Uzbek without asking language
            self.assertFalse(any('Tilni tanlang' in call.args[1] for call in send_message.call_args_list))
            self.assertTrue(any('654321' in call.args[1] for call in send_message.call_args_list))
            self.assertTrue(any('tasdiqlash kodi' in call.args[1] for call in send_message.call_args_list))

    def test_auto_send_confirmation_code_on_order_without_start(self):
        from apps.telegram_bot.sender import try_send_confirmation_code_on_order

        # Foydalanuvchi avval botga /start bosgan (TelegramProfile da username va chat_id bor)
        TelegramProfile.objects.create(chat_id='888777', username='testuser123', language='uz')

        order = Order.objects.create(
            order_number='TEST-8888',
            customer_name='Farrux',
            customer_phone='+998901234567',
            confirmation_code='778899',
            telegram_username='@testuser123',
        )

        with patch('apps.telegram_bot.sender._send_message') as send_message:
            send_message.return_value = True
            sent = try_send_confirmation_code_on_order(order)
            self.assertTrue(sent)
            order.refresh_from_db()
            self.assertEqual(order.telegram_chat_id, '888777')
            self.assertTrue(any('778899' in str(call.args) for call in send_message.call_args_list))
