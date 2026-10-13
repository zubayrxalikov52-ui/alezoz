"""
Telegram Bot Webhook view — receives updates from Telegram.
Handles language selection, order confirmation codes, and multi-language communication.
"""
import json
import logging

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from apps.telegram_bot import sender


def _send_message(*args, **kwargs):
    return sender._send_message(*args, **kwargs)


def answer_callback_query(*args, **kwargs):
    return sender.answer_callback_query(*args, **kwargs)

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

        try:
            _handle_update(data)
        except Exception:
            logger.exception('Telegram webhook error')

        return JsonResponse({'ok': True})


def _language_text(language, uzbek, russian):
    return russian if language == 'ru' else uzbek


def _get_main_keyboard(language):
    """Return persistent reply keyboard for customer according to language."""
    if language == 'ru':
        return {
            'keyboard': [
                ['📋 Мой заказ / код', '🌐 Сменить язык'],
                ['ℹ️ О нас', '📞 Контакты'],
            ],
            'resize_keyboard': True,
        }
    return {
        'keyboard': [
            ['📋 Mening buyurtmam / kod', "🌐 Tilni o'zgartirish"],
            ['ℹ️ Biz haqimizda', "📞 Bog'lanish"],
        ],
        'resize_keyboard': True,
    }


def _send_language_prompt(chat_id):
    """Ask user to select language with Reply keyboard."""
    reply_markup = {
        'keyboard': [["O'zbekcha", 'Русский']],
        'resize_keyboard': True,
        'one_time_keyboard': True,
    }
    text = (
        "Tilni tanlang / Выберите язык:\n\n"
        "🇺🇿 <b>Assalomu alaykum!</b> Iltimos, muloqot tilini tanlang:\n"
        "🇷🇺 <b>Здравствуйте!</b> Пожалуйста, выберите язык обслуживания:"
    )
    _send_message(chat_id, text, reply_markup=reply_markup)


def _get_profile(chat_id, username='', first_name=''):
    from apps.telegram_bot.models import TelegramProfile

    profile, _ = TelegramProfile.objects.get_or_create(chat_id=str(chat_id))
    return profile


def _parse_language_choice(text):
    """Detect language selection from user text or callback data."""
    if not text:
        return None
    val = text.strip()
    if val in ("🇺🇿 O'zbekcha", "O'zbekcha", "O‘zbekcha", "uz", "/uz", "lang_uz"):
        return 'uz'
    if val in ('🇷🇺 Русский', 'Русский', 'ru', '/ru', 'lang_ru'):
        return 'ru'
    return None


