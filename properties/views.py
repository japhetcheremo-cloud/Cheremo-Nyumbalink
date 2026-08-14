from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Property, Amenity, PropertyImage, Booking, Application, Favorite, Review
from users.models import CustomUser

def property_list(request):
    properties = Property.objects.filter(status='available')
    
    # Text search
    q = request.GET.get('q')
    if q:
        properties = properties.filter(
            Q(title__icontains=q) | 
            Q(description__icontains=q) |
            Q(town__icontains=q) |
            Q(estate__icontains=q)
        )
        
    # Filters
    county = request.GET.get('county')
    if county:
        properties = properties.filter(county__iexact=county)
        
    town = request.GET.get('town')
    if town:
        properties = properties.filter(town__icontains=town)
        
    estate = request.GET.get('estate')
    if estate:
        properties = properties.filter(estate__icontains=estate)
        
    category = request.GET.get('category')
    if category:
        properties = properties.filter(category=category)
        
    min_price = request.GET.get('min_price')
    if min_price:
        properties = properties.filter(monthly_rent__gte=min_price)
        
    max_price = request.GET.get('max_price')
    if max_price:
        properties = properties.filter(monthly_rent__lte=max_price)
        
    bedrooms = request.GET.get('bedrooms')
    if bedrooms and bedrooms != 'any':
        properties = properties.filter(bedrooms=bedrooms)
        
    bathrooms = request.GET.get('bathrooms')
    if bathrooms and bathrooms != 'any':
        properties = properties.filter(bathrooms=bathrooms)

    # Filtering by multiple amenities
    selected_amenities = request.GET.getlist('amenities')
    for amenity_id in selected_amenities:
        properties = properties.filter(amenities__id=amenity_id)

    amenities = Amenity.objects.all()
    
    context = {
        'properties': properties,
        'amenities': amenities,
        'categories': Property.CATEGORY_CHOICES,
        'params': request.GET
    }
    return render(request, 'properties/property_list.html', context)

def property_detail(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    
    # Check favorite status
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, property=property_obj).exists()
        
    reviews = Review.objects.filter(property=property_obj)
    
    # Calculate average rating
    rating_avg = 0
    if reviews.exists():
        rating_avg = sum([r.rating for r in reviews]) / reviews.count()
        
    context = {
        'property': property_obj,
        'is_favorite': is_favorite,
        'reviews': reviews,
        'rating_avg': round(rating_avg, 1)
    }
    return render(request, 'properties/property_detail.html', context)

@login_required
def property_create(request):
    if request.user.role not in [CustomUser.ROLE_LANDLORD, CustomUser.ROLE_AGENT, CustomUser.ROLE_ADMIN]:
        messages.error(request, "Only landlords and agents can list properties.")
        return redirect('dashboard_redirect')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        monthly_rent = request.POST.get('monthly_rent')
        deposit = request.POST.get('deposit')
        service_charge = request.POST.get('service_charge', 0.00)
        bedrooms = request.POST.get('bedrooms', 0)
        bathrooms = request.POST.get('bathrooms', 0)
        square_footage = request.POST.get('square_footage')
        floor_number = request.POST.get('floor_number', 0)
        county = request.POST.get('county')
        town = request.POST.get('town')
        estate = request.POST.get('estate')
        address = request.POST.get('address')
        video_url = request.POST.get('video_url', '')
        house_rules = request.POST.get('house_rules', '')
        nearby_schools = request.POST.get('nearby_schools', '')
        nearby_hospitals = request.POST.get('nearby_hospitals', '')
        nearby_shopping = request.POST.get('nearby_shopping', '')
        nearby_bus_stops = request.POST.get('nearby_bus_stops', '')
        
        # Latitude and longitude mocks
        latitude = request.POST.get('latitude') or -1.2921
        longitude = request.POST.get('longitude') or 36.8219
        
        property_obj = Property.objects.create(
            title=title,
            description=description,
            category=category,
            monthly_rent=monthly_rent,
            deposit=deposit,
            service_charge=service_charge,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            square_footage=square_footage if square_footage else None,
            floor_number=floor_number,
            county=county,
            town=town,
            estate=estate,
            address=address,
            video_url=video_url,
            house_rules=house_rules,
            nearby_schools=nearby_schools,
            nearby_hospitals=nearby_hospitals,
            nearby_shopping=nearby_shopping,
            nearby_bus_stops=nearby_bus_stops,
            latitude=latitude,
            longitude=longitude,
            created_by=request.user,
            status='pending' # needs admin approval first
        )
        
        # Amenities
        amenity_ids = request.POST.getlist('amenities')
        property_obj.amenities.set(amenity_ids)
        
        # Multi-image uploads
        images = request.FILES.getlist('images')
        for index, img in enumerate(images):
            PropertyImage.objects.create(
                property=property_obj,
                image=img,
                is_featured=(index == 0) # set first image as featured
            )
            
        messages.success(request, "Property listed successfully! It will appear on search results after admin approval.")
        return redirect('landlord_dashboard')
        
    amenities = Amenity.objects.all()
    context = {
        'amenities': amenities,
        'categories': Property.CATEGORY_CHOICES
    }
    return render(request, 'properties/property_form.html', context)

