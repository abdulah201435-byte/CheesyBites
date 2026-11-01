"""
Django settings for CheesyBites project (with the Unfold admin theme).
"""

from pathlib import Path

from django.urls import reverse_lazy

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-^f_$+@-n=&atifz^6+ml)jxf$&=8a2t%4tqpuw+#d66vubj4u%'

DEBUG = True

ALLOWED_HOSTS = ['*', '.pythonanywhere.com', 'localhost', '127.0.0.1']


# ---------- Applications ----------
# "unfold" MUST be the first line (before django.contrib.admin)
INSTALLED_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'home',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'CheesyBites.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'CheesyBites.wsgi.application'


# ---------- Database ----------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ---------- Language and time ----------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Karachi'   # offer times typed in the admin are Pakistan time
USE_I18N = True
USE_TZ = True


# ---------- Static and media files ----------
STATIC_URL = 'static/'
# uses your folder whether it is called "static" or "statics"
STATICFILES_DIRS = [p for p in (BASE_DIR / 'static', BASE_DIR / 'statics') if p.exists()]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ---------- Admin theme (Unfold) ----------
UNFOLD = {
    "SITE_TITLE": "Cheesy Bites",
    "SITE_HEADER": "Cheesy Bites",
    "SITE_URL": "/",
    "DASHBOARD_CALLBACK": "home.dashboard.dashboard_callback",
    "COLORS": {   # yellow brand colour
        "primary": {
            "50": "254 252 232", "100": "254 249 195", "200": "254 240 138", "300": "253 224 71",
            "400": "250 204 21", "500": "234 179 8", "600": "202 138 4", "700": "161 98 7",
            "800": "133 77 14", "900": "113 63 18", "950": "66 32 6",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {"title": "Overview", "items": [
                {"title": "Dashboard", "icon": "dashboard", "link": reverse_lazy("admin:index")},
            ]},
            {"title": "Restaurant", "separator": True, "items": [
                {"title": "Menu items", "icon": "restaurant_menu", "link": reverse_lazy("admin:home_menuitems_changelist")},
                {"title": "Offers", "icon": "local_offer", "link": reverse_lazy("admin:home_offer_changelist")},
            ]},
            {"title": "Customers", "separator": True, "items": [
                {"title": "Reviews", "icon": "reviews", "link": reverse_lazy("admin:home_review_changelist")},
                {"title": "Contact messages", "icon": "mail", "link": reverse_lazy("admin:home_contactmessage_changelist"),
                 "badge": "home.dashboard.unread_badge"},
            ]},
            {"title": "Website", "separator": True, "items": [
                {"title": "Our Story page", "icon": "auto_stories", "link": reverse_lazy("admin:home_storypage_changelist")},
                {"title": "Story posts", "icon": "article", "link": reverse_lazy("admin:home_storypost_changelist")},
                {"title": "Team members", "icon": "groups", "link": reverse_lazy("admin:home_staffmember_changelist")},
            ]},
            {"title": "Administration", "separator": True, "items": [
                {"title": "Users", "icon": "person", "link": reverse_lazy("admin:auth_user_changelist")},
                {"title": "Groups", "icon": "lock", "link": reverse_lazy("admin:auth_group_changelist")},
            ]},
        ],
    },
}