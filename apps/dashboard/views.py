import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.utils.text import slugify

from apps.orders.models import Order, OrderItem
from apps.menu.models import Category, MenuItem, ContactMessage, Banner
from apps.accounts.models import CustomUser
from apps.accounts.auth import get_authenticated_user
from apps.telegram_bot.sender import notify_order_status_change

logger = logging.getLogger(__name__)


def _json(data, status=200):
    return JsonResponse(data, status=status, safe=False)


def _extract_request(*args):
    for arg in args:
        if hasattr(arg, 'META') or hasattr(arg, 'headers'):
            return arg
    return None


def require_admin(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        request = _extract_request(*args)
        user = get_authenticated_user(request)
        if not user or not user.is_admin:
            return _json({'status': 'error', 'detail': 'Ruxsat yo‘q. Faqat Administrator uchun'}, 403)
        if request:
            request.authenticated_user = user
        return view_func(*args, **kwargs)
    return wrapper


def require_chef_or_admin(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        request = _extract_request(*args)
        user = get_authenticated_user(request)
        if not user:
            return _json({'status': 'error', 'detail': 'Autentifikatsiya talab qilinadi'}, 401)
        if user.role not in (CustomUser.ROLE_ADMIN, CustomUser.ROLE_CHEF):
            return _json({'status': 'error', 'detail': 'Ruxsat yo‘q'}, 403)
        if request:
            request.authenticated_user = user
        return view_func(*args, **kwargs)
    return wrapper


def require_chef(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        request = _extract_request(*args)
        user = get_authenticated_user(request)
        if not user:
            return _json({'status': 'error', 'detail': 'Autentifikatsiya talab qilinadi'}, 401)
        if user.role not in (CustomUser.ROLE_ADMIN, CustomUser.ROLE_CHEF):
            return _json({'status': 'error', 'detail': 'Faqat Oshpaz uchun'}, 403)
        if request:
            request.authenticated_user = user
        return view_func(*args, **kwargs)
    return wrapper


# ── Admin Page Views ─────────────────────────────────────────────────────────

class AdminPageView(View):
    def get(self, request):
        return render(request, 'pages/admin.html')


class ChefPageView(View):
    def get(self, request):
        return render(request, 'pages/chef.html')


# ── Admin API Endpoints ───────────────────────────────────────────────────────

@method_decorator(csrf_exempt, name='dispatch')
class AdminStatsApiView(View):
    @method_decorator(require_admin)
    def get(self, request):
        today = timezone.now().date()
        orders_today = Order.objects.filter(created_at__date=today)

        today_revenue = sum(o.total for o in orders_today.filter(status__in=[Order.STATUS_CONFIRMED, Order.STATUS_PREPARING, Order.STATUS_READY, Order.STATUS_DELIVERED]))
        pending = Order.objects.filter(status__in=[Order.STATUS_PENDING, Order.STATUS_CONFIRMED, Order.STATUS_PREPARING]).count()
        completed = Order.objects.filter(status=Order.STATUS_DELIVERED).count()

        total_prods = MenuItem.objects.count()
        total_chefs = CustomUser.objects.filter(role=CustomUser.ROLE_CHEF, is_active=True).count()

        # Category counts
        cat_slugs = ['food', 'salad', 'snack', 'drink', 'dessert']
        cat_counts = []
        for s in cat_slugs:
            cnt = MenuItem.objects.filter(category__slug=s).count()
            cat_counts.append(cnt)

        return _json({
            'today_orders': orders_today.count(),
            'today_revenue': int(today_revenue),
            'pending_orders': pending,
            'completed_orders': completed,
            'total_products': total_prods,
            'total_chefs': total_chefs,
            'category_counts': cat_counts,
            'chart_labels': ['Dush', 'Sesh', 'Chor', 'Pay', 'Jum', 'Shan', 'Yak'],
            'chart_sales': [420000, 580000, 510000, 680000, 890000, 1120000, max(int(today_revenue), 950000)],
        })


@method_decorator(csrf_exempt, name='dispatch')
class AdminOrdersApiView(View):
    @method_decorator(require_admin)
    def get(self, request, order_id=None):
        if order_id:
            order = get_object_or_404(Order, pk=order_id)
            return _json(order.to_dict())

        status_filter = request.GET.get('status', '')
        orders = Order.objects.prefetch_related('items').order_by('-created_at')
        if status_filter and status_filter != 'all':
            orders = orders.filter(status=status_filter)

        return _json([o.to_dict() for o in orders[:100]])

    @method_decorator(require_admin)
    def patch(self, request, order_id=None):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return _json({'status': 'error', 'detail': 'Bad request'}, 400)

        order = get_object_or_404(Order, pk=order_id)
        new_status = data.get('status')
        if not new_status:
            return _json({'status': 'error', 'detail': 'Status kiritilmadi'}, 400)

        old_status = order.status
        if new_status == old_status:
            return _json({'status': 'success', 'new_status': new_status, 'order': order.to_dict()})

        order.update_status(new_status, note=data.get('note', ''))
        notify_order_status_change(order, old_status)

        return _json({'status': 'success', 'new_status': new_status, 'order': order.to_dict()})


def _get_request_data_and_files(request):
    """Extract POST/JSON data and FILES from request."""
    if request.content_type and 'multipart/form-data' in request.content_type:
        return request.POST, request.FILES
    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST or {}
    return data, request.FILES


@method_decorator(csrf_exempt, name='dispatch')
class AdminProductsApiView(View):
    @method_decorator(require_admin)
    def get(self, request, product_id=None):
        if product_id:
            item = get_object_or_404(MenuItem, pk=product_id)
            return _json(item.to_dict())
        items = MenuItem.objects.select_related('category').order_by('-created_at')
        return _json([item.to_dict() for item in items])

    @method_decorator(require_admin)
    def post(self, request, product_id=None):
        if product_id:
            return self.put(request, product_id)

        data, files = _get_request_data_and_files(request)

        cat_slug = data.get('category_slug', 'food')
        cat = Category.objects.filter(slug=cat_slug).first() or Category.objects.first()

        image_file = files.get('image_file') or files.get('image')

        item = MenuItem(
            category=cat,
            name=data.get('name', 'Yangi Taom'),
            description=data.get('description', ''),
            price=int(data.get('price', 0)),
            image_url=data.get('image_url', data.get('image', '') if isinstance(data.get('image'), str) else ''),
            is_available=str(data.get('is_available', '1')).lower() in ('1', 'true', 'on'),
            is_popular=str(data.get('is_featured', '0')).lower() in ('1', 'true', 'on'),
        )
        if image_file:
            item.image = image_file
        item.save()
        return _json({'status': 'created', 'item': item.to_dict()}, 201)

    @method_decorator(require_admin)
    def put(self, request, product_id=None):
        item = get_object_or_404(MenuItem, pk=product_id)
        data, files = _get_request_data_and_files(request)

        if 'name' in data:
            item.name = data['name']
        if 'description' in data:
            item.description = data['description']
        if 'price' in data:
            item.price = int(data['price'])
        if 'image' in data and isinstance(data['image'], str):
            item.image_url = data['image']
        if 'image_url' in data and isinstance(data['image_url'], str):
            item.image_url = data['image_url']
        if 'is_available' in data:
            item.is_available = str(data['is_available']).lower() in ('1', 'true', 'on')
        if 'is_featured' in data:
            item.is_popular = str(data['is_featured']).lower() in ('1', 'true', 'on')
        if 'category_slug' in data:
            cat = Category.objects.filter(slug=data['category_slug']).first()
            if cat:
                item.category = cat

        image_file = files.get('image_file') or files.get('image')
        if image_file:
            item.image = image_file

        item.save()
        return _json({'status': 'updated', 'item': item.to_dict()})

    @method_decorator(require_admin)
    def delete(self, request, product_id=None):
        item = get_object_or_404(MenuItem, pk=product_id)
        item.delete()
        return _json({'status': 'deleted'})


@method_decorator(csrf_exempt, name='dispatch')
class AdminProductToggleApiView(View):
    @method_decorator(require_admin)
    def patch(self, request, product_id=None):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return _json({'status': 'error', 'detail': 'Bad request'}, 400)

        item = get_object_or_404(MenuItem, pk=product_id)
        field = data.get('field')
        value = data.get('value', 0)

        if field == 'is_available':
            item.is_available = bool(value)
        elif field == 'is_featured':
            item.is_popular = bool(value)
        else:
            return _json({'status': 'error', 'detail': 'Noto‘g‘ri maydon'}, 400)

        item.save()
        return _json({'status': 'success'})


@method_decorator(csrf_exempt, name='dispatch')
class AdminCategoriesApiView(View):
    @method_decorator(require_admin)
    def get(self, request, cat_id=None):
        if cat_id:
            c = get_object_or_404(Category, pk=cat_id)
            return _json({
                'id': c.id,
                'name': c.name,
                'name_uz': c.name_uz or c.name,
                'name_ru': c.name_ru or c.name,
                'slug': c.slug,
                'icon': c.icon,
                'sort_order': c.sort_order,
                'is_active': c.is_active,
                'items_count': c.items.count()
            })

        categories = Category.objects.all().order_by('sort_order', 'id')
        return _json([
            {
                'id': c.id,
                'name': c.name,
                'name_uz': c.name_uz or c.name,
                'name_ru': c.name_ru or c.name,
                'slug': c.slug,
                'icon': c.icon,
                'sort_order': c.sort_order,
                'is_active': c.is_active,
                'items_count': c.items.count()
            }
            for c in categories
        ])

    @method_decorator(require_admin)
    def post(self, request, cat_id=None):
        if request.content_type and 'multipart/form-data' in request.content_type:
            data = request.POST.dict()
        else:
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return _json({'status': 'error', 'detail': 'Noto‘g‘ri ma’lumot formati'}, 400)

        name = data.get('name', '').strip()
        if not name:
            return _json({'status': 'error', 'detail': 'Kategoriya nomi kiritilishi shart'}, 400)

        name_uz = data.get('name_uz', '').strip() or name
        name_ru = data.get('name_ru', '').strip() or name
        icon = data.get('icon', '🍽️').strip() or '🍽️'
        sort_order = int(data.get('sort_order', 0) or 0)
        is_active = str(data.get('is_active', '1')).lower() in ('1', 'true', 'yes', 'on')
        slug = data.get('slug', '').strip()

        target_id = cat_id or data.get('id')
        if target_id:
            # Update existing category
            cat = get_object_or_404(Category, pk=target_id)
            cat.name = name
            cat.name_uz = name_uz
            cat.name_ru = name_ru
            cat.icon = icon
            cat.sort_order = sort_order
            cat.is_active = is_active

            if slug and slug != cat.slug:
                if Category.objects.filter(slug=slug).exclude(pk=cat.id).exists():
                    return _json({'status': 'error', 'detail': f"'{slug}' nomli slug allaqachon mavjud"}, 400)
                cat.slug = slug

            cat.save()
            return _json({
                'status': 'updated',
                'category': {'id': cat.id, 'name': cat.name, 'slug': cat.slug}
            }, 200)

        # Create new category
        if not slug:
            clean_name = name.replace("'", "").replace("’", "").replace("`", "")
            slug = slugify(clean_name, allow_unicode=True) or f"cat-{Category.objects.count() + 1}"

        if Category.objects.filter(slug=slug).exists():
            base_slug = slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

        cat = Category.objects.create(
            name=name,
            name_uz=name_uz,
            name_ru=name_ru,
            slug=slug,
            icon=icon,
            sort_order=sort_order,
            is_active=is_active
        )
        return _json({
            'status': 'created',
            'category': {'id': cat.id, 'name': cat.name, 'slug': cat.slug}
        }, 201)

    @method_decorator(require_admin)
    def put(self, request, cat_id=None):
        return self.post(request, cat_id=cat_id)

    @method_decorator(require_admin)
    def delete(self, request, cat_id=None):
        cat = get_object_or_404(Category, pk=cat_id)
        items_count = cat.items.count()
        cat.delete()
        return _json({'status': 'deleted', 'id': cat_id, 'deleted_items': items_count})


@method_decorator(csrf_exempt, name='dispatch')
class AdminBannersApiView(View):
    @method_decorator(require_admin)
    def get(self, request):
        banners = Banner.objects.all().order_by('sort_order', '-created_at')
        return _json([b.to_dict() for b in banners])

    @method_decorator(require_admin)
    def post(self, request):
        if request.content_type and 'multipart/form-data' in request.content_type:
            title = request.POST.get('title', '').strip()
            image_url = request.POST.get('image_url', '').strip()
            uploaded_file = request.FILES.get('image')
            sort_order = int(request.POST.get('sort_order', 0) or 0)
        else:
            try:
                data = json.loads(request.body)
            except (json.JSONDecodeError, ValueError):
                data = {}
            title = data.get('title', '').strip()
            image_url = data.get('image_url', '').strip()
            uploaded_file = None
            sort_order = int(data.get('sort_order', 0) or 0)

        if not uploaded_file and not image_url:
            return _json({'status': 'error', 'detail': 'Rasm fayli yoki rasm havolasi (URL) kiritilishi shart'}, 400)

        banner = Banner.objects.create(
            title=title,
            image=uploaded_file,
            image_url=image_url,
            sort_order=sort_order,
            is_active=True
        )
        return _json({'status': 'created', 'banner': banner.to_dict()}, 201)

    @method_decorator(require_admin)
    def patch(self, request, banner_id=None):
        banner = get_object_or_404(Banner, pk=banner_id)
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return _json({'status': 'error', 'detail': 'Bad request'}, 400)

        if 'is_active' in data:
            banner.is_active = bool(data['is_active'])
        if 'sort_order' in data:
            banner.sort_order = int(data['sort_order'])
        if 'title' in data:
            banner.title = data['title']
        banner.save()
        return _json({'status': 'updated', 'banner': banner.to_dict()})

    @method_decorator(require_admin)
    def delete(self, request, banner_id=None):
        banner = get_object_or_404(Banner, pk=banner_id)
        banner.delete()
        return _json({'status': 'deleted'})


@method_decorator(csrf_exempt, name='dispatch')
class AdminChefsApiView(View):
    @method_decorator(require_admin)
    def get(self, request):
        chefs = CustomUser.objects.filter(role=CustomUser.ROLE_CHEF).order_by('-created_at')
        return _json([{
            'id': c.id,
            'full_name': c.get_display_name(),
            'username': c.username,
            'telegram_id': c.telegram_id,
            'is_active': int(c.is_active),
            'created_at': c.created_at.strftime('%Y-%m-%d %H:%M'),
        } for c in chefs])

    @method_decorator(require_admin)
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return _json({'status': 'error', 'detail': 'Bad request'}, 400)

        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        full_name = data.get('full_name', '').strip()
        telegram_id = data.get('telegram_id', '').strip()

        if not username or not password:
            return _json({'status': 'error', 'detail': 'Username va parol majburiy'}, 400)

        if CustomUser.objects.filter(username=username).exists():
            return _json({'status': 'error', 'detail': 'Bu username allaqachon mavjud'}, 400)

        chef = CustomUser.objects.create_user(
            username=username,
            password=password,
            full_name=full_name,
            telegram_id=telegram_id,
            role=CustomUser.ROLE_CHEF,
            is_2fa_required=True,
        )
        return _json({'status': 'created', 'chef_id': chef.id}, 201)

    @method_decorator(require_admin)
    def delete(self, request, chef_id=None):
        chef = get_object_or_404(CustomUser, pk=chef_id, role=CustomUser.ROLE_CHEF)
        chef.delete()
        return _json({'status': 'deleted'})


@method_decorator(csrf_exempt, name='dispatch')
class AdminChefToggleApiView(View):
    @method_decorator(require_admin)
    def patch(self, request, chef_id=None):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return _json({'status': 'error', 'detail': 'Bad request'}, 400)

        chef = get_object_or_404(CustomUser, pk=chef_id, role=CustomUser.ROLE_CHEF)
        chef.is_active = bool(data.get('is_active', 1))
        chef.save()
        return _json({'status': 'success'})


@method_decorator(csrf_exempt, name='dispatch')
class AdminMessagesApiView(View):
    @method_decorator(require_admin)
    def get(self, request):
        messages = ContactMessage.objects.all()[:50]
        return _json([m.to_dict() for m in messages])


# ── Chef API Endpoints ────────────────────────────────────────────────────────

@method_decorator(csrf_exempt, name='dispatch')
class ChefOrdersApiView(View):
    @method_decorator(require_chef)
    def get(self, request):
        orders = Order.objects.filter(
            status__in=[Order.STATUS_PENDING, Order.STATUS_CONFIRMED, Order.STATUS_PREPARING, Order.STATUS_READY]
        ).prefetch_related('items').order_by('created_at')
        return _json([o.to_dict() for o in orders])

    @method_decorator(require_chef)
    def patch(self, request, order_id=None):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return _json({'status': 'error', 'detail': 'Bad request'}, 400)

        new_status = data.get('status')
        # Chef: Accepted, Preparing, Ready  |  Admin: also Delivered, Cancelled
        user = getattr(request, 'authenticated_user', None)
        is_admin = user and user.is_admin
        chef_statuses = [Order.STATUS_CONFIRMED, Order.STATUS_PREPARING, Order.STATUS_READY, 'Accepted', 'Preparing', 'Ready']
        admin_extra   = [Order.STATUS_DELIVERED, Order.STATUS_CANCELLED, 'Delivered', 'Cancelled']
        allowed_chef_statuses = chef_statuses + (admin_extra if is_admin else [])
        if new_status not in allowed_chef_statuses:
            return _json({"status": "error", "detail": "Bu statusni o'rnatishga ruxsat yo'q"}, 403)

        # normalize status name
        status_map = {
            'Accepted':  Order.STATUS_CONFIRMED,
            'Preparing': Order.STATUS_PREPARING,
            'Ready':     Order.STATUS_READY,
            'Delivered': Order.STATUS_DELIVERED,
            'Cancelled': Order.STATUS_CANCELLED,
        }
        normalized = status_map.get(new_status, new_status)

        order = get_object_or_404(Order, pk=order_id)
        old_status = order.status
        if normalized == old_status:
            return _json({'status': 'success', 'new_status': new_status, 'order': order.to_dict()})

        order.update_status(normalized, note=f"Chef ({request.authenticated_user.get_display_name()})")
        notify_order_status_change(order, old_status)

        return _json({'status': 'success', 'new_status': new_status, 'order': order.to_dict()})
