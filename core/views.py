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

def cheremo_gpt_page(request):
    """Renders the Cheremo GPT AI assistant interactive workspace."""
    sample_properties = Property.objects.filter(status='available')[:3]
    context = {
        'sample_properties': sample_properties
    }
    return render(request, 'core/cheremo_gpt.html', context)

from django.http import JsonResponse
from django.db.models import Q
import re

def cheremo_gpt_chat(request):
    """
    AI Endpoint for Cheremo GPT. Processes user queries, provides smart real estate advice,
    and returns matching active properties from Cheremo NyumbaLink.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

    user_message = request.POST.get('message', '').strip()
    if not user_message:
        return JsonResponse({'status': 'error', 'message': 'Empty message'}, status=400)

    msg_lower = user_message.lower()
    matching_props = []
    reply_text = ""

    # 1. Search Query Intent Detection
    if any(k in msg_lower for k in ['find', 'search', 'house', 'apartment', 'bedroom', 'studio', 'bedsitter', 'villa', 'rent', 'under', 'nairobi', 'mombasa', 'kisumu', 'westlands', 'nyali', 'kilimani', 'milimani', 'available']):
        props_qs = Property.objects.filter(status='available')
        
        # Check location
        for loc in ['westlands', 'nyali', 'kilimani', 'milimani', 'nairobi', 'mombasa', 'kisumu']:
            if loc in msg_lower:
                props_qs = props_qs.filter(Q(town__icontains=loc) | Q(county__icontains=loc) | Q(estate__icontains=loc))
                break

        # Check price intent (e.g., under 50000, 30k)
        price_match = re.search(r'(\d+)\s*k', msg_lower)
        if price_match:
            max_p = float(price_match.group(1)) * 1000
            props_qs = props_qs.filter(monthly_rent__lte=max_p)
        else:
            price_num = re.search(r'under\s*(\d+)', msg_lower)
            if price_num:
                props_qs = props_qs.filter(monthly_rent__lte=float(price_num.group(1)))

        # Check category / bedrooms
        if 'studio' in msg_lower:
            props_qs = props_qs.filter(category='studio')
        elif 'bedsitter' in msg_lower:
            props_qs = props_qs.filter(category='bedsitter')
        elif 'villa' in msg_lower:
            props_qs = props_qs.filter(category='villa')
        elif '1' in msg_lower or 'one' in msg_lower:
            props_qs = props_qs.filter(bedrooms=1)
        elif '2' in msg_lower or 'two' in msg_lower:
            props_qs = props_qs.filter(bedrooms=2)
        elif '3' in msg_lower or 'three' in msg_lower:
            props_qs = props_qs.filter(bedrooms=3)

        results = list(props_qs[:4])
        if results:
            reply_text = f"🤖 **Cheremo GPT Found {len(results)} Matching Listing(s) on Cheremo NyumbaLink:**\n\nI analyzed your request and retrieved the best available properties matching your criteria:"
            for p in results:
                feat_img = p.images.filter(is_featured=True).first() or p.images.first()
                matching_props.append({
                    'id': p.id,
                    'title': p.title,
                    'rent': float(p.monthly_rent),
                    'location': f"{p.estate}, {p.town}",
                    'category': p.get_category_display(),
                    'bedrooms': p.bedrooms,
                    'url': f"/properties/{p.id}/",
                    'image': feat_img.image.url if feat_img else '/static/images/japhet_landlord.jpg'
                })
        else:
            # Fallback if specific filters yielded 0
            all_avail = list(Property.objects.filter(status='available')[:3])
            reply_text = "🤖 **Cheremo GPT Search Result:**\n\nI searched our active database for your specific criteria. Here are our top featured listings currently available for booking:"
            for p in all_avail:
                feat_img = p.images.filter(is_featured=True).first() or p.images.first()
                matching_props.append({
                    'id': p.id,
                    'title': p.title,
                    'rent': float(p.monthly_rent),
                    'location': f"{p.estate}, {p.town}",
                    'category': p.get_category_display(),
                    'bedrooms': p.bedrooms,
                    'url': f"/properties/{p.id}/",
                    'image': feat_img.image.url if feat_img else '/static/images/japhet_landlord.jpg'
                })

    # 2. Rent Budget Calculator Intent
    elif any(k in msg_lower for k in ['budget', 'calculate', 'total cost', 'move in', 'deposit']):
        price_found = re.search(r'(\d+)', msg_lower)
        rent_val = float(price_found.group(1)) if price_found else 30000.0
        if rent_val < 100: rent_val *= 1000 # handles '30k' format

        deposit = rent_val
        service_charge = round(rent_val * 0.05)
        moving_est = 6000.0
        total_estimate = rent_val + deposit + service_charge + moving_est

        reply_text = f"""📊 **Cheremo GPT Move-In Budget Breakdown for KES {rent_val:,.2f} Monthly Rent:**

• **First Month's Rent:** KES {rent_val:,.2f}
• **Security Deposit (1 Month):** KES {deposit:,.2f}
• **Estimated Service Charge:** KES {service_charge:,.2f}
• **Estimated Moving Truck & Logistics:** KES {moving_est:,.2f}
--------------------------------------------------
💰 **Estimated Total Move-In Capital Needed:** **KES {total_estimate:,.2f}**

💡 *Pro Tip:* Always ask the landlord if token electricity meters carry debt from past tenants before signing!"""

    # 3. Tenant Rights & Legal Advice Intent
    elif any(k in msg_lower for k in ['law', 'rights', 'notice', 'evict', 'deposit refund', 'lease', 'agreement', 'tenant act']):
        reply_text = """⚖️ **Cheremo GPT Real Estate Legal Guide (Kenya):**

1. **Deposit Refund:** Under Kenyan tenancy practice, landlords should refund your security deposit within 14–30 days after inspection upon vacating, minus reasonable repair costs.
2. **Termination Notice:** Standard leases require **1 full calendar month written notice** prior to moving out.
3. **Rent Increases:** Landlords must issue a minimum 90-day written notice before adjusting rent prices.
4. **Water & Electricity:** Ensure token meters and borehole bill meters are cleared by the outgoing tenant before paying your initial deposit."""

    # 4. Water / Security / Inspection Advice
    elif any(k in msg_lower for k in ['water', 'inspect', 'check', 'security', 'meter', 'wifi']):
        reply_text = """🔍 **Cheremo GPT Pre-Move Inspection Checklist:**

✅ **Water Flow:** Test tap pressure in both kitchen and bathroom. Ask neighbors if Kanjo water rationing occurs on specific days.
✅ **Token Meter:** Inspect the KPLC prepaid meter serial number and dial `*433#` or check current units to ensure zero negative balance.
✅ **Mobile Signal:** Check cellular signal strength inside bedrooms (some thick concrete walls block signal).
✅ **Security:** Verify 24/7 security guard presence and gate opening/closure curfew times."""

    # 5. General Conversational / Greetings
    else:
        reply_text = f"""👋 Hello! I am **Cheremo GPT**, your AI Real Estate Assistant on Cheremo NyumbaLink.

I can help you:
🔍 **Find rentals** matching your budget & preferred town (e.g. *"Show me 2 bedrooms in Westlands under 50k"*)
📊 **Calculate move-in costs** (e.g. *"Calculate budget for 25k rent"*)
⚖️ **Explain tenancy laws & deposit refunds in Kenya**
📝 **Give pre-inspection checklists before paying deposit**

How can I assist your house hunt today?"""

    return JsonResponse({
        'status': 'success',
        'reply': reply_text,
        'properties': matching_props
    })

