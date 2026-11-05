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
from django.urls import path, re_path
from .models import ContactMessage, MenuItems, Offer, Review, StaffMember, StoryPage, StoryPost


@ensure_csrf_cookie
def index(request, *args, **kwargs):
    context = {
        "name": "Cheesy Bites",
        "name_colour": "#f5c71a",
        "tagline": "Delicious cheesy bites for every occasion",
        "open_time": "3:00 PM",
        "close_time": "3:00 AM",
        "delivery_range": "Within 5",
        "phone_number": "03236663067",
        "number": "03236663067", #whatsapp
        "email": "",
        "written_location": "C25C+RX3, Naimat Abad Rd, Faisalabad, Pakistan",
        "social_links": {
            "facebook": "https://www.tiktok.com/@cheesybites",
            "instagram": "https://www.tiktok.com/@cheesybites",
            "tiktok": "https://tiktok.com/@cheesybites",
        },
        "embedded_map_url": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d637.7480505566792!2d73.02222775192917!3d31.4095202024297!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x392243002959b011%3A0xa887d504e0345b44!2sCheesious%20Bites!5e0!3m2!1sen!2s!4v1793891430049!5m2!1sen!2s",
        "logo_svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 560" width="100%" height="100%">
                        <defs>
                            <!-- 3D Moulded Coral-Pink Tube Gradient -->
                            <linearGradient id="coralBase" x1="15%" y1="10%" x2="85%" y2="90%">
                                <stop id="stop-light" offset="0%" stop-color="#FF9A8B"></stop>
                                <stop id="stop-mid" offset="45%" stop-color="#ff6a59"></stop>
                                <stop id="stop-dark" offset="100%" stop-color="#C83728"></stop>
                            </linearGradient>

                            <!-- Inner Specular Ridge Highlight Gradient -->
                            <linearGradient id="ridgeHighlight" x1="0%" y1="0%" x2="0%" y2="100%">
                                <stop offset="0%" stop-color="#FFD8D0" stop-opacity="0.95"></stop>
                                <stop offset="100%" stop-color="#FF8E7F" stop-opacity="0.35"></stop>
                            </linearGradient>

                            <!-- Knife & Fork Inner Groove Shade -->
                            <linearGradient id="grooveShade" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#D94334"></stop>
                                <stop offset="100%" stop-color="#FF7868"></stop>
                            </linearGradient>

                            <!-- Soft 3D Relief Drop Shadow (Transparent-safe) -->
                            <filter id="tubeShadow" x="-15%" y="-15%" width="130%" height="130%">
                                <feDropShadow id="shadow-node" dx="2" dy="12" stdDeviation="9.6" flood-color="#2A0805" flood-opacity="0.55"></feDropShadow>
                            </filter>

                            <!-- Reusable Chef Hat & Face Monoline Tube Paths -->
                            <g id="chef-hat-paths">
                                <!-- 1. Top Crown Arch: Left downward hook -> high top arch -> right loop knot -->
                                <path d="M 216 128 C 198 102, 204 54, 244 38 C 288 22, 378 65, 466 105 C 485 113, 505 112, 504 97 C 503 83, 478 82, 466 96"></path>

                                <!-- 2. Lower Crown Band: From right loop knot -> sweeping down-left -> left small loop -->
                                <path d="M 466 96 C 412 132, 344 176, 282 170 C 254 167, 232 148, 240 136 C 247 126, 266 142, 270 162"></path>

                                <!-- 3. Left Vertical Hat Side & Cheek Line -->
                                <path d="M 270 162 C 275 215, 277 275, 282 325"></path>

                                <!-- 4. Right Detached Vertical Hat Side -->
                                <path d="M 432 152 C 412 195, 402 242, 400 284"></path>

                                <!-- 5. Middle Headband Arch (with left overhang & right downward curve) -->
                                <path d="M 252 264 C 292 238, 355 240, 402 278"></path>

                                <!-- 6. Mustache (Wavy bar with sharp center upward peak, extending past both cheeks) -->
                                <path d="M 248 318 C 272 332, 294 336, 312 326 C 325 319, 333 308, 338 302 C 344 310, 352 324, 368 334 C 386 345, 408 348, 424 352"></path>

                                <!-- 7. Chin / Beard U-Loop + Lower Right Jaw Check -->
                                <path d="M 282 325 C 288 368, 315 390, 342 388 C 372 386, 392 355, 402 304"></path>
                            </g>

                            <!-- Curved Text Baseline Arcs (Tops of letters facing inward toward center) -->
                            <!-- Left Arc for "EAT GOOD" -->
                            <path id="eatGoodArc" d="M 122 336 A 215 215 0 0 0 278 518" fill="none"></path>
                            <!-- Right Arc for "FEEL GOOD" -->
                            <path id="feelGoodArc" d="M 382 522 A 215 215 0 0 0 538 336" fill="none"></path>
                        </defs>

                        <!-- ==================== MAIN LOGO ARTWORK GROUP ==================== -->
                        <g filter="url(#tubeShadow)">

                            <!-- 1. LEFT KNIFE (Angled -21 deg, blade facing out-left, straight spine facing hat) -->
                            <g transform="rotate(-21 195 275)">
                                <!-- Outer 3D Moulded Knife Body -->
                                <path d="M 204 122
                                         C 172 145, 160 212, 166 292
                                         L 182 302
                                         L 182 414
                                         C 182 426, 204 426, 204 414
                                         Z" fill="url(#coralBase)" stroke="url(#coralBase)" stroke-width="10" stroke-linejoin="round" stroke-linecap="round"></path>
                                <!-- Inner Recessed Blade & Handle Detail -->
                                <path d="M 196 146 C 177 168, 171 220, 175 286 L 196 286 Z" fill="url(#grooveShade)"></path>
                                <!-- Raised 3D Bevel Highlight along Knife Rim -->
                                <path d="M 200 132 C 175 155, 165 215, 170 290 L 185 300 L 185 412 C 185 420, 200 420, 200 412 L 200 132" fill="none" stroke="url(#ridgeHighlight)" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"></path>
                            </g>

                            <!-- 2. RIGHT FORK (Angled +20 deg, 4 tines at top-right, sleek handle down-left) -->
                            <g transform="rotate(20 465 285)">
                                <!-- Fork Handle & Neck Base -->
                                <path d="M 455 232
                                         L 452 416
                                         C 452 429, 476 429, 476 416
                                         L 473 232
                                         Z" fill="url(#coralBase)" stroke="url(#coralBase)" stroke-width="8" stroke-linejoin="round"></path>
                                <!-- Fork Head Shoulder -->
                                <path d="M 436 196
                                         C 436 224, 452 232, 455 238
                                         L 473 238
                                         C 476 232, 492 224, 492 196
                                         Z" fill="url(#coralBase)" stroke="url(#coralBase)" stroke-width="8" stroke-linejoin="round"></path>
                                <!-- 4 Distinct Tines -->
                                <g stroke="url(#coralBase)" stroke-width="10" stroke-linecap="round">
                                    <line x1="438" y1="126" x2="438" y2="200"></line>
                                    <line x1="455" y1="126" x2="455" y2="200"></line>
                                    <line x1="473" y1="126" x2="473" y2="200"></line>
                                    <line x1="490" y1="126" x2="490" y2="200"></line>
                                </g>
                                <!-- 3D Inner Highlight on Fork Tines & Handle -->
                                <g stroke="url(#ridgeHighlight)" stroke-width="3.5" stroke-linecap="round" fill="none">
                                    <line x1="438" y1="128" x2="438" y2="198"></line>
                                    <line x1="455" y1="128" x2="455" y2="198"></line>
                                    <line x1="473" y1="128" x2="473" y2="198"></line>
                                    <line x1="490" y1="128" x2="490" y2="198"></line>
                                    <path d="M 440 200 C 442 220, 456 228, 458 238 L 456 414 C 456 422, 472 422, 472 414 L 470 238 C 472 228, 486 220, 488 200"></path>
                                </g>
                            </g>

                            <!-- 3. CENTER CHEF HAT & MUSTACHE FACE (Layered 3D Tube Effect) -->
                            <!-- Outer Coral Tube Base -->
                            <use id="hat-base-stroke" href="#chef-hat-paths" fill="none" stroke="url(#coralBase)" stroke-width="15.5" stroke-linecap="round" stroke-linejoin="round"></use>
                            <!-- Inner 3D Specular Bevel Ridge -->
                            <use id="hat-highlight-stroke" href="#chef-hat-paths" fill="none" stroke="url(#ridgeHighlight)" stroke-width="5.9" stroke-linecap="round" stroke-linejoin="round" transform="translate(-1, -1.5)"></use>

                            <!-- 4. THREE PLUMP 5-POINTED STARS AT BOTTOM CENTER -->
                            <g fill="url(#coralBase)" stroke="url(#coralBase)" stroke-width="5" stroke-linejoin="round">
                                <!-- Left Star (290, 434) -->
                                <polygon points="290,416 295,427 307,428 298,436 301,448 290,442 279,448 282,436 273,428 285,427"></polygon>
                                <!-- Center Star (332, 436) -->
                                <polygon points="332,418 337,429 349,430 340,438 343,450 332,444 321,450 324,438 315,430 327,429"></polygon>
                                <!-- Right Star (374, 438) -->
                                <polygon points="374,420 379,431 391,432 382,440 385,452 374,446 363,452 366,440 357,432 369,431"></polygon>
                            </g>
                            <!-- Star 3D Inner Highlights -->
                            <g fill="url(#ridgeHighlight)" opacity="0.85">
                                <polygon points="290,420 293,428 302,429 295,435 297,443 290,438 283,443 285,435 278,429 287,428"></polygon>
                                <polygon points="332,422 335,430 344,431 337,437 339,445 332,440 325,445 327,437 320,431 329,430"></polygon>
                                <polygon points="374,424 377,432 386,433 379,439 381,447 374,442 367,447 369,439 362,433 371,432"></polygon>
                            </g>

                            <!-- 5. CURVED 3D EMBOSSED TEXT: "EAT GOOD" & "FEEL GOOD" -->
                            <g font-family="'Anton', 'Impact', 'Arial Black', sans-serif" font-size="46" letter-spacing="2.5">
                                <!-- Extruded Base Layer -->
                                <text fill="url(#coralBase)" stroke="#C83728" stroke-width="4" stroke-linejoin="round" paint-order="stroke fill">
                                    <textPath href="#eatGoodArc" startOffset="50%" text-anchor="middle">EAT GOOD</textPath>
                                </text>
                                <text fill="url(#coralBase)" stroke="#C83728" stroke-width="4" stroke-linejoin="round" paint-order="stroke fill">
                                    <textPath href="#feelGoodArc" startOffset="50%" text-anchor="middle">FEEL GOOD</textPath>
                                </text>

                                <!-- Top 3D Highlight Bevel Layer -->
                                <text fill="url(#ridgeHighlight)" opacity="0.7" transform="translate(-1, -1.5)">
                                    <textPath href="#eatGoodArc" startOffset="50%" text-anchor="middle">EAT GOOD</textPath>
                                </text>
                                <text fill="url(#ridgeHighlight)" opacity="0.7" transform="translate(-1, -1.5)">
                                    <textPath href="#feelGoodArc" startOffset="50%" text-anchor="middle">FEEL GOOD</textPath>
                                </text>
                            </g>

                        </g>
                    </svg>""",
    }
    return render(request, "index.html", context = context)


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