def _handle_update(data):
    """Handle incoming Telegram messages, commands, and callback queries."""
    callback_query = data.get('callback_query')
    if callback_query:
        _handle_callback(callback_query)
        return

    message = data.get('message', {})
    if not message:
        return

    chat_id = str(message.get('chat', {}).get('id', ''))
    text = message.get('text', '').strip()
    username = message.get('from', {}).get('username', '').strip().lstrip('@')
    first_name = message.get('from', {}).get('first_name', '').strip()

    if not chat_id or not text:
        return

    profile = _get_profile(chat_id, username, first_name)

    # 1. Handle Language Selection if text is a language choice
    selected_language = _parse_language_choice(text)
    if selected_language:
        _apply_language_selection(profile, chat_id, username, selected_language)
        return

    # 2. /start command
    if text.startswith('/start'):
        parts = text.split(maxsplit=1)
        tracking_code = parts[1].strip() if len(parts) > 1 else ''

        # If user has not chosen language yet -> prompt for language first!
        if not profile.language:
            if tracking_code:
                profile.pending_tracking_code = tracking_code
                profile.save(update_fields=['pending_tracking_code'])
            _send_language_prompt(chat_id)
            return

        # User already selected language: communicate in their saved language
        lang = profile.language
        if tracking_code:
            if _send_code_by_tracking_code(chat_id, username, tracking_code, lang):
                return

        if username and _try_send_code_by_username(chat_id, username, lang):
            return

        # Welcome message in user's saved language
        welcome_text = _language_text(
            lang,
            "Assalomu alaykum! 🍽 <b>Al Ezoz</b> milliy kafesining rasmiy botiga xush kelibsiz.\n\n"
            "Buyurtmangizni tasdiqlash uchun saytdagi havola orqali kiring yoki Telegram username'ingizni ko'rsating.\n\n"
            "Pastdagi tugmalar orqali kerakli bo'limni tanlashingiz mumkin.",
            "Здравствуйте! 🍽 Добро пожаловать в официальный бот ресторана <b>Al Ezoz</b>.\n\n"
            "Для подтверждения заказа перейдите по ссылке с сайта или укажите ваш Telegram username.\n\n"
            "Вы можете воспользоваться кнопками меню ниже.",
        )
        _send_message(chat_id, welcome_text, reply_markup=_get_main_keyboard(lang))
        return

    # If user has no language selected yet and sent any other message, prompt language
    if not profile.language:
        _send_language_prompt(chat_id)
        return

    lang = profile.language

    # 3. Change language command
    if text in ("🌐 Tilni o'zgartirish", '🌐 Сменить язык', '/lang', '/language'):
        _send_language_prompt(chat_id)
        return

    # 4. My code / Order status command
    if text in ('📋 Mening buyurtmam / kod', '📋 Мой заказ / код', '/mycode'):
        if _send_last_order_info(chat_id, username, lang):
            return
        not_found_text = _language_text(
            lang,
            "Sizda faol buyurtmalar topilmadi. Saytimiz orqali mazali taomlarga buyurtma berishingiz mumkin!",
            "У вас нет активных заказов. Вы можете заказать вкусные блюда на нашем сайте!",
        )
        _send_message(chat_id, not_found_text, reply_markup=_get_main_keyboard(lang))
        return

    # 5. About us
    if text in ('ℹ️ Biz haqimizda', 'ℹ️ О нас', '/about'):
        about_text = _language_text(
            lang,
            "🏛 <b>Al Ezoz Milliy Kafesi</b>\n\n"
            "Toshkent markazidagi eng shinam muhit, betakror milliy va yevropa taomlari maskani.\n\n"
            "⏰ <b>Ish vaqti:</b> Har kuni 09:00 — 23:00\n"
            "📍 <b>Manzil:</b> Toshkent shahri, Amir Temur shoh ko'chasi, 42-uy\n"
            "🗺 <b>Xarita:</b> https://yandex.ru/maps/?pt=69.22108906908464,41.32114573809359&z=16&l=map\n"
            "📞 <b>Telefon:</b>\n"
            "  • +998 90 911 52 52\n"
            "  • +998 90 138 18 23",
            "🏛 <b>Национальное кафе Al Ezoz</b>\n\n"
            "Уютная атмосфера и изысканные блюда национальной и европейской кухни в центре Ташкента.\n\n"
            "⏰ <b>Время работы:</b> Ежедневно с 09:00 до 23:00\n"
            "📍 <b>Адрес:</b> г. Ташкент, проспект Амира Темура, д. 42\n"
            "🗺 <b>Карта:</b> https://yandex.ru/maps/?pt=69.22108906908464,41.32114573809359&z=16&l=map\n"
            "📞 <b>Телефон:</b>\n"
            "  • +998 90 911 52 52\n"
            "  • +998 90 138 18 23",
        )
        _send_message(chat_id, about_text, reply_markup=_get_main_keyboard(lang))
        return

    # 6. Contact
    if text in ("📞 Bog'lanish", '📞 Контакты', '/contact'):
        contact_text = _language_text(
            lang,
            "📞 <b>Bog'lanish uchun ma'lumotlar:</b>\n\n"
            "☎️ <b>Telefonlar:</b>\n"
            "  • +998 90 911 52 52\n"
            "  • +998 90 138 18 23\n\n"
            "📍 <b>Manzil:</b> Toshkent shahri, Amir Temur shoh ko'chasi, 42-uy\n"
            "🗺 <b>Xarita:</b> https://yandex.ru/maps/?pt=69.22108906908464,41.32114573809359&z=16&l=map\n"
            "🕒 <b>Ish vaqti:</b> 09:00 — 23:00",
            "📞 <b>Контактная информация:</b>\n\n"
            "☎️ <b>Телефоны:</b>\n"
            "  • +998 90 911 52 52\n"
            "  • +998 90 138 18 23\n\n"
            "📍 <b>Адрес:</b> г. Ташкент, проспект Амира Темура, д. 42\n"
            "🗺 <b>Карта:</b> https://yandex.ru/maps/?pt=69.22108906908464,41.32114573809359&z=16&l=map\n"
            "🕒 <b>Время работы:</b> 09:00 — 23:00",
        )
        _send_message(chat_id, contact_text, reply_markup=_get_main_keyboard(lang))
        return

    # 7. User ID
    if text == '/myid':
        _send_message(
            chat_id,
            _language_text(
                lang,
                f"Sizning Telegram Chat ID raqamingiz: <code>{chat_id}</code>\nZarur bo'lganda ushbu ID'ni administratorga taqdim etishingiz mumkin.",
                f"Ваш Telegram Chat ID: <code>{chat_id}</code>\nПри необходимости отправьте этот ID администратору.",
            ),
            reply_markup=_get_main_keyboard(lang),
        )
        return

    # 8. Try checking if message is related to an unlinked pending order by username
    if username and _try_send_code_by_username(chat_id, username, lang, only_unlinked=True):
        return

    # Default fallback message
    default_text = _language_text(
        lang,
        "Xabaringiz qabul qilindi. Buyurtmani tasdiqlash uchun saytdagi havola orqali kiring yoki pastdagi menyudan foydalaning.",
        "Ваше сообщение принято. Для подтверждения заказа воспользуйтесь ссылкой с сайта или кнопками меню ниже.",
    )
    _send_message(chat_id, default_text, reply_markup=_get_main_keyboard(lang))


