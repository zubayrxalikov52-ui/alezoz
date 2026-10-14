from django.urls import path
from .views import (
    AdminPageView, AdminStatsApiView, AdminOrdersApiView,
    AdminProductsApiView, AdminProductToggleApiView,
    AdminCategoriesApiView, AdminChefsApiView, AdminChefToggleApiView,
    AdminMessagesApiView, AdminBannersApiView
)

app_name = 'dashboard'

urlpatterns = [
    path('', AdminPageView.as_view(), name='admin_page'),
    path('home/', AdminPageView.as_view(), name='admin_home'),

    # Direct APIs (when accessed via /api/admin/...)
    path('stats', AdminStatsApiView.as_view(), name='admin_stats_direct'),
    path('orders', AdminOrdersApiView.as_view(), name='admin_orders_direct'),
    path('orders/', AdminOrdersApiView.as_view(), name='admin_orders_direct_slash'),
    path('orders/<int:order_id>', AdminOrdersApiView.as_view(), name='admin_order_detail_direct'),
    path('orders/<int:order_id>/status', AdminOrdersApiView.as_view(), name='admin_order_status_direct'),

    path('products', AdminProductsApiView.as_view(), name='admin_products_direct'),
    path('products/', AdminProductsApiView.as_view(), name='admin_products_direct_slash'),
    path('products/<int:product_id>', AdminProductsApiView.as_view(), name='admin_product_detail_direct'),
    path('products/<int:product_id>/toggle', AdminProductToggleApiView.as_view(), name='admin_product_toggle_direct'),

    path('categories', AdminCategoriesApiView.as_view(), name='admin_categories_direct'),
    path('categories/', AdminCategoriesApiView.as_view(), name='admin_categories_direct_slash'),
    path('categories/<int:cat_id>', AdminCategoriesApiView.as_view(), name='admin_category_delete_direct'),

    path('banners', AdminBannersApiView.as_view(), name='admin_banners_direct'),
    path('banners/', AdminBannersApiView.as_view(), name='admin_banners_direct_slash'),
    path('banners/<int:banner_id>', AdminBannersApiView.as_view(), name='admin_banner_detail_direct'),

    path('chefs', AdminChefsApiView.as_view(), name='admin_chefs_direct'),
    path('chefs/', AdminChefsApiView.as_view(), name='admin_chefs_direct_slash'),
    path('chefs/<int:chef_id>', AdminChefsApiView.as_view(), name='admin_chef_delete_direct'),
    path('chefs/<int:chef_id>/toggle', AdminChefToggleApiView.as_view(), name='admin_chef_toggle_direct'),

    path('messages', AdminMessagesApiView.as_view(), name='admin_messages_direct'),
    path('messages/', AdminMessagesApiView.as_view(), name='admin_messages_direct_slash'),

    # Prefixed APIs (when accessed via /secure-admin/api/...)
    path('api/stats', AdminStatsApiView.as_view(), name='admin_stats'),
    path('api/orders', AdminOrdersApiView.as_view(), name='admin_orders'),
    path('api/orders/', AdminOrdersApiView.as_view(), name='admin_orders_slash'),
    path('api/orders/<int:order_id>', AdminOrdersApiView.as_view(), name='admin_order_detail'),
    path('api/orders/<int:order_id>/status', AdminOrdersApiView.as_view(), name='admin_order_status'),

    path('api/products', AdminProductsApiView.as_view(), name='admin_products'),
    path('api/products/', AdminProductsApiView.as_view(), name='admin_products_slash'),
    path('api/products/<int:product_id>', AdminProductsApiView.as_view(), name='admin_product_detail'),
    path('api/products/<int:product_id>/toggle', AdminProductToggleApiView.as_view(), name='admin_product_toggle'),

    path('api/categories', AdminCategoriesApiView.as_view(), name='admin_categories'),
    path('api/categories/', AdminCategoriesApiView.as_view(), name='admin_categories_slash'),
    path('api/categories/<int:cat_id>', AdminCategoriesApiView.as_view(), name='admin_category_delete'),

    path('api/banners', AdminBannersApiView.as_view(), name='admin_banners'),
    path('api/banners/', AdminBannersApiView.as_view(), name='admin_banners_slash'),
    path('api/banners/<int:banner_id>', AdminBannersApiView.as_view(), name='admin_banner_detail'),

    path('api/chefs', AdminChefsApiView.as_view(), name='admin_chefs'),
    path('api/chefs/', AdminChefsApiView.as_view(), name='admin_chefs_slash'),
    path('api/chefs/<int:chef_id>', AdminChefsApiView.as_view(), name='admin_chef_delete'),
    path('api/chefs/<int:chef_id>/toggle', AdminChefToggleApiView.as_view(), name='admin_chef_toggle'),

    path('api/messages', AdminMessagesApiView.as_view(), name='admin_messages'),
    path('api/messages/', AdminMessagesApiView.as_view(), name='admin_messages_slash'),
]
