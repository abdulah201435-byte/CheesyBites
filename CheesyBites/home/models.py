from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify

PURGE_AFTER = timedelta(days=5)


class Review(models.Model):
    name = models.CharField(max_length=60)
    email = models.EmailField(max_length=120)  # private: never sent to the website
    text = models.TextField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def word_count(self):
        return len(self.text.split())

    def __str__(self):
        return f"{self.name}: {self.text[:40]}"


class MenuItems(models.Model):
    name = models.CharField("dish name", max_length=60)
    category = models.CharField(max_length=120, help_text="Dishes with the same category are grouped together, e.g. Pizza, Burgers")
    size = models.CharField(max_length=50, blank=True, null=True,
                            help_text="e.g. Small, Medium, Large. For a dish with several sizes, add one row per size with the same dish name and category.")
    price = models.DecimalField("price (Rs.)", max_digits=8, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    picture = models.ImageField(upload_to="menu_pictures/", null=True, blank=True)

    class Meta:
        ordering = ["category", "name", "price"]
        verbose_name = "menu item"
        verbose_name_plural = "menu items"

    def __str__(self):
        return f"{self.name} ({self.category}) - Rs. {self.price}"


class Offer(models.Model):
    offer_name = models.CharField("deal name", max_length=100)
    offer_picture = models.ImageField("deal picture", upload_to="offer_pictures/", null=True, blank=True)
    is_available = models.BooleanField("available", default=True,
                                       help_text="Untick to mark Not Available. The offer is deleted automatically 5 days later.")
    old_price = models.DecimalField("old price (Rs.)", max_digits=8, decimal_places=2, null=True, blank=True)
    new_price = models.DecimalField("new price (Rs.)", max_digits=8, decimal_places=2)
    start_date = models.DateTimeField("available from")
    end_date = models.DateTimeField("available until")
    unavailable_since = models.DateTimeField(null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.offer_name} (Rs. {self.new_price})"

    def clean(self):
        if self.old_price is not None and self.new_price is not None and self.new_price >= self.old_price:
            raise ValidationError({"new_price": "The new price must be lower than the old price."})
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError({"end_date": "The end must be after the start."})

    def save(self, *args, **kwargs):
        if self.is_available:
            self.unavailable_since = None
        elif not self.unavailable_since:
            self.unavailable_since = timezone.now()
        super().save(*args, **kwargs)

    @property
    def status(self):
        now = timezone.now()
        if not self.is_available:
            return "unavailable"
        if now < self.start_date:
            return "upcoming"
        if now > self.end_date:
            return "expired"
        return "active"

    @property
    def delete_on(self):
        """When this offer will be deleted automatically."""
        if not self.is_available and self.unavailable_since:
            return self.unavailable_since + PURGE_AFTER
        return self.end_date + PURGE_AFTER

    @classmethod
    def purge_old(cls):
        """Delete offers that ended, or were marked Not Available, more than 5 days ago."""
        cutoff = timezone.now() - PURGE_AFTER
        count = 0
        for offer in cls.objects.filter(models.Q(end_date__lt=cutoff) | models.Q(unavailable_since__lt=cutoff)):
            offer.delete()
            count += 1
        return count


class OfferItem(models.Model):
    """One line of 'what the deal contains': item name, how many, which size."""
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="items")
    name = models.CharField("item name", max_length=80)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    size = models.CharField(max_length=40, blank=True, help_text="e.g. Small, Large, 1.5L (optional)")

    class Meta:
        ordering = ["id"]
        verbose_name = "item in this deal"
        verbose_name_plural = "items in this deal"

    def __str__(self):
        return f"{self.quantity} x {self.name} {self.size}".strip()


class OfferImage(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField("more pictures", upload_to="offer_pictures/more/")

    class Meta:
        ordering = ["id"]
        verbose_name = "extra picture"
        verbose_name_plural = "extra pictures"

    def __str__(self):
        return f"Picture for {self.offer.offer_name}"


@receiver(post_delete, sender=OfferImage)
def remove_offer_extra_picture(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)


@receiver(post_delete, sender=MenuItems)
def remove_menu_picture(sender, instance, **kwargs):
    if instance.picture:
        instance.picture.delete(save=False)


@receiver(post_delete, sender=Offer)
def remove_offer_picture(sender, instance, **kwargs):
    if instance.offer_picture:
        instance.offer_picture.delete(save=False)


class ContactMessage(models.Model):
    """Messages from the Contact Us form. Only the owner sees them, in the admin panel."""
    name = models.CharField(max_length=60)
    email = models.EmailField(max_length=120)
    subject = models.CharField(max_length=100)
    message = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_read = models.BooleanField("read", default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "contact message"

    def __str__(self):
        return f"{self.subject} - {self.name}"


class StoryPage(models.Model):
    """The text and picture at the top of the Our Story section (only one of these exists)."""
    intro = models.TextField("introduction", blank=True)
    mission = models.TextField("our mission", blank=True)
    food_quality = models.TextField("food quality", blank=True)
    picture = models.ImageField(upload_to="story/", null=True, blank=True)

    class Meta:
        verbose_name = "Our Story page"
        verbose_name_plural = "Our Story page"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return "Our Story page"


class StoryPost(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    image = models.ImageField("featured picture", upload_to="story/", null=True, blank=True)
    excerpt = models.CharField("short summary", max_length=250, blank=True)
    content = models.TextField("full story")
    is_published = models.BooleanField("published", default=True, help_text="Untick to keep it hidden (draft)")
    published_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-published_at"]
        verbose_name = "story post"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "story"
            slug, n = base, 2
            while StoryPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f"{base}-{n}", n + 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class StaffMember(models.Model):
    name = models.CharField(max_length=80)
    role = models.CharField(max_length=80, blank=True)
    photo = models.ImageField(upload_to="staff/", null=True, blank=True)
    bio = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0, help_text="Smaller numbers show first")
    is_active = models.BooleanField("show on website", default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "team member"

    def __str__(self):
        return self.name


def _delete_file(field):
    def handler(sender, instance, **kwargs):
        f = getattr(instance, field)
        if f:
            f.delete(save=False)
    return handler


for _model, _field in ((StoryPage, "picture"), (StoryPost, "image"), (StaffMember, "photo")):
    post_delete.connect(_delete_file(_field), sender=_model, weak=False)