import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Category, MenuItem, ContactMessage


def _json(data, status=200):
    return JsonResponse(data, status=status, safe=False)


class HomeView(View):
    def get(self, request):
        popular_items = MenuItem.objects.filter(
            is_available=True, is_popular=True
        ).select_related('category')[:8]
        categories = Category.objects.filter(is_active=True)
        return render(request, 'pages/home.html', {
            'popular_items': popular_items,
            'categories': categories,
        })


class MenuView(View):
    def get(self, request):
        categories = Category.objects.filter(is_active=True).prefetch_related('items')
        all_items = MenuItem.objects.filter(is_available=True).select_related('category')
        return render(request, 'pages/menu.html', {
            'categories': categories,
            'all_items': all_items,
        })


class AboutView(View):
    def get(self, request):
        return render(request, 'pages/about.html')


class ContactView(View):
    def get(self, request):
        return render(request, 'pages/contact.html')


class CartView(View):
    def get(self, request):
        return render(request, 'pages/cart.html')


# ── REST API Endpoints ────────────────────────────────────────────────────────

class CategoriesApiView(View):
    def get(self, request):
        categories = Category.objects.filter(is_active=True).order_by('sort_order')
        return _json([
            {
                'id': c.id,
                'name': c.name,
                'name_uz': c.name_uz or c.name,
                'name_ru': c.name_ru or c.name,
                'slug': c.slug,
                'icon': c.icon,
                'is_active': 1 if c.is_active else 0,
                'sort_order': c.sort_order,
            }
            for c in categories
        ])


class ProductsApiView(View):
    def get(self, request):
        category = request.GET.get('category')
        search = request.GET.get('search')
        items = MenuItem.objects.filter(is_available=True).select_related('category')

        if category and category != 'all':
            items = items.filter(category__slug=category)
        if search:
            items = items.filter(name__icontains=search)

        items = items.order_by('id')
        return _json([
            {
                'id': it.id,
                'name': it.name,
                'name_uz': it.name_uz or it.name,
                'name_ru': it.name_ru or it.name,
                'slug': it.category.slug if it.category else 'food',
                'category_slug': it.category.slug if it.category else 'food',
                'description': it.description,
                'description_uz': it.description_uz or it.description,
                'description_ru': it.description_ru or it.description,
                'price': int(it.price),
                'image': it.display_image,
                'is_available': 1 if it.is_available else 0,
                'is_featured': 1 if it.is_popular else 0,
            }
            for it in items
        ])


class MenuItemDetailApiView(View):
    def get(self, request, pk):
        try:
            item = MenuItem.objects.get(pk=pk, is_available=True)
            return _json({'item': item.to_dict()})
        except MenuItem.DoesNotExist:
            return _json({'error': 'Topilmadi'}, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class ContactApiView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return _json({'status': 'error', 'detail': 'Bad request'}, 400)

        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        subject = data.get('subject', 'Umumiy').strip()
        message = data.get('message', '').strip()

        if not name or not phone or not message:
            return _json({'status': 'error', 'detail': 'Ism, telefon va xabar kiritish shart'}, 400)

        ContactMessage.objects.create(
            name=name,
            phone=phone,
            subject=subject,
            message=message
        )
        return _json({'status': 'success', 'message': 'Xabaringiz qabul qilindi'})


# ── Custom Error Views ────────────────────────────────────────────────────────

def error_404(request, exception=None):
    if request.path.startswith('/api/'):
        return _json({'status': 'error', 'detail': 'Topilmadi'}, 404)
    return render(request, 'errors/404.html', status=404)


def error_403(request, exception=None):
    if request.path.startswith('/api/'):
        return _json({'status': 'error', 'detail': 'Ruxsat yo‘q'}, 403)
    return render(request, 'errors/403.html', status=403)


def error_500(request):
    if request.path.startswith('/api/'):
        return _json({'status': 'error', 'detail': 'Server ichki xatosi'}, 500)
    return render(request, 'errors/500.html', status=500)
