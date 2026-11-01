from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin, UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from unfold.admin import ModelAdmin, TabularInline
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from django.utils.html import format_html

from .models import (ContactMessage, MenuItems, Offer, OfferImage, OfferItem, Review,
                     StaffMember, StoryPage, StoryPost)


def _thumb(f):
    return format_html('<img src="{}" style="height:48px;border-radius:6px">', f.url) if f else "-"


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ("name", "email", "short_text", "words", "created_at")
    search_fields = ("name", "email", "text")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)
    actions = ["delete_selected"]

    @admin.display(description="Review")
    def short_text(self, obj):
        return obj.text[:80] + ("..." if len(obj.text) > 80 else "")

    @admin.display(description="Words")
    def words(self, obj):
        return obj.word_count


@admin.register(MenuItems)
class MenuItemsAdmin(ModelAdmin):
    list_display = ("preview", "name", "category", "size", "price", "created_at")
    list_display_links = ("preview", "name")
    list_filter = ("category",)
    search_fields = ("name", "category")
    readonly_fields = ("preview",)
    fields = ("name", "category", "size", "price", "picture", "preview")

    @admin.display(description="Picture")
    def preview(self, obj):
        return _thumb(obj.picture)


class OfferItemInline(TabularInline):
    model = OfferItem
    extra = 1          # click "Add another item in this deal" to add more rows


class OfferImageInline(TabularInline):
    model = OfferImage
    extra = 1          # click "Add another extra picture" to add more pictures


@admin.register(Offer)
class OfferAdmin(ModelAdmin):
    list_display = ("preview", "offer_name", "is_available", "old_price", "new_price", "start_date", "end_date", "state", "removed_on")
    list_display_links = ("preview", "offer_name")
    list_filter = ("is_available",)
    search_fields = ("offer_name",)
    inlines = [OfferItemInline, OfferImageInline]
    fields = ("offer_name", "offer_picture", "preview", "is_available", "old_price", "new_price", "start_date", "end_date", "unavailable_since", "created_at")
    readonly_fields = ("preview", "unavailable_since", "created_at")
    date_hierarchy = "start_date"

    def changelist_view(self, request, extra_context=None):
        Offer.purge_old()  # old offers disappear as soon as the owner opens this list
        return super().changelist_view(request, extra_context)

    @admin.display(description="Picture")
    def preview(self, obj):
        return _thumb(obj.offer_picture)

    @admin.display(description="State")
    def state(self, obj):
        return {"active": "Available now", "upcoming": "Coming soon", "expired": "Expired", "unavailable": "Not available"}[obj.status]

    @admin.display(description="Deleted automatically on")
    def removed_on(self, obj):
        return obj.delete_on.strftime("%d %b %Y %H:%M")


@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdmin):
    list_display = ("subject", "name", "email", "created_at", "is_read")
    list_display_links = ("subject",)
    list_editable = ("is_read",)
    list_filter = ("is_read",)
    search_fields = ("name", "email", "subject", "message")
    date_hierarchy = "created_at"
    readonly_fields = ("name", "email", "subject", "message", "created_at")
    fields = ("name", "email", "subject", "message", "created_at", "is_read")

    def has_add_permission(self, request):
        return False  # messages only come from the website


@admin.register(StoryPage)
class StoryPageAdmin(ModelAdmin):
    fields = ("intro", "mission", "food_quality", "picture")

    def has_add_permission(self, request):
        return not StoryPage.objects.exists()  # only one Our Story page

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(StoryPost)
class StoryPostAdmin(ModelAdmin):
    list_display = ("preview", "title", "is_published", "published_at")
    list_display_links = ("preview", "title")
    list_filter = ("is_published",)
    search_fields = ("title", "excerpt", "content")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    readonly_fields = ("preview",)
    fields = ("title", "slug", "image", "preview", "excerpt", "content", "is_published", "published_at")

    @admin.display(description="Picture")
    def preview(self, obj):
        return _thumb(obj.image)


@admin.register(StaffMember)
class StaffMemberAdmin(ModelAdmin):
    list_display = ("preview", "name", "role", "sort_order", "is_active")
    list_display_links = ("preview", "name")
    list_editable = ("sort_order", "is_active")
    readonly_fields = ("preview",)
    fields = ("name", "role", "photo", "preview", "bio", "sort_order", "is_active")

    @admin.display(description="Photo")
    def preview(self, obj):
        return _thumb(obj.photo)


# Users and Groups, restyled with the same theme
admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass