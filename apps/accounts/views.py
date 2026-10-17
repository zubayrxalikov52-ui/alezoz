import json
import logging
import os
import random
from datetime import datetime, timedelta
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from .models import CustomUser, VerificationCode
from .auth import create_jwt_token, get_authenticated_user
from apps.telegram_bot.sender import send_verification_code_to_user, _is_dev_mode

logger = logging.getLogger(__name__)


def _json(data, status=200):
    return JsonResponse(data, status=status, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class Send2FACodeView(View):
    """Handles sending 2FA verification codes for Admin or Chef."""
    target_role = None  # 'admin' or 'chef' or None

    def post(self, request, role=None):
        role_to_check = self.target_role or role
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return _json({'status': 'error', 'detail': 'Noto‘g‘ri JSON format'}, 400)

        username = data.get('username', '').strip()

        if not username:
            return _json({'status': 'error', 'detail': 'Login kiritilmadi'}, 400)

        try:
            user = CustomUser.objects.get(username=username, is_active=True)
        except CustomUser.DoesNotExist:
            return _json({'status': 'error', 'detail': 'Foydalanuvchi topilmadi'}, 400)

        if role_to_check and user.role != role_to_check:
            return _json({'status': 'error', 'detail': 'Ruxsat yo‘q'}, 403)

        # Invalidate old codes
        VerificationCode.objects.filter(user=user, is_used=False).update(is_used=True)

        expire_seconds = getattr(settings, 'VERIFICATION_CODE_EXPIRE_SECONDS', 180)
        code_obj = VerificationCode.generate_for_user(user, expire_seconds=expire_seconds)
        send_verification_code_to_user(user, code_obj.code)

        dev_mode = _is_dev_mode()
        dev_code = code_obj.code if dev_mode else None

        # Also store in session
        request.session['pending_2fa_user_id'] = user.pk
        request.session['pending_2fa_role'] = user.role

        return _json({
            'status': 'code_sent',
            'success': True,
            'message': 'Kod yuborildi',
            'dev_code': dev_code,
            'expires_in': expire_seconds,
        })


@method_decorator(csrf_exempt, name='dispatch')
class Verify2FACodeView(View):
    """Handles verifying 2FA verification codes and issuing JWT & Django session."""
    target_role = None

    def post(self, request, role=None):
        role_to_check = self.target_role or role
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return _json({'status': 'error', 'detail': 'Noto‘g‘ri JSON format'}, 400)

        username = data.get('username', '').strip()
        code_str = str(data.get('code', '')).strip().replace(' ', '')

        if not code_str:
            return _json({'status': 'error', 'detail': 'Kod kiritilmadi'}, 400)

        user = None
        if username:
            user = CustomUser.objects.filter(username=username, is_active=True).first()
        if not user:
            user_id = request.session.get('pending_2fa_user_id')
            if user_id:
                user = CustomUser.objects.filter(pk=user_id, is_active=True).first()

        if not user:
            return _json({'status': 'error', 'detail': 'Foydalanuvchi topilmadi'}, 400)

        if role_to_check and user.role != role_to_check:
            return _json({'status': 'error', 'detail': 'Ruxsat yo‘q'}, 403)

        code_obj = VerificationCode.objects.filter(
            user=user, is_used=False
        ).order_by('-created_at').first()

        if not code_obj:
            return _json({'status': 'error', 'detail': 'Tasdiqlash kodi topilmadi yoki muddati tugagan'}, 400)

        ok, msg = code_obj.verify(code_str)
        if not ok:
            return _json({'status': 'error', 'detail': msg}, 400)

        # Login Django session
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        request.session.pop('pending_2fa_user_id', None)
        request.session.pop('pending_2fa_role', None)

        # Issue JWT token
        token = create_jwt_token(user)
        cookie_name = 'admin_jwt_token' if user.is_admin else 'chef_jwt_token'

        response = JsonResponse({
            'status': 'success',
            'success': True,
            'token': token,
            'role': user.role,
            'user': {
                'username': user.username,
                'full_name': user.get_display_name(),
                'role': user.role,
            },
            'redirect': '/secure-admin/' if user.is_admin else '/chef-panel/'
        })
        response.set_cookie(key=cookie_name, value=token, httponly=True, max_age=86400)
        return response


@method_decorator(csrf_exempt, name='dispatch')
class CurrentUserView(View):
    """GET /api/auth/me"""
    def get(self, request):
        user = get_authenticated_user(request)
        if not user:
            return _json({'status': 'error', 'detail': 'Autentifikatsiya talab qilinadi'}, 401)

        return _json({
            'sub': user.username,
            'username': user.username,
            'name': user.get_display_name(),
            'role': user.role,
            'is_admin': user.is_admin,
            'is_chef': user.is_chef,
        })


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(View):
    """POST /api/auth/logout"""
    def post(self, request):
        logout(request)
        response = _json({'status': 'success', 'success': True, 'message': 'Chiqildi'})
        response.delete_cookie('admin_jwt_token')
        response.delete_cookie('chef_jwt_token')
        return response
