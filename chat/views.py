from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from .models import Message
from users.models import CustomUser

@login_required
def inbox(request):
    # Fetch all messages involving the logged-in user
    all_msgs = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).order_by('-timestamp')
    
    # Get distinct list of conversation partners with their last message
    conversations = []
    seen_users = set()
    
    for msg in all_msgs:
        partner = msg.recipient if msg.sender == request.user else msg.sender
        if partner.id not in seen_users:
            seen_users.add(partner.id)
            # Count unread messages from this partner
            unread_count = Message.objects.filter(
                sender=partner,
                recipient=request.user,
                is_read=False
            ).count()
            
            conversations.append({
                'partner': partner,
                'last_message': msg,
                'unread_count': unread_count
            })
            
    context = {
        'conversations': conversations
    }
    return render(request, 'chat/inbox.html', context)

@login_required
def chat_thread(request, user_id):
    partner = get_object_or_404(CustomUser, pk=user_id)
    
    # Mark messages from partner as read
    Message.objects.filter(
        sender=partner,
        recipient=request.user,
        is_read=False
    ).update(is_read=True)
    
    # Fetch all messages between user and partner
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(recipient=partner)) |
        (Q(sender=partner) & Q(recipient=request.user))
    ).order_by('timestamp')
    
    context = {
        'partner': partner,
        'chat_messages': messages
    }
    return render(request, 'chat/chat_thread.html', context)

@login_required
def send_message(request):
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        content = request.POST.get('content')
        
        if not recipient_id or not content:
            return JsonResponse({'status': 'error', 'message': 'Missing fields'}, status=400)
            
        recipient = get_object_or_404(CustomUser, pk=recipient_id)
        msg = Message.objects.create(
            sender=request.user,
            recipient=recipient,
            content=content
        )
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
            return JsonResponse({
                'status': 'success',
                'message': {
                    'id': msg.id,
                    'content': msg.content,
                    'timestamp': msg.timestamp.strftime('%I:%M %p'),
                    'sender_id': msg.sender.id,
                }
            })
        
        return redirect('chat_thread', user_id=recipient_id)
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def get_messages(request, user_id):
    partner = get_object_or_404(CustomUser, pk=user_id)
    
    # Fetch unread messages from partner
    unread_messages = Message.objects.filter(
        sender=partner,
        recipient=request.user,
        is_read=False
    ).order_by('timestamp')
    
    messages_data = []
    for msg in unread_messages:
        messages_data.append({
            'id': msg.id,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%I:%M %p'),
            'sender_id': msg.sender.id,
        })
        
    # Mark them as read now
    unread_messages.update(is_read=True)
    
    return JsonResponse({'status': 'success', 'messages': messages_data})
