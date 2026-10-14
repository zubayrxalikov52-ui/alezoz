"""
Telegram Sender — All outgoing messages to Telegram.
"""
import logging
import json
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def _is_dev_mode():
    """Return True if no Telegram bot token is configured."""
    return not bool(getattr(settings, 'TELEGRAM_BOT_TOKEN', ''))


def _get_bot_token():
    return getattr(settings, 'TELEGRAM_BOT_TOKEN', '')


def _customer_language(chat_id):
    if not chat_id:
        return 'uz'
    try:
        from apps.telegram_bot.models import TelegramProfile
        return TelegramProfile.objects.filter(chat_id=str(chat_id)).values_list(
            'language', flat=True
        ).first() or 'uz'
    except Exception:
        return 'uz'


def _send_message(chat_id, text, parse_mode='HTML', reply_markup=None):
    """Low-level Telegram sendMessage."""
    if getattr(settings, 'DISABLE_TELEGRAM_NOTIFICATIONS', False):
        return True

    token = _get_bot_token()
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN not configured")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': str(chat_id),
        'text': text,
        'parse_mode': parse_mode,
    }
    if reply_markup:
        if isinstance(reply_markup, dict):
            payload['reply_markup'] = json.dumps(reply_markup)
        else:
            payload['reply_markup'] = reply_markup

    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        return True
    except requests.RequestException as e:
        logger.error(f"Telegram send error to {chat_id}: {e}")
        return False


def answer_callback_query(callback_query_id, text=None):
    """Answer an incoming callback query."""
    token = _get_bot_token()
    if not token or not callback_query_id:
        return False
    url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
    payload = {'callback_query_id': callback_query_id}
    if text:
        payload['text'] = text
    try:
        requests.post(url, json=payload, timeout=5)
        return True
    except Exception as e:
        logger.warning(f"Failed to answer callback query: {e}")
        return False


def send_verification_code_to_user(user, code):
    """Send 2FA code to admin/chef's Telegram.
    In dev mode (no bot token), print code to console and return True.
    """
    if _is_dev_mode():
        print(f"\n{'='*50}")
        print(f"🔐 DEV MODE — 2FA CODE for '{user.username}': {code}")
        print(f"{'='*50}\n")
        logger.warning(f"DEV MODE: 2FA code for {user.username} is {code}")
        return True

    tg_id = user.telegram_id
    if not tg_id:
        if getattr(user, 'is_admin', False) or getattr(user, 'role', '') == 'admin':
            tg_id = getattr(settings, 'ADMIN_TELEGRAM_ID', '')
        elif getattr(user, 'is_chef', False) or getattr(user, 'role', '') == 'chef':
            tg_id = getattr(settings, 'CHEF_TELEGRAM_ID', '') or getattr(settings, 'CHEF_TELEGRAM_IDS', '')

    if not tg_id:
        logger.error(f"User {user.username} has no telegram_id and no fallback in settings")
        return False

    text = (
        f"🔐 <b>Al Ezoz — Tizimga kirish kodi</b>\n\n"
        f"Assalomu alaykum, <b>{user.get_display_name()}</b>!\n\n"
        f"Sizning bir martalik tasdiqlash kodingiz:\n\n"
        f"<code>🔑 {code}</code>\n\n"
        f"⏱ Kod <b>10 daqiqa</b> davomida amal qiladi.\n"
        f"🚫 Ushbu kodni hech kimga ma'lum qilmang!"
    )
    return _send_message(tg_id, text)


