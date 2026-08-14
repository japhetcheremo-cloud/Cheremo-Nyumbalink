from django.contrib import admin
from .models import Amenity, Property, PropertyImage, Booking, Application, Review, Favorite, Payment


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ('image', 'is_featured')


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name',)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'county', 'town', 'monthly_rent', 'status', 'created_by', 'date_posted')
    list_filter = ('status', 'category', 'county')
    search_fields = ('title', 'description', 'town', 'estate', 'county')
    list_editable = ('status',)
    ordering = ('-date_posted',)
    readonly_fields = ('date_posted',)
    inlines = [PropertyImageInline]
    filter_horizontal = ('amenities',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'property_type', 'status', 'created_by')
        }),
        ('Pricing', {
            'fields': ('monthly_rent', 'deposit', 'service_charge')
        }),
        ('Property Details', {
            'fields': ('bedrooms', 'bathrooms', 'square_footage', 'floor_number')
        }),
        ('Location', {
            'fields': ('county', 'town', 'estate', 'address', 'latitude', 'longitude')
        }),
        ('Extras', {
            'fields': ('amenities', 'video_url', 'house_rules'),
            'classes': ('collapse',)
        }),
        ('Nearby Places', {
            'fields': ('nearby_schools', 'nearby_hospitals', 'nearby_shopping', 'nearby_bus_stops'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'is_featured')
    list_filter = ('is_featured',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'property', 'date', 'time', 'status', 'created_at')
    list_filter = ('status', 'date')
    search_fields = ('tenant__username', 'property__title')
    list_editable = ('status',)
    ordering = ('-created_at',)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'property', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('tenant__username', 'property__title')
    list_editable = ('status',)
    ordering = ('-created_at',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'property', 'rating', 'date')
    list_filter = ('rating',)
    search_fields = ('tenant__username', 'property__title', 'text')
    ordering = ('-date',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'property', 'created_at')
    search_fields = ('user__username', 'property__title')
    ordering = ('-created_at',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'till_number', 'amount', 'mpesa_code', 'payment_type', 'status', 'created_at')
    list_filter = ('status', 'payment_type', 'till_number', 'created_at')
    search_fields = ('user__username', 'phone_number', 'mpesa_code', 'till_number')
    ordering = ('-created_at',)

