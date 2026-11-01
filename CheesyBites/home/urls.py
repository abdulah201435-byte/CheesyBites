from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.index, name="home"),

    # data for the website
    path("api/csrf/", views.csrf_token),
    path("api/contact/", views.contact_submit),
    path("api/story/", views.story_api),
    path("api/menu/", views.menu_api),
    path("api/offers/", views.offers_api),
    path("api/reviews/", views.reviews_list),
    path("api/reviews/submit/", views.review_submit),

    # page addresses: all of them show index.html
    re_path(r"^(?:home|menu|offers|reviews|story|contact|find-location)/?$", views.index),
    re_path(r"^(?:reviews|offers|stories)/[\w-]+/?$", views.index),
]