def _handle_callback(callback_query):
    """Handle inline button clicks."""
    cq_id = callback_query.get('id')
    from_user = callback_query.get('from', {})
    chat_id = str(from_user.get('id', ''))
    data_str = callback_query.get('data', '')
    username = from_user.get('username', '').strip().lstrip('@')
    first_name = from_user.get('first_name', '').strip()

    answer_callback_query(cq_id)

    if not chat_id:
        return

    profile = _get_profile(chat_id, username, first_name)
    selected_language = _parse_language_choice(data_str)
    if selected_language:
        _apply_language_selection(profile, chat_id, username, selected_language)


def _apply_language_selection(profile, chat_id, username, selected_language):
    """Save selected language and send appropriate follow-up messages."""
    profile.language = selected_language
    profile.save(update_fields=['language'])

    keyboard = _get_main_keyboard(selected_language)

    confirm_msg = _language_text(
        selected_language,
        "✅ <b>Til muvaffaqiyatli tanlandi: O'zbekcha!</b>",
        "✅ <b>Язык успешно выбран: Русский!</b>",
    )
    _send_message(chat_id, confirm_msg, reply_markup=keyboard)

    # Check if there is a pending tracking code from a website order
    tracking_code = profile.pending_tracking_code
    if tracking_code:
        profile.pending_tracking_code = ''
        profile.save(update_fields=['pending_tracking_code'])
        if _send_code_by_tracking_code(chat_id, username, tracking_code, selected_language):
            return

    # Check by username
    if username and _try_send_code_by_username(chat_id, username, selected_language):
        return

    # Welcome guidance
    guide_msg = _language_text(
        selected_language,
        "🍽 <b>Al Ezoz</b> milliy kafesining rasmiy botiga xush kelibsiz!\n\n"
        "Saytdan buyurtma berganingizda ushbu bot orqali tasdiqlash kodini olasiz va holatini kuzatib borishingiz mumkin.\n\n"
        "/mycode — buyurtma tasdiqlash kodi\n"
        "/myid — sizning Telegram ID raqamingiz\n"
        "/lang — tilni o'zgartirish",
        "🍽 Добро пожаловать в официальный бот ресторана <b>Al Ezoz</b>!\n\n"
        "При оформлении заказа на сайте здесь вы получите код подтверждения и сможете следить за статусом заказа.\n\n"
        "/mycode — код подтверждения заказа\n"
        "/myid — ваш Telegram ID\n"
        "/lang — сменить язык",
    )
    _send_message(chat_id, guide_msg, reply_markup=keyboard)


def _send_code_by_tracking_code(chat_id, username, tracking_code, language):
    from apps.orders.models import Order

    order = Order.objects.filter(tracking_code=tracking_code).first()
    if not order:
        return False

    # ✅ USERNAME TEKSHIRUVI: faqat checkout'da kiritilgan username'dan kelgan so'rovga kod yuboriladi
    order_username = (order.telegram_username or '').strip().lstrip('@').lower()
    sender_username = username.strip().lstrip('@').lower() if username else ''

    if order_username and sender_username != order_username:
        # Boshqa akkauntdan kelgan — kod bermaymiz
        _send_message(
            chat_id,
            _language_text(
                language,
                f"⛔ Ushbu buyurtma <b>@{order.telegram_username}</b> akkauntiga tegishli.\n"
                "Kodni faqat shu akkauntdan olishingiz mumkin.",
                f"⛔ Этот заказ привязан к аккаунту <b>@{order.telegram_username}</b>.\n"
                "Код можно получить только с этого аккаунта.",
            ),
        )
        return True  # True — shu foydalanuvchiga xabar yuborildi, boshqa handle qilinmasin

    # Username mos keldi — chat_id bog'laymiz va kod yuboramiz
    order.telegram_chat_id = chat_id
    if sender_username and not order_username:
        order.telegram_username = username  # agar checkout'da username kiritilmagan bo'lsa, saqlab qo'yamiz
    order.save(update_fields=['telegram_chat_id', 'telegram_username'])
    _send_confirmation_code(chat_id, order, language)
    return True


