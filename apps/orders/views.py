import json
import logging
import random
import string
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Order, OrderItem
from apps.menu.models import MenuItem
from apps.telegram_bot.sender import notify_new_order, notify_order_status_change

logger = logging.getLogger(__name__)


def _json(data, status=200):
    return JsonResponse(data, status=status, safe=False)


class CheckoutView(View):
    def get(self, request):
        return render(request, 'pages/checkout.html')


class OrderStatusView(View):
    def get(self, request):
        tracking = request.GET.get('num', request.GET.get('tracking', ''))
        return render(request, 'pages/order_status.html', {'tracking': tracking})


@method_decorator(csrf_exempt, name='dispatch')
class PlaceOrderView(View):
    """POST /api/orders — Place order from website or API."""

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return _json({'status': 'error', 'detail': 'Noto‘g‘ri format'}, 400)

        items_data = data.get('items', [])
        if not items_data:
            return _json({'status': 'error', 'detail': 'Savat bo‘sh bo‘lishi mumkin emas'}, 400)

        customer_name = data.get('customer_name', '').strip()
        customer_phone = data.get('customer_phone', '').strip()

        if not customer_name or not customer_phone:
            return _json({'status': 'error', 'detail': 'Ism va telefon kiritish shart'}, 400)

        order_type = data.get('order_type', 'delivery')
        delivery_address = data.get('delivery_address', '').strip()
        comment = data.get('comment', data.get('customer_notes', '')).strip()
        table_number = data.get('table_number', '').strip()
        payment_method = data.get('payment_method', 'cash')
        
        # Telegram username (@ belgisisiz saqlash)
        telegram_username = data.get('telegram_username', '').strip().lstrip('@')
        
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        if latitude:
            try:
                latitude = float(latitude)
            except ValueError:
                latitude = None
        if longitude:
            try:
                longitude = float(longitude)
            except ValueError:
                longitude = None

        # Generate unique order number: e.g. 1007-1002
        today_code = datetime.now().strftime('%m%d')
        total_orders_count = Order.objects.count()
        order_num = f"{today_code}-{1001 + total_orders_count}"
        while Order.objects.filter(order_number=order_num).exists():
            total_orders_count += 1
            order_num = f"{today_code}-{1001 + total_orders_count}"

        total_price = 0
        calculated_items = []

        for item_data in items_data:
            name = item_data.get('name', 'Taom')
            price = int(item_data.get('price', 0))
            quantity = int(item_data.get('quantity', 1))
            if quantity <= 0:
                continue

            subtotal = price * quantity
            total_price += subtotal

            # Try finding MenuItem
            m_item = None
            item_id = item_data.get('id')
            if item_id:
                try:
                    m_item = MenuItem.objects.get(pk=item_id)
                except Exception:
                    pass

            calculated_items.append({
                'menu_item': m_item,
                'name': name,
                'price': price,
                'quantity': quantity,
                'subtotal': subtotal,
                'notes': item_data.get('notes', ''),
            })

        if not calculated_items:
            return _json({'status': 'error', 'detail': 'Hech qanday mahsulot topilmadi'}, 400)

        confirmation_code = ''.join(random.choices(string.digits, k=6))

        order = Order.objects.create(
            order_number=order_num,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_notes=comment,
            order_type=order_type,
            table_number=table_number,
            delivery_address=delivery_address,
            payment_method=payment_method,
            subtotal=total_price,
            delivery_fee=0,
            total=total_price,
            status=Order.STATUS_PENDING,
            latitude=latitude,
            longitude=longitude,
            confirmation_code=confirmation_code,
            telegram_username=telegram_username,
        )

        for itm in calculated_items:
            OrderItem.objects.create(
                order=order,
                menu_item=itm['menu_item'],
                name=itm['name'],
                price=itm['price'],
                quantity=itm['quantity'],
                notes=itm['notes'],
            )

        # Notify via Telegram is now moved to ConfirmOrderView
        # We just return the created order details so the user can verify it

        return _json({
            'status': 'success',
            'success': True,
            'order_number': order_num,
            'tracking_code': str(order.tracking_code),
            'total_price': total_price,
            'total': total_price,
            'has_telegram': bool(telegram_username),
        }, 201)


@method_decorator(csrf_exempt, name='dispatch')
class TrackOrderView(View):
    """GET /api/orders/<order_number_or_tracking_code>"""

    def get(self, request, order_identifier):
        # Can look up by order_number or tracking_code
        order = Order.objects.filter(order_number=order_identifier).first()
        if not order:
            try:
                order = Order.objects.filter(tracking_code=order_identifier).first()
            except Exception:
                pass

        if not order:
            return _json({'status': 'error', 'detail': 'Buyurtma topilmadi'}, 404)

        return _json(order.to_dict())

@method_decorator(csrf_exempt, name='dispatch')
class ConfirmOrderView(View):
    """POST /api/orders/<tracking_code>/confirm"""
    def post(self, request, tracking_code):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return _json({'status': 'error', 'detail': 'Noto‘g‘ri format'}, 400)
            
        code = str(data.get('code', '')).strip().replace(' ', '')
        if not code:
            return _json({'status': 'error', 'detail': 'Kodni kiriting'}, 400)
            
        order = Order.objects.filter(tracking_code=tracking_code).first()
        if not order:
            return _json({'status': 'error', 'detail': 'Buyurtma topilmadi'}, 404)
            
        if order.status != Order.STATUS_PENDING:
            return _json({'status': 'error', 'detail': 'Buyurtma allaqachon tasdiqlangan yoki bekor qilingan'}, 400)

        # Check 10-minute expiration
        if order.is_code_expired:
            order.update_status(Order.STATUS_CANCELLED, note='Tasdiqlash kodi muddati tugadi (10 daqiqa)')
            return _json({'status': 'error', 'detail': 'Tasdiqlash kodi muddati tugagan (10 daqiqa o‘tdi). Qaytadan buyurtma bering.'}, 400)
            
        expected_code = str(order.confirmation_code).strip().replace(' ', '')
        if expected_code != code:
            return _json({'status': 'error', 'detail': 'Kod xato! Telegram botdan yuborilgan 6 xonali kodni kiriting.'}, 400)
            
        order.update_status(Order.STATUS_CONFIRMED, note='User tasdiqladi')
        
        try:
            notify_order_status_change(order, Order.STATUS_PENDING)
        except Exception as e:
            logger.error(f"Telegram customer notification error on confirm: {e}")

        try:
            notify_new_order(order)
        except Exception as e:
            logger.error(f"Telegram staff notification error on confirm: {e}")
            
        return _json({'status': 'success', 'success': True, 'detail': 'Buyurtma tasdiqlandi'})
