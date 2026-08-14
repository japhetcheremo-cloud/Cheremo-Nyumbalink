from django.shortcuts import render, redirect, get_object_or_404
from properties.models import Property, Amenity
from .models import BlogPost
from django.contrib import messages
from users.models import CustomUser

def home(request):
    featured_properties = Property.objects.filter(status='available')[:6]
    latest_properties = Property.objects.filter(status='available').order_by('-date_posted')[:3]
    blogs = BlogPost.objects.all()[:3]
    
    # Platform stats
    stats = {
        'total_listings': Property.objects.count() + 120, # start with nice stats base
        'happy_tenants': 850,
        'verified_landlords': CustomUser.objects.filter(role='landlord', is_verified=True).count() + 45,
        'cities_covered': 8
    }

    context = {
        'featured_properties': featured_properties,
        'latest_properties': latest_properties,
        'blogs': blogs,
        'stats': stats,
        'categories': Property.CATEGORY_CHOICES
    }
    return render(request, 'core/home.html', context)

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        
        # In a real app we'd save to a ContactMessage model or send an email.
        # For now, show a toast success message.
        messages.success(request, f"Thank you, {name}! Your message has been sent successfully. We will get back to you shortly.")
        return redirect('contact')
        
    return render(request, 'core/contact.html')

def faq(request):
    return render(request, 'core/faq.html')

def blog_list(request):
    blogs = BlogPost.objects.all()
    context = {
        'blogs': blogs
    }
    return render(request, 'core/blog_list.html', context)

def blog_detail(request, slug):
    blog = get_object_or_404(BlogPost, slug=slug)
    context = {
        'blog': blog
    }
    return render(request, 'core/blog_detail.html', context)

def terms(request):
    return render(request, 'core/terms.html')

def privacy(request):
    return render(request, 'core/privacy.html')

def cookies(request):
    return render(request, 'core/cookies.html')