def _send_confirmation_code(chat_id, order, language):
    from apps.orders.models import Order

    if order.is_code_expired:
        order.update_status(
            Order.STATUS_CANCELLED,
            note=_language_text(language, '10 daqiqada tasdiqlanmadi', 'Не подтверждён в течение 10 минут'),
        )
        _send_message(
            chat_id,
            _language_text(
                language,
                f"⚠️ <b>#{order.order_number}</b> buyurtmangizning tasdiqlash kodi muddati tugadi (10 daqiqa o'tdi).\n"
                "Iltimos, saytdan qaytadan buyurtma bering.",
                f"⚠️ Срок действия кода заказа <b>№{order.order_number}</b> истёк (прошло 10 минут).\n"
                "Пожалуйста, оформите заказ на сайте заново.",
            ),
            reply_markup=_get_main_keyboard(language),
        )
        return

    _send_message(
        chat_id,
        _language_text(
            language,
            f"✅ <b>#{order.order_number} buyurtmangizni tasdiqlash kodi:</b>\n\n"
            f"<code>{order.confirmation_code}</code>\n\n"
            f"⏱ Kod <b>10 daqiqa</b> amal qiladi.\n"
            "Ushbu kodni saytdagi tasdiqlash oynasiga kiriting.",
            f"✅ <b>Код подтверждения заказа №{order.order_number}:</b>\n\n"
            f"<code>{order.confirmation_code}</code>\n\n"
            f"⏱ Код действует <b>10 минут</b>.\n"
            "Введите его в окне подтверждения на сайте.",
        ),
        reply_markup=_get_main_keyboard(language),
    )


def _try_send_code_by_username(chat_id, username, language, only_unlinked=False):
    from apps.orders.models import Order

    orders = Order.objects.filter(
        telegram_username__iexact=username.strip().lstrip('@'),
        status=Order.STATUS_PENDING,
    ).order_by('-created_at')
    if only_unlinked:
        orders = orders.filter(telegram_chat_id='')
    order = orders.first()
    if not order:
        return False

    if not order.telegram_chat_id:
        order.telegram_chat_id = chat_id
        order.save(update_fields=['telegram_chat_id'])
    _send_confirmation_code(chat_id, order, language)
    return True


def _send_last_order_info(chat_id, username, language):
    """Find last order by chat_id or username and send details."""
    from apps.orders.models import Order

    order = Order.objects.filter(telegram_chat_id=str(chat_id)).order_by('-created_at').first()
    if not order and username:
        order = Order.objects.filter(telegram_username__iexact=username.strip().lstrip('@')).order_by('-created_at').first()

    if not order:
        return False

    if order.status == Order.STATUS_PENDING:
        _send_confirmation_code(chat_id, order, language)
        return True

    status_names = {
        'uz': {
            'confirmed': '✅ Tasdiqlangan (oshxona qabul qildi)',
            'preparing': '👨‍🍳 Tayyorlanmoqda',
            'ready': '🔔 Tayyor (topshirishga shay)',
            'delivered': '🎉 Yetkazilgan',
            'cancelled': '❌ Bekor qilingan',
        },
        'ru': {
            'confirmed': '✅ Подтверждён (принят кухней)',
            'preparing': '👨‍🍳 Готовится',
            'ready': '🔔 Готов к выдаче',
            'delivered': '🎉 Доставлен',
            'cancelled': '❌ Отменён',
        },
    }
    status_text = status_names.get(language, status_names['uz']).get(order.status, order.status)

    msg = _language_text(
        language,
        f"📦 <b>Oxirgi buyurtmangiz #{order.order_number}:</b>\n\n"
        f"• Holat: <b>{status_text}</b>\n"
        f"• Summa: <b>{int(order.total):,} so'm</b>\n"
        f"• Sana: {order.created_at.strftime('%d.%m.%Y %H:%M')}",
        f"📦 <b>Ваш последний заказ №{order.order_number}:</b>\n\n"
        f"• Статус: <b>{status_text}</b>\n"
        f"• Сумма: <b>{int(order.total):,} сум</b>\n"
        f"• Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}",
    )
    _send_message(chat_id, msg, reply_markup=_get_main_keyboard(language))
    return True
