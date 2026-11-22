
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


# ==========================================================
# AMENITIES
# ==========================================================

class Amenity(models.Model):
    name = models.CharField(max_length=100, unique=True)

    icon = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="FontAwesome icon class"
    )

    class Meta:
        verbose_name_plural = "Amenities"
        ordering = ["name"]

    def __str__(self):
        return self.name


# ==========================================================
# PROPERTY
# ==========================================================

class Property(models.Model):

    CATEGORY_CHOICES = [
        ("bedsitter", "Bedsitter"),
        ("single_room", "Single Room"),
        ("studio", "Studio Apartment"),
        ("one_bedroom", "One Bedroom"),
        ("two_bedroom", "Two Bedroom"),
        ("three_bedroom", "Three Bedroom"),
        ("apartment", "Apartment"),
        ("maisonette", "Maisonette"),
        ("villa", "Villa"),
        ("bungalow", "Bungalow"),
        ("hostel", "Hostel"),
        ("office", "Office"),
        ("shop", "Shop"),
        ("warehouse", "Warehouse"),
        ("commercial", "Commercial Property"),
        ("land", "Land"),
        ("holiday_home", "Holiday Home"),
    ]

    STATUS_CHOICES = [
        ("available", "Available"),
        ("occupied", "Occupied"),
        ("booked", "Booked"),
        ("pending", "Pending Approval"),
        ("renovation", "Under Renovation"),
    ]

    # Basic information
    title = models.CharField(max_length=200)
    description = models.TextField()

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )

    property_type = models.CharField(
        max_length=50,
        default="Rental"
    )

    # Pricing
    monthly_rent = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    deposit = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    service_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    # Property specifications
    bedrooms = models.IntegerField(default=0)
    bathrooms = models.IntegerField(default=0)

    square_footage = models.IntegerField(
        blank=True,
        null=True
    )

    floor_number = models.IntegerField(default=0)

    # Location
    county = models.CharField(max_length=100)
    town = models.CharField(max_length=100)
    estate = models.CharField(max_length=100)
    address = models.CharField(max_length=255)

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )

    # Relationships
    amenities = models.ManyToManyField(
        Amenity,
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="properties"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    # Video
    video_url = models.URLField(
        blank=True,
        null=True,
        help_text="YouTube or external video tour URL"
    )

    # House rules
    house_rules = models.TextField(
        blank=True,
        null=True,
        help_text="No pets, late gate entry guidelines, etc."
    )

    # Nearby facilities
    nearby_schools = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    nearby_hospitals = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    nearby_shopping = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    nearby_bus_stops = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    date_posted = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Properties"
        ordering = ["-date_posted"]

    def __str__(self):
        return f"{self.title} - {self.town} ({self.get_status_display()})"

    @property
    def property_id(self):
        return f"NL-{self.id:05d}" if self.id else "NL-PENDING"

    @property
    def default_image_url(self):
        category_fallbacks = {
            "bedsitter": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&q=80&w=800",
            "single_room": "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?auto=format&fit=crop&q=80&w=800",
            "studio": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&q=80&w=800",
            "one_bedroom": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&q=80&w=800",
            "two_bedroom": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&q=80&w=800",
            "three_bedroom": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&q=80&w=800",
            "apartment": "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&q=80&w=800",
            "villa": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&q=80&w=800",
            "maisonette": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&q=80&w=800",
            "bungalow": "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&q=80&w=800",
        }
        return category_fallbacks.get(self.category, "https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&q=80&w=800")

    @property
    def display_image_url(self):
        feat = self.images.filter(is_featured=True).first() or self.images.first()
        if feat and feat.image:
            try:
                return feat.image.url
            except Exception:
                pass
        return self.default_image_url


# ==========================================================
# PROPERTY IMAGES
# ==========================================================

class PropertyImage(models.Model):

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(
        upload_to="property_images/"
    )

    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.property.title}"


# ==========================================================
# BOOKINGS
# ==========================================================

class Booking(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending Confirmation"),
        ("confirmed", "Confirmed"),
        ("declined", "Declined"),
        ("cancelled", "Cancelled"),
    ]

    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    date = models.DateField()
    time = models.TimeField()

    message = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-time"]

    def __str__(self):
        return f"Booking by {self.tenant.username} for {self.property.title}"


# ==========================================================
# APPLICATIONS
# ==========================================================

class Application(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending Approval"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]

    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    message = models.TextField(
        blank=True,
        null=True,
        help_text="Why do you want to rent this property?"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Application by {self.tenant.username} for {self.property.title}"


# ==========================================================
# REVIEWS
# ==========================================================

class Review(models.Model):

    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    text = models.TextField()

    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"Review by {self.tenant.username} for {self.property.title} - {self.rating} stars"


# ==========================================================
# FAVORITES
# ==========================================================

class Favorite(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites"
    )

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="favorites"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "property")

    def __str__(self):
        return f"{self.user.username} saved {self.property.title}"


# ==========================================================
# PAYMENTS
# ==========================================================

class Payment(models.Model):

    PAYMENT_TYPES = [
        ("rent_deposit", "Rent Deposit & Move-In"),
        ("viewing_fee", "House Viewing Fee"),
        ("service_charge", "Service Charge"),
        ("landlord_verification", "Landlord Verification Fee"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending M-PESA Confirmation"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    property = models.ForeignKey(
        Property,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    phone_number = models.CharField(max_length=20)

    mpesa_code = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    till_number = models.CharField(
        max_length=20,
        default="5927622"
    )

    payment_type = models.CharField(
        max_length=50,
        choices=PAYMENT_TYPES,
        default="rent_deposit"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="completed"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"M-PESA KES {self.amount} by {self.user.username} (Till {self.till_number})"