def notify_new_order(order):
    """Notify admin and chefs about a new order."""
    admin_id = getattr(settings, 'ADMIN_TELEGRAM_ID', '')

    items_text = '\n'.join(
        f"  • {item.name} × {item.quantity} — {int(item.total):,} so'm"
        for item in order.items.all()
    )

    order_types = {
        'delivery': '🛵 Yetkazib berish',
        'takeaway': '🛍 Olib ketish',
        'pickup': '🛍 Olib ketish',
        'dine_in': '🍽 Restoranda (Stol)',
        'table': '🍽 Restoranda (Stol)',
    }
    payment_methods = {
        'cash': '💵 Naqd pul',
        'card': '💳 Karta',
        'click': '🔹 Click',
        'payme': '🔸 Payme',
    }

    order_type_str = order_types.get(order.order_type, order.get_order_type_display())
    payment_str = payment_methods.get(order.payment_method, order.get_payment_method_display())

    text = (
        f"🔔 <b>YANGI BUYURTMA #{order.order_number}</b>\n\n"
        f"👤 Mijoz: <b>{order.customer_name}</b>\n"
        f"📱 Telefon: <code>{order.customer_phone}</code>\n"
        + (f"✈️ Telegram: @{order.telegram_username}\n" if order.telegram_username else "")
        + f"📦 Turi: {order_type_str}\n"
        + (f"🪑 Stol: #{order.table_number}\n" if order.table_number else "")
        + (f"📍 Manzil: {order.delivery_address}\n" if order.delivery_address else "")
        + f"💳 To'lov: {payment_str}\n\n"
        f"📋 <b>Buyurtma tarkibi:</b>\n{items_text}\n\n"
        f"💰 <b>Jami: {int(order.total):,} so'm</b>"
        + (f"\n📝 Izoh: {order.customer_notes}" if order.customer_notes else "")
    )
    if order.latitude and order.longitude:
        text += f"\n📍 Xarita: https://yandex.ru/maps/?pt={order.longitude},{order.latitude}&z=16&l=map"

    if admin_id and not _is_dev_mode():
        _send_message(admin_id, text.strip())
    elif _is_dev_mode():
        print(f"\n[DEV] New Order Telegram Notification:\n{text.strip()}\n")

    # Also notify chefs
    notify_chefs_new_order(order)
    return True


def notify_order_status_change(order, old_status):
    """Notify customer (if they have a chat) and admin about status change in customer's preferred language."""
    if old_status == order.status:
        return False

    admin_id = getattr(settings, 'ADMIN_TELEGRAM_ID', '')

    status_messages = {
        'uz': {
            'confirmed': f"✅ <b>#{order.order_number}-buyurtmangiz tasdiqlandi!</b>\nOshxonamiz taomni tayyorlashga kirishdi.",
            'preparing': f"👨‍🍳 <b>#{order.order_number}-buyurtmangiz tayyorlanmoqda!</b>\nMohir oshpazlarimiz taomingiz ustida ishlamoqda.",
            'ready': f"🔔 <b>#{order.order_number}-buyurtmangiz tayyor!</b>\nYoqimli ishtaha tilaymiz!",
            'delivered': f"🎉 <b>#{order.order_number}-buyurtmangiz muvaffaqiyatli yetkazildi!</b>\nAl Ezoz xizmatidan foydalanganingiz uchun rahmat!",
            'cancelled': f"❌ <b>#{order.order_number}-buyurtmangiz bekor qilindi.</b>",
        },
        'ru': {
            'confirmed': f"✅ <b>Ваш заказ №{order.order_number} подтверждён!</b>\nКухня приступила к приготовлению.",
            'preparing': f"👨‍🍳 <b>Ваш заказ №{order.order_number} готовится!</b>\nНаши повара уже готовят ваше блюдо.",
            'ready': f"🔔 <b>Ваш заказ №{order.order_number} готов!</b>\nПриятного аппетита!",
            'delivered': f"🎉 <b>Ваш заказ №{order.order_number} успешно доставлен!</b>\nСпасибо, что выбрали Al Ezoz!",
            'cancelled': f"❌ <b>Ваш заказ №{order.order_number} отменён.</b>",
        },
    }

    if admin_id and not _is_dev_mode():
        admin_text = (
            f"📊 <b>Buyurtma holati o'zgardi #{order.order_number}</b>\n"
            f"{old_status} ➔ <b>{order.status}</b>\n"
            f"👤 {order.customer_name} ({order.customer_phone})"
        )
        _send_message(admin_id, admin_text)

    # Notify customer via Telegram if they have a chat ID
    if order.telegram_chat_id:
        language = _customer_language(order.telegram_chat_id)
        msg_dict = status_messages.get(language, status_messages['uz'])
        msg = msg_dict.get(order.status)
        if msg:
            _send_message(order.telegram_chat_id, msg)

    return True