@login_required
def property_update(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    if property_obj.created_by != request.user and not request.user.is_superuser:
        messages.error(request, "You are not authorized to edit this property.")
        return redirect('dashboard_redirect')
        
    if request.method == 'POST':
        property_obj.title = request.POST.get('title')
        property_obj.description = request.POST.get('description')
        property_obj.category = request.POST.get('category')
        property_obj.monthly_rent = request.POST.get('monthly_rent')
        property_obj.deposit = request.POST.get('deposit')
        property_obj.service_charge = request.POST.get('service_charge', 0.00)
        property_obj.bedrooms = request.POST.get('bedrooms', 0)
        property_obj.bathrooms = request.POST.get('bathrooms', 0)
        
        square_footage = request.POST.get('square_footage')
        property_obj.square_footage = square_footage if square_footage else None
        
        property_obj.floor_number = request.POST.get('floor_number', 0)
        property_obj.county = request.POST.get('county')
        property_obj.town = request.POST.get('town')
        property_obj.estate = request.POST.get('estate')
        property_obj.address = request.POST.get('address')
        property_obj.video_url = request.POST.get('video_url', '')
        property_obj.house_rules = request.POST.get('house_rules', '')
        property_obj.nearby_schools = request.POST.get('nearby_schools', '')
        property_obj.nearby_hospitals = request.POST.get('nearby_hospitals', '')
        property_obj.nearby_shopping = request.POST.get('nearby_shopping', '')
        property_obj.nearby_bus_stops = request.POST.get('nearby_bus_stops', '')
        
        # update status if landlord toggled availability
        status = request.POST.get('status')
        if status:
            property_obj.status = status
            
        property_obj.save()
        
        # update amenities
        amenity_ids = request.POST.getlist('amenities')
        property_obj.amenities.set(amenity_ids)
        
        # optional new images
        images = request.FILES.getlist('images')
        if images:
            # clear existing featured flag if new images uploaded
            for img in images:
                PropertyImage.objects.create(
                    property=property_obj,
                    image=img,
                    is_featured=False
                )
                
        messages.success(request, "Property updated successfully.")
        return redirect('landlord_dashboard')
        
    amenities = Amenity.objects.all()
    context = {
        'property': property_obj,
        'amenities': amenities,
        'categories': Property.CATEGORY_CHOICES
    }
    return render(request, 'properties/property_form.html', context)

@login_required
def property_delete(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    if property_obj.created_by != request.user and not request.user.is_superuser:
        messages.error(request, "You are not authorized to delete this property.")
        return redirect('dashboard_redirect')
        
    if request.method == 'POST':
        property_obj.delete()
        messages.success(request, "Property deleted successfully.")
        return redirect('landlord_dashboard')
        
    return render(request, 'properties/property_confirm_delete.html', {'property': property_obj})

@login_required
def book_viewing(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        date = request.POST.get('date')
        time = request.POST.get('time')
        message = request.POST.get('message')
        
        Booking.objects.create(
            tenant=request.user,
            property=property_obj,
            date=date,
            time=time,
            message=message
        )
        
        messages.success(request, "Viewing booked successfully! Awaiting landlord confirmation.")
        return redirect('tenant_dashboard')
        
    return redirect('property_detail', pk=pk)

@login_required
def apply_rental(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        message = request.POST.get('message')
        
        # Check if already applied
        if Application.objects.filter(tenant=request.user, property=property_obj).exists():
            messages.warning(request, "You have already applied for this property.")
        else:
            Application.objects.create(
                tenant=request.user,
                property=property_obj,
                message=message
            )
            messages.success(request, "Application submitted successfully! Landlord will review your application.")
            
        return redirect('tenant_dashboard')
        
    return redirect('property_detail', pk=pk)

@login_required
def toggle_favorite(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    favorite, created = Favorite.objects.get_or_create(user=request.user, property=property_obj)
    if not created:
        favorite.delete()
        messages.success(request, f"{property_obj.title} removed from favorites.")
    else:
        messages.success(request, f"{property_obj.title} added to favorites.")
        
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('property_detail', pk=pk)

@login_required
def add_review(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        text = request.POST.get('text')
        
        Review.objects.create(
            tenant=request.user,
            property=property_obj,
            rating=rating,
            text=text
        )
        messages.success(request, "Review submitted successfully.")
        
    return redirect('property_detail', pk=pk)

@login_required
def approve_property(request, pk):
    if not request.user.is_superuser and request.user.role != CustomUser.ROLE_ADMIN:
        messages.error(request, "Unauthorized operation.")
        return redirect('dashboard_redirect')
        
    property_obj = get_object_or_404(Property, pk=pk)
    property_obj.status = 'available'
    property_obj.save()
    
    messages.success(request, f"Property '{property_obj.title}' approved successfully.")
    return redirect('admin_dashboard')

@login_required
def verify_user(request, pk):
    if not request.user.is_superuser and request.user.role != CustomUser.ROLE_ADMIN:
        messages.error(request, "Unauthorized operation.")
        return redirect('dashboard_redirect')
        
    user = get_object_or_404(CustomUser, pk=pk)
    user.is_verified = True
    user.save()
    
    messages.success(request, f"User '{user.username}' verified successfully.")
    return redirect('admin_dashboard')

@login_required
def manage_booking(request, pk, status):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.property.created_by != request.user and not request.user.is_superuser:
        messages.error(request, "Unauthorized operation.")
        return redirect('dashboard_redirect')
        
    if status in ['confirmed', 'declined', 'cancelled']:
        booking.status = status
        booking.save()
        messages.success(request, f"Booking status updated to {status}.")
        
    return redirect('landlord_dashboard')

@login_required
def manage_application(request, pk, status):
    application = get_object_or_404(Application, pk=pk)
    if application.property.created_by != request.user and not request.user.is_superuser:
        messages.error(request, "Unauthorized operation.")
        return redirect('dashboard_redirect')
        
    if status in ['accepted', 'rejected']:
        application.status = status
        application.save()
        
        # update property status if accepted
        if status == 'accepted':
            application.property.status = 'occupied'
            application.property.save()
            
        messages.success(request, f"Application status updated to {status}.")
        
    return redirect('landlord_dashboard')
