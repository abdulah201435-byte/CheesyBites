from datetime import timedelta

from django.utils import timezone

from .models import ContactMessage, MenuItems, Offer, Review


def dashboard_callback(request, context):
    """Numbers and lists shown on the admin home page (templates/admin/index.html)."""
    now = timezone.now()
    offers = list(Offer.objects.all())
    context.update({
        "cards": [
            {"icon": "restaurant_menu", "label": "Menu items", "value": MenuItems.objects.count(),
             "note": "dishes and sizes on the menu", "url": "admin:home_menuitems_changelist"},
            {"icon": "local_offer", "label": "Offers running now", "value": sum(o.status == "active" for o in offers),
             "note": f"{len(offers)} offers in total", "url": "admin:home_offer_changelist"},
            {"icon": "reviews", "label": "Reviews", "value": Review.objects.count(),
             "note": f"{Review.objects.filter(created_at__gte=now - timedelta(days=7)).count()} new this week",
             "url": "admin:home_review_changelist"},
            {"icon": "mail", "label": "Unread messages", "value": ContactMessage.objects.filter(is_read=False).count(),
             "note": f"{ContactMessage.objects.count()} messages in total", "url": "admin:home_contactmessage_changelist"},
        ],
        "latest_messages": ContactMessage.objects.all()[:6],
        "latest_reviews": Review.objects.all()[:6],
    })
    return context


def unread_badge(request):
    return ContactMessage.objects.filter(is_read=False).count() or None