def notify_chefs_new_order(order):
    """Notify all chefs about a new order (KDS)."""
    chef_ids_str = getattr(settings, 'CHEF_TELEGRAM_IDS', '')
    if not chef_ids_str:
        return

    chef_ids = [cid.strip() for cid in str(chef_ids_str).split(',') if cid.strip()]

    items_text = '\n'.join(
        f"  • {item.name} × {item.quantity}"
        + (f" [{item.notes}]" if item.notes else "")
        for item in order.items.all()
    )

    order_types = {
        'delivery': '🛵 Yetkazib berish',
        'takeaway': '🛍 Olib ketish',
        'pickup': '🛍 Olib ketish',
        'dine_in': '🍽 Restoranda',
        'table': '🍽 Restoranda',
    }
    order_type_str = order_types.get(order.order_type, order.get_order_type_display())

    text = (
        f"👨‍🍳 <b>KDS — YANGI BUYURTMA #{order.order_number}</b>\n\n"
        f"📋 <b>Tarkibi:</b>\n{items_text}\n\n"
        f"🍽 {order_type_str}"
        + (f" | Stol #{order.table_number}" if order.table_number else "")
        + (f"\n📝 Izoh: {order.customer_notes}" if order.customer_notes else "")
    )
    
    if order.latitude and order.longitude:
        text += f"\n📍 Manzil xaritada: https://yandex.ru/maps/?pt={order.longitude},{order.latitude}&z=16&l=map"

    for chef_id in chef_ids:
        _send_message(chef_id, text)


def try_send_confirmation_code_on_order(order):
    """
    Buyurtma yaratilganda chaqiriladi.
    Agar foydalanuvchi avval botga /start bosgan bo'lsa (TelegramProfile yoki avvalgi Order'da chat_id mavjud),
    darhol tasdiqlash kodini uning Telegram akkauntiga yuboradi — havola bosish yoki /start bosish shart emas!
    """
    if not order.telegram_username:
        return False

    try:
        from apps.telegram_bot.models import TelegramProfile
        from apps.orders.models import Order

        username_clean = (
            order.telegram_username.strip()
            .replace('https://t.me/', '')
            .replace('http://t.me/', '')
            .replace('t.me/', '')
            .lstrip('@')
            .strip()
            .lower()
        )
        if not username_clean:
            return False

        # 1. TelegramProfile jadvalida shu username bo'yicha qidiramiz
        profile = TelegramProfile.objects.filter(
            username__iexact=username_clean
        ).exclude(chat_id='').first()

        chat_id = profile.chat_id if (profile and profile.chat_id) else None

        # 2. Agar TelegramProfile da topilmasa, avvalgi Order'lar tarixidan chat_id ni qidiramiz
        if not chat_id:
            prev_order = Order.objects.filter(
                telegram_username__iexact=username_clean
            ).exclude(telegram_chat_id='').order_by('-created_at').first()
            if prev_order and prev_order.telegram_chat_id:
                chat_id = str(prev_order.telegram_chat_id)
                # Profilni ham yaratib / to'ldirib qo'yamiz
                profile, _ = TelegramProfile.objects.update_or_create(
                    chat_id=chat_id,
                    defaults={'username': username_clean}
                )

        if not chat_id:
            logger.info(f"Foydalanuvchi @{username_clean} uchun bot chat_id topilmadi (avval /start bosmagan bo'lishi mumkin)")
            return False

        # Buyurtmaga chat_id bog'laymiz
        order.telegram_chat_id = str(chat_id)
        order.save(update_fields=['telegram_chat_id'])

        language = (profile.language if profile else None) or 'uz'

        from apps.telegram_bot.views import _send_confirmation_code
        return bool(_send_confirmation_code(chat_id, order, language))

    except Exception as e:
        logger.error(f"try_send_confirmation_code_on_order error: {e}")
        return False
