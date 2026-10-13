from django.urls import path
from .views import Send2FACodeView, Verify2FACodeView, CurrentUserView, LogoutView

app_name = 'accounts'

urlpatterns = [
    # General login & verify
    path('login', Send2FACodeView.as_view(), name='login_direct'),
    path('login/', Send2FACodeView.as_view(), name='login'),
    path('verify', Verify2FACodeView.as_view(), name='verify_direct'),
    path('verify/', Verify2FACodeView.as_view(), name='verify'),
    path('logout', LogoutView.as_view(), name='logout_direct'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me', CurrentUserView.as_view(), name='current_user_direct'),
    path('me/', CurrentUserView.as_view(), name='current_user'),

    # Admin specific 2FA endpoints
    path('admin/send-code', Send2FACodeView.as_view(target_role='admin'), name='admin_send_code'),
    path('admin/send-code/', Send2FACodeView.as_view(target_role='admin'), name='admin_send_code_slash'),
    path('admin/request-code', Send2FACodeView.as_view(target_role='admin'), name='admin_request_code'),
    path('admin/request-code/', Send2FACodeView.as_view(target_role='admin'), name='admin_request_code_slash'),
    path('admin/verify-code', Verify2FACodeView.as_view(target_role='admin'), name='admin_verify_code'),
    path('admin/verify-code/', Verify2FACodeView.as_view(target_role='admin'), name='admin_verify_code_slash'),

    # Chef specific 2FA endpoints
    path('chef/send-code', Send2FACodeView.as_view(target_role='chef'), name='chef_send_code'),
    path('chef/send-code/', Send2FACodeView.as_view(target_role='chef'), name='chef_send_code_slash'),
    path('chef/request-code', Send2FACodeView.as_view(target_role='chef'), name='chef_request_code'),
    path('chef/request-code/', Send2FACodeView.as_view(target_role='chef'), name='chef_request_code_slash'),
    path('chef/verify-code', Verify2FACodeView.as_view(target_role='chef'), name='chef_verify_code'),
    path('chef/verify-code/', Verify2FACodeView.as_view(target_role='chef'), name='chef_verify_code_slash'),
]
