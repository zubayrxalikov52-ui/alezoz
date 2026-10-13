from django.urls import path
from .views import ChefPageView, ChefOrdersApiView

app_name = 'chef'

urlpatterns = [
    path('', ChefPageView.as_view(), name='chef_page'),
    path('home/', ChefPageView.as_view(), name='chef_home'),

    # Direct APIs (when accessed via /api/chef/...)
    path('orders', ChefOrdersApiView.as_view(), name='chef_orders_direct'),
    path('orders/', ChefOrdersApiView.as_view(), name='chef_orders_direct_slash'),
    path('orders/<int:order_id>/status', ChefOrdersApiView.as_view(), name='chef_order_status_direct'),

    # Prefixed APIs (when accessed via /chef-panel/api/...)
    path('api/orders', ChefOrdersApiView.as_view(), name='chef_orders'),
    path('api/orders/', ChefOrdersApiView.as_view(), name='chef_orders_slash'),
    path('api/orders/<int:order_id>/status', ChefOrdersApiView.as_view(), name='chef_order_status'),
]
