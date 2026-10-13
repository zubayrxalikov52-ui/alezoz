from django.urls import path
from .views import (
    HomeView, MenuView, AboutView, ContactView, CartView,
    CategoriesApiView, ProductsApiView, MenuItemDetailApiView, ContactApiView
)

urlpatterns = [
    # Pages
    path('', HomeView.as_view(), name='home'),
    path('menu/', MenuView.as_view(), name='menu'),
    path('menu', MenuView.as_view(), name='menu_no_slash'),
    path('about/', AboutView.as_view(), name='about'),
    path('about', AboutView.as_view(), name='about_no_slash'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('contact', ContactView.as_view(), name='contact_no_slash'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart', CartView.as_view(), name='cart_no_slash'),

    # Public JSON APIs
    path('api/categories', CategoriesApiView.as_view(), name='api_categories'),
    path('api/products', ProductsApiView.as_view(), name='api_products'),
    path('api/contact', ContactApiView.as_view(), name='api_contact'),

    # Menu items API aliases
    path('api/menu/categories', CategoriesApiView.as_view(), name='api_menu_categories'),
    path('api/menu/categories/', CategoriesApiView.as_view(), name='api_menu_categories_slash'),
    path('api/menu/items', ProductsApiView.as_view(), name='api_menu_items'),
    path('api/menu/items/', ProductsApiView.as_view(), name='api_menu_items_slash'),
    path('api/menu/items/<int:pk>/', MenuItemDetailApiView.as_view(), name='api_menu_item_detail'),
]
