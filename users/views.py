from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.utils.crypto import get_random_string
from .models import CustomUser
from properties.models import Property, Booking, Application, Favorite, Review
from django.db.models import Sum

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        role = request.POST.get('role', 'tenant')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, 'users/register.html')
            
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, 'users/register.html')
            
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            phone=phone,
            first_name=first_name,
            last_name=last_name
        )
        
        messages.success(request, f"Welcome {user.username}! Your account has been created successfully.")
        login(request, user)
        return redirect('dashboard_redirect')
        
    return render(request, 'users/register.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('dashboard_redirect')
        else:
            messages.error(request, "Invalid username or password.")
            
    form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')

def google_login(request):
    """
    Handles Google account creation and sign in.
    Creates a new CustomUser account if it's the user's first time signing in with Google,
    or logs in the existing Google user and redirects to their dashboard.
    """
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    google_email = request.GET.get('email', 'japhet_google@gmail.com')
    google_username = google_email.split('@')[0]
    
    user = CustomUser.objects.filter(email=google_email).first()
    if not user:
        user = CustomUser.objects.filter(username=google_username).first()

    if not user:
        # Register new Google user
        user = CustomUser.objects.create_user(
            username=google_username,
            email=google_email,
            password=get_random_string(16),
            role=CustomUser.ROLE_TENANT,
            first_name='Google',
            last_name='Account',
            is_verified=True
        )
        messages.success(request, f"Welcome to Cheremo NyumbaLink! Account created via Google ({google_email}).")
    else:
        messages.success(request, f"Signed in with Google as {user.email}.")

    login(request, user)
    return redirect('dashboard_redirect')

@login_required
def dashboard_redirect(request):
    if request.user.role == CustomUser.ROLE_ADMIN or request.user.is_superuser:
        return redirect('admin_dashboard')
    elif request.user.role in [CustomUser.ROLE_LANDLORD, CustomUser.ROLE_AGENT]:
        return redirect('landlord_dashboard')
    else:
        return redirect('tenant_dashboard')

@login_required
def tenant_dashboard(request):
    if request.user.role not in [CustomUser.ROLE_TENANT, CustomUser.ROLE_ADMIN]:
        return redirect('dashboard_redirect')
        
    bookings = Booking.objects.filter(tenant=request.user)
    applications = Application.objects.filter(tenant=request.user)
    favorites = Favorite.objects.filter(user=request.user)
    reviews = Review.objects.filter(tenant=request.user)
    
    context = {
        'bookings': bookings,
        'applications': applications,
        'favorites': favorites,
        'reviews': reviews,
    }
    return render(request, 'users/tenant_dashboard.html', context)

@login_required
def landlord_dashboard(request):
    if request.user.role not in [CustomUser.ROLE_LANDLORD, CustomUser.ROLE_AGENT, CustomUser.ROLE_ADMIN] and not request.user.is_superuser:
        return redirect('dashboard_redirect')
        
    properties = Property.objects.filter(created_by=request.user)
    bookings = Booking.objects.filter(property__created_by=request.user)
    applications = Application.objects.filter(property__created_by=request.user)
    
    # Calculate revenue based on occupied properties
    revenue = Property.objects.filter(
        created_by=request.user, 
        status='occupied'
    ).aggregate(total=Sum('monthly_rent'))['total'] or 0.00
    
    # Quick metrics
    metrics = {
        'total_properties': properties.count(),
        'available_properties': properties.filter(status='available').count(),
        'pending_bookings': bookings.filter(status='pending').count(),
        'pending_applications': applications.filter(status='pending').count(),
        'revenue': revenue
    }
    
    context = {
        'properties': properties,
        'bookings': bookings[:5], # limit to recent bookings
        'all_bookings': bookings,
        'applications': applications[:5], # limit to recent applicants
        'all_applications': applications,
        'metrics': metrics
    }
    return render(request, 'users/landlord_dashboard.html', context)

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser and request.user.role != CustomUser.ROLE_ADMIN:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('dashboard_redirect')
        
    pending_properties = Property.objects.filter(status='pending')
    pending_verifications = CustomUser.objects.filter(
        role__in=[CustomUser.ROLE_LANDLORD, CustomUser.ROLE_AGENT], 
        is_verified=False
    ).exclude(verification_document='')
    
    all_users = CustomUser.objects.all()
    all_properties = Property.objects.all()
    
    # System statistics
    stats = {
        'total_users': all_users.count(),
        'total_properties': all_properties.count(),
        'pending_approvals': pending_properties.count(),
        'active_bookings': Booking.objects.filter(status='confirmed').count()
    }
    
    context = {
        'pending_properties': pending_properties,
        'pending_verifications': pending_verifications,
        'all_users': all_users,
        'all_properties': all_properties,
        'stats': stats
    }
    return render(request, 'users/admin_dashboard.html', context)

@login_required
def profile_settings(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.phone = request.POST.get('phone', '')
        user.bio = request.POST.get('bio', '')
        
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
            
        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('profile_settings')
        
    return render(request, 'users/profile_settings.html')

@login_required
def upload_verification(request):
    user = request.user
    if user.role not in [CustomUser.ROLE_LANDLORD, CustomUser.ROLE_AGENT]:
        messages.error(request, "Only landlords and agents can apply for verification.")
        return redirect('dashboard_redirect')
        
    if request.method == 'POST':
        if 'verification_document' in request.FILES:
            user.verification_document = request.FILES['verification_document']
            user.save()
            messages.success(request, "Verification document uploaded successfully. Our administration team will review it.")
        else:
            messages.error(request, "Please select a file to upload.")
            
        return redirect('dashboard_redirect')
        
    return render(request, 'users/upload_verification.html')
