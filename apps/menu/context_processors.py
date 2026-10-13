def cart_count(request):
    """Inject cart count into every template context."""
    cart = request.session.get('cart', {})
    count = sum(item.get('quantity', 0) for item in cart.values())
    return {'cart_count': count}
