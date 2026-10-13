import jwt
from datetime import datetime, timedelta
from django.conf import settings
from apps.accounts.models import CustomUser

SECRET_KEY = getattr(settings, 'SECRET_KEY', 'allon_cafe_default_secret_key_restaurant_2026')
ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24


def create_jwt_token(user: CustomUser) -> str:
    payload = {
        'sub': user.username,
        'user_id': user.pk,
        'name': user.get_display_name(),
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_authenticated_user(request):
    """Returns CustomUser if authenticated via JWT Bearer header, JWT Cookie, or Session."""
    if not request:
        return None

    # 1. Bearer Header precedence
    auth_header = ''
    if hasattr(request, 'headers'):
        auth_header = request.headers.get('Authorization', '')
    if not auth_header and hasattr(request, 'META'):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ', 1)[1].strip()
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get('sub')
            if username:
                user = CustomUser.objects.filter(username=username, is_active=True).first()
                if user:
                    return user
        except Exception:
            return None

    # 2. Cookies (admin_jwt_token / chef_jwt_token)
    if hasattr(request, 'COOKIES'):
        cookie_token = request.COOKIES.get('admin_jwt_token') or request.COOKIES.get('chef_jwt_token')
        if cookie_token:
            try:
                payload = jwt.decode(cookie_token, SECRET_KEY, algorithms=[ALGORITHM])
                username = payload.get('sub')
                if username:
                    user = CustomUser.objects.filter(username=username, is_active=True).first()
                    if user:
                        return user
            except Exception:
                pass

    # 3. Session User fallback
    if hasattr(request, 'user') and request.user.is_authenticated:
        return request.user

    return None
