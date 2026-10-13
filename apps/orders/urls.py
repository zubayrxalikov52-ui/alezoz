from django.urls import path
from .views import CheckoutView, OrderStatusView, PlaceOrderView, TrackOrderView, ConfirmOrderView

urlpatterns = [
    # Pages
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('checkout', CheckoutView.as_view(), name='checkout_no_slash'),
    path('order-status/', OrderStatusView.as_view(), name='order_status'),
    path('order-status', OrderStatusView.as_view(), name='order_status_no_slash'),

    # Order APIs
    path('api/orders', PlaceOrderView.as_view(), name='api_orders'),
    path('api/orders/', PlaceOrderView.as_view(), name='api_orders_slash'),
    path('api/orders/<str:order_identifier>', TrackOrderView.as_view(), name='api_track_order'),
    path('api/orders/<str:order_identifier>/', TrackOrderView.as_view(), name='api_track_order_slash'),
    path('api/orders/<str:tracking_code>/confirm', ConfirmOrderView.as_view(), name='api_confirm_order'),
    path('api/orders/<str:tracking_code>/confirm/', ConfirmOrderView.as_view(), name='api_confirm_order_slash'),
]
