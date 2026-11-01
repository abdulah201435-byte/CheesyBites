import json

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils import timezone
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .models import ContactMessage, MenuItems, Offer, Review, StaffMember, StoryPage, StoryPost


@ensure_csrf_cookie
def index(request, *args, **kwargs):
    return render(request, "index.html")


@ensure_csrf_cookie
def csrf_token(request):
    return JsonResponse({"token": get_token(request)})


# ---------- reviews ----------
def _public(r):
    # the email is deliberately NOT included
    return {"id": r.id, "name": r.name, "text": r.text, "t": int(r.created_at.timestamp() * 1000)}


@require_GET
def reviews_list(request):
    return JsonResponse({"reviews": [_public(r) for r in Review.objects.all()[:500]]})


@require_POST
def review_submit(request):
    try:
        d = json.loads(request.body or b"{}")
    except ValueError:
        return JsonResponse({"error": "Invalid request."}, status=400)
    if d.get("website"):  # hidden spam field
        return JsonResponse({"error": "Rejected."}, status=400)
    name = str(d.get("name", "")).strip()
    email = str(d.get("email", "")).strip()
    text = str(d.get("text", "")).strip()
    if not 2 <= len(name) <= 60:
        return JsonResponse({"error": "Enter your name (2 to 60 characters)."}, status=400)
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({"error": "Enter a valid email address."}, status=400)
    if not 10 <= len(text) <= 5000:
        return JsonResponse({"error": "Write between 10 and 5000 characters."}, status=400)
    if "http://" in text.lower() or "https://" in text.lower() or "www." in text.lower():
        return JsonResponse({"error": "Links are not allowed in reviews."}, status=400)
    ip = request.META.get("REMOTE_ADDR", "unknown")
    if not cache.add(f"review-rate:{ip}", 1, 60):  # one review per minute per visitor
        return JsonResponse({"error": "Please wait a minute before posting another review."}, status=429)
    review = Review.objects.create(name=name, email=email, text=text)
    return JsonResponse({"review": _public(review)}, status=201)


# ---------- menu ----------
@require_GET
def menu_api(request):
    """Rows with the same dish name and category are merged into one card with several sizes."""
    grouped = {}
    for m in MenuItems.objects.all():
        key = (m.category.strip().lower(), m.name.strip().lower())
        g = grouped.setdefault(key, {"id": m.id, "name": m.name, "cat": m.category, "desc": "", "image": "", "sizes": []})
        if m.picture and not g["image"]:
            g["image"] = m.picture.url
        g["sizes"].append({"label": m.size or "", "price": float(m.price)})
    items = list(grouped.values())
    for g in items:
        g["sizes"].sort(key=lambda s: s["price"])
    return JsonResponse({"items": items})


# ---------- offers ----------
@require_GET
def offers_api(request):
    Offer.purge_old()  # deletes offers that ended / were unavailable more than 5 days ago
    out = []
    for o in Offer.objects.prefetch_related("items", "images"):
        extras = [i.image.url for i in o.images.all() if i.image]
        main = o.offer_picture.url if o.offer_picture else (extras[0] if extras else "")
        out.append({
            "slug": str(o.id), "name": o.offer_name, "desc": "",
            "image": main, "images": ([o.offer_picture.url] if o.offer_picture else []) + extras,
            "items": [{"name": i.name, "qty": i.quantity, "size": i.size} for i in o.items.all()],
            "orig": float(o.old_price) if o.old_price else 0, "price": float(o.new_price),
            "start": o.start_date.isoformat(), "end": o.end_date.isoformat(), "reason": "", "status": o.status,
        })
    return JsonResponse({"offers": out})


# ---------- contact form ----------
@require_POST
def contact_submit(request):
    """Saves the message in the database. The owner reads it in the admin panel; nobody else sees it."""
    try:
        d = json.loads(request.body or b"{}")
    except ValueError:
        return JsonResponse({"error": "Invalid request."}, status=400)
    if d.get("website"):  # hidden spam field
        return JsonResponse({"error": "Rejected."}, status=400)
    name = str(d.get("name", "")).strip()
    email = str(d.get("email", "")).strip()
    subject = str(d.get("subject", "")).strip()
    message = str(d.get("message", "")).strip()
    if not 2 <= len(name) <= 60:
        return JsonResponse({"error": "Enter your name (2 to 60 characters)."}, status=400)
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({"error": "Enter a valid email address."}, status=400)
    if not 3 <= len(subject) <= 100:
        return JsonResponse({"error": "Enter a subject (3 to 100 characters)."}, status=400)
    if not 10 <= len(message) <= 1000:
        return JsonResponse({"error": "Write between 10 and 1000 characters."}, status=400)
    ip = request.META.get("REMOTE_ADDR", "unknown")
    if not cache.add(f"contact-rate:{ip}", 1, 30):
        return JsonResponse({"error": "Please wait 30 seconds before sending another message."}, status=429)
    ContactMessage.objects.create(name=name, email=email, subject=subject, message=message)
    return JsonResponse({"ok": True}, status=201)


# ---------- our story ----------
@require_GET
def story_api(request):
    page = StoryPage.objects.first()
    posts = StoryPost.objects.filter(is_published=True, published_at__lte=timezone.now())
    return JsonResponse({
        "page": {
            "intro": page.intro if page else "", "mission": page.mission if page else "",
            "quality": page.food_quality if page else "",
            "image": page.picture.url if page and page.picture else "",
        },
        "posts": [{"slug": p.slug, "title": p.title, "date": p.published_at.date().isoformat(),
                   "excerpt": p.excerpt, "body": p.content, "image": p.image.url if p.image else ""} for p in posts],
        "team": [{"name": t.name, "role": t.role, "bio": t.bio, "photo": t.photo.url if t.photo else ""}
                 for t in StaffMember.objects.filter(is_active=True)],
    })