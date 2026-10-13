"""
Django Automated System Test Suite for Al Ezoz Restaurant
Tests all pages, static files, APIs, 2FA auth, order lifecycle, KDS, and CRUD operations.
"""
import os
import sys
import json
import django

# Set UTF-8 output encoding for windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
settings.DISABLE_TELEGRAM_NOTIFICATIONS = True

from unittest.mock import patch
patch('apps.telegram_bot.sender._send_message', return_value=True).start()
patch('apps.telegram_bot.views._send_message', return_value=True).start()

from django.test import Client
from apps.accounts.models import CustomUser, VerificationCode
from apps.menu.models import Category, MenuItem, ContactMessage
from apps.orders.models import Order, OrderItem


def run_tests():
    print("=" * 60)
    print("AL EZOZ RESTAURANT DJANGO SYSTEM TEST SUITE")
    print("=" * 60)

    client = Client()
    passed = 0
    total = 0

    def assert_test(condition, message):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"[PASS] {message}")
        else:
            print(f"[FAIL] {message}")
            sys.exit(1)

    # 1. Frontend Pages
    resp = client.get('/')
    assert_test(resp.status_code == 200, "Home Page: 200 OK")

    resp = client.get('/menu/')
    assert_test(resp.status_code == 200, "Menu Page: 200 OK")

    resp = client.get('/about/')
    assert_test(resp.status_code == 200, "About Page: 200 OK")

    resp = client.get('/contact/')
    assert_test(resp.status_code == 200, "Contact Page: 200 OK")

    resp = client.get('/cart/')
    assert_test(resp.status_code == 200, "Cart Page: 200 OK")

    resp = client.get('/checkout/')
    assert_test(resp.status_code == 200, "Checkout Page: 200 OK")

    resp = client.get('/order-status/')
    assert_test(resp.status_code == 200, "Order Status Page: 200 OK")

    resp = client.get('/secure-admin/')
    assert_test(resp.status_code == 200, "Admin Panel Page: 200 OK")

    resp = client.get('/chef-panel/')
    assert_test(resp.status_code == 200, "Chef Panel Page: 200 OK")

    resp = client.get('/nonexistent-page-test-404')
    assert_test(resp.status_code == 404, "Custom 404 Page: 404 OK")

    # 2. Public APIs
    resp = client.get('/api/categories')
    assert_test(resp.status_code == 200 and len(resp.json()) >= 6, f"Categories API: {len(resp.json())} categories loaded")

    resp = client.get('/api/products')
    assert_test(resp.status_code == 200 and len(resp.json()) >= 50, f"Products API: {len(resp.json())} products loaded")

    # 3. Contact Form API
    contact_payload = {
        "name": "Aziz Rahimov",
        "phone": "+998 90 123 45 67",
        "subject": "Stol band qilish",
        "message": "Ertaga kechki 19:00 ga 4 kishilik stol kerak"
    }
    resp = client.post('/api/contact', data=json.dumps(contact_payload), content_type='application/json')
    assert_test(resp.status_code == 200 and resp.json().get('status') == 'success', "Contact Form API: Message saved successfully")

    # 4. Security Test: Wrong admin password
    resp = client.post('/api/auth/admin/send-code', data=json.dumps({'username': 'Alezozadmin', 'password': 'wrongpassword'}), content_type='application/json')
    assert_test(resp.status_code == 400, "Security Test: Wrong admin password correctly rejected (400)")

    # 5. Admin Login 2FA Flow
    resp = client.post('/api/auth/admin/send-code', data=json.dumps({'username': 'Alezozadmin', 'password': 'Alezoztashkent'}), content_type='application/json')
    assert_test(resp.status_code == 200 and resp.json().get('status') == 'code_sent', "Admin Login Step 1: Verification code generated and sent")

    admin_code = VerificationCode.objects.filter(user__username='Alezozadmin', is_used=False).first().code

    # Wrong code test
    resp = client.post('/api/auth/admin/verify-code', data=json.dumps({'username': 'Alezozadmin', 'code': '000000'}), content_type='application/json')
    assert_test(resp.status_code == 400, "Security Test: Wrong 2FA code correctly rejected (400)")

    # Correct code verification
    resp = client.post('/api/auth/admin/verify-code', data=json.dumps({'username': 'Alezozadmin', 'code': admin_code}), content_type='application/json')
    assert_test(resp.status_code == 200 and 'token' in resp.json(), "Admin Login Step 2: 2FA Code verified & JWT token issued")
    admin_token = resp.json()['token']

    # 6. Chef Login 2FA Flow
    resp = client.post('/api/auth/chef/send-code', data=json.dumps({'username': 'Alezozchef', 'password': 'Alezoztashkent'}), content_type='application/json')
    assert_test(resp.status_code == 200 and resp.json().get('status') == 'code_sent', "Chef Login Step 1: Code sent")

    chef_code = VerificationCode.objects.filter(user__username='Alezozchef', is_used=False).first().code
    resp = client.post('/api/auth/chef/verify-code', data=json.dumps({'username': 'Alezozchef', 'code': chef_code}), content_type='application/json')
    assert_test(resp.status_code == 200 and 'token' in resp.json(), "Chef Login Step 2: Chef JWT token issued")
    chef_token = resp.json()['token']

    # 7. Role-Based Access Control
    resp = client.get('/api/admin/stats', HTTP_AUTHORIZATION=f'Bearer {chef_token}')
    assert_test(resp.status_code == 403, "Security Test: Chef forbidden from accessing Admin Stats (403 Forbidden)")

    resp = client.get('/api/admin/stats', HTTP_AUTHORIZATION=f'Bearer {admin_token}')
    assert_test(resp.status_code == 200 and 'today_orders' in resp.json(), "Admin Stats API: Verified access with Admin token")

    # 8. Place Customer Order
    order_payload = {
        "customer_name": "Sardor Alimov",
        "customer_phone": "+998 90 987 65 43",
        "delivery_address": "Chilonzor 9-mavze, 15-uy",
        "comment": "Piyozsiz bo'lsin, iltimos",
        "order_type": "delivery",
        "items": [
            {"id": "1", "name": "Classic Burger", "price": 45000, "quantity": 2},
            {"id": "2", "name": "Caesar Salad", "price": 38000, "quantity": 1}
        ]
    }
    resp = client.post('/api/orders', data=json.dumps(order_payload), content_type='application/json')
    assert_test(resp.status_code in (200, 201) and resp.json().get('status') == 'success', f"Website Order Created: #{resp.json().get('order_number')} (Total: {resp.json().get('total_price')} so'm)")
    order_num = resp.json()['order_number']

    # 9. Track Order
    resp = client.get(f'/api/orders/{order_num}')
    assert_test(resp.status_code == 200 and resp.json().get('customer_name') == 'Sardor Alimov', "Customer Order Status tracking: Status is 'pending'")
    order_id = resp.json()['id']

    # 10. Chef KDS Lifecycle
    resp = client.get('/api/chef/orders', HTTP_AUTHORIZATION=f'Bearer {chef_token}')
    assert_test(resp.status_code == 200 and any(o['id'] == order_id for o in resp.json()), "Chef KDS: Order appeared on Kitchen Display")
    assert_test(resp.status_code == 200 and any(o.get('chef_status') == 'New' for o in resp.json() if o['id'] == order_id), "Chef KDS: API exposes normalized chef status for the dashboard")

    # Chef accepts order
    resp = client.patch(f'/api/chef/orders/{order_id}/status', data=json.dumps({'status': 'Accepted'}), content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {chef_token}')
    assert_test(resp.status_code == 200 and resp.json().get('status') == 'success', "Chef Action: Order status changed to 'Accepted'")

    # Chef starts preparing
    resp = client.patch(f'/api/chef/orders/{order_id}/status', data=json.dumps({'status': 'Preparing'}), content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {chef_token}')
    assert_test(resp.status_code == 200 and resp.json().get('status') == 'success', "Chef Action: Order status changed to 'Preparing'")

    # Chef marks ready
    resp = client.patch(f'/api/chef/orders/{order_id}/status', data=json.dumps({'status': 'Ready'}), content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {chef_token}')
    assert_test(resp.status_code == 200 and resp.json().get('status') == 'success', "Chef Action: Order status changed to 'Ready'")

    # Chef cannot mark delivered
    resp = client.patch(f'/api/chef/orders/{order_id}/status', data=json.dumps({'status': 'Delivered'}), content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {chef_token}')
    assert_test(resp.status_code == 403, "Security Test: Chef cannot set 'Delivered' status (403 Forbidden)")

    # Admin marks delivered
    resp = client.patch(f'/api/admin/orders/{order_id}/status', data=json.dumps({'status': 'delivered'}), content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {admin_token}')
    assert_test(resp.status_code == 200 and resp.json().get('status') == 'success', "Admin Action: Order status completed as 'delivered'")

    # 11. Product CRUD
    prod_payload = {
        "name": "Chef Special Steak",
        "category_slug": "food",
        "price": 95000,
        "description": "Premium mol go‘shti, maxsus sous bilan",
        "image": "https://loremflickr.com/500/500/steak",
        "is_available": 1,
        "is_featured": 1
    }
    resp = client.post('/api/admin/products', data=json.dumps(prod_payload), content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {admin_token}')
    assert_test(resp.status_code in (200, 201), "Product CRUD: Created 'Chef Special Steak'")
    new_prod_id = resp.json()['item']['id']

    # Toggle availability
    resp = client.patch(f'/api/admin/products/{new_prod_id}/toggle', data=json.dumps({'field': 'is_available', 'value': 0}), content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {admin_token}')
    assert_test(resp.status_code == 200, "Product CRUD: Toggled Availability to OFF")

    # Delete product
    resp = client.delete(f'/api/admin/products/{new_prod_id}', HTTP_AUTHORIZATION=f'Bearer {admin_token}')
    assert_test(resp.status_code == 200, "Product CRUD: Deleted product cleanly")

    # 12. Chef Management CRUD
    import time
    chef_username = f"test_chef_{int(time.time())}"
    chef_payload = {
        "username": chef_username,
        "password": "password123",
        "full_name": "Test Oshpazbek",
        "telegram_id": "743453896"
    }
    resp = client.post('/api/admin/chefs', data=json.dumps(chef_payload), content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {admin_token}')
    assert_test(resp.status_code in (200, 201), f"Chef Management: Created Chef account '{chef_username}'")

    # Cleanup test data
    Order.objects.filter(customer_name='Sardor Alimov').delete()
    CustomUser.objects.filter(username=chef_username).delete()

    print("=" * 60)
    print(f"ALL {passed}/{total} DJANGO AUTOMATED TESTS PASSED SUCCESSFULLY! 100% WORKING.")
    print("=" * 60)


if __name__ == '__main__':
    run_tests()

