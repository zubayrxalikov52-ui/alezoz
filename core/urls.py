"""Allon Cafe — Root URL configuration."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Public pages & public APIs (menu, categories, products, contact)
    path('', include('apps.menu.urls')),

    # Orders & Checkout
    path('', include('apps.orders.urls')),

    # Custom Admin Panel (e.g. /secure-admin/ and /secure-admin)
    path(f'{settings.ADMIN_PANEL_URL}/', include('apps.dashboard.urls', namespace='dashboard')),
    path('api/admin/', include(('apps.dashboard.urls', 'dashboard'), namespace='api_admin')),

    # Chef Panel (e.g. /chef-panel/ and /chef-panel)
    path(f'{settings.CHEF_PANEL_URL}/', include('apps.dashboard.chef_urls', namespace='chef')),
    path('api/chef/', include(('apps.dashboard.chef_urls', 'chef'), namespace='api_chef')),

    # Accounts / Auth (API endpoints for 2FA, e.g. /api/auth/)
    path('api/auth/', include('apps.accounts.urls', namespace='accounts')),

    # Telegram Webhook
    path('api/telegram/', include('apps.telegram_bot.urls', namespace='telegram')),
]

from django.views.static import serve
from django.urls import re_path

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'apps.menu.views.error_404'
handler403 = 'apps.menu.views.error_403'
handler500 = 'apps.menu.views.error_500'
