from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
import json

from .models import Message, Thread


@login_required
def messages_page(request):
    threads_qs = (
        Thread.objects.filter(participants=request.user)
        .prefetch_related("participants", "messages")
        .distinct()
    )
    thread_cards = []
    thread_messages = {}
    for idx, thread in enumerate(threads_qs, start=1):
        other = thread.participants.exclude(id=request.user.id).first() or request.user
        msgs = list(thread.messages.all().order_by("created_at")[:30])
        last_msg = msgs[-1].body if msgs else "No messages yet"
        thread_cards.append(
            {
                "id": thread.id,
                "name": other.get_full_name() or other.username,
                "initials": other.initials,
                "color": "linear-gradient(135deg,#0D6E6E,#E8A830)" if idx % 2 else "linear-gradient(135deg,#E85D04,#E8A830)",
                "title": getattr(getattr(other, "freelancer_profile", None), "title", "Professional"),
                "lastMsg": last_msg,
                "time": "now",
                "unread": any(not m.is_read and m.sender_id != request.user.id for m in msgs),
                "profileUrl": f"/profile/{other.username}/",
            }
        )
        thread_messages[str(thread.id)] = [
            {
                "mine": m.sender_id == request.user.id,
                "text": m.body or "Attachment",
                "time": m.created_at.strftime("%I:%M %p"),
            }
            for m in msgs
        ]

    return render(
        request,
        "pages/messages.jinja",
        {
            "threads_json": json.dumps(thread_cards),
            "messages_json": json.dumps(thread_messages),
            "active_thread_id": thread_cards[0]["id"] if thread_cards else None,
        },
    )


@login_required
def thread_view(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id, participants=request.user)
    messages = thread.messages.all().order_by("created_at")
    return render(request, "partials/_message_bubble.jinja", {"messages": messages, "user": request.user})


@login_required
def send_message(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id, participants=request.user)
    body = request.POST.get("body", "").strip() or "Message sent"
    Message.objects.create(thread=thread, sender=request.user, body=body)
    return HttpResponse("<div class='text-sm text-green-300'>Message sent</div>")


@login_required
def mark_read(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id, participants=request.user)
    thread.messages.exclude(sender=request.user).update(is_read=True)
    return HttpResponse("<div class='text-sm text-[var(--text-muted)]'>Marked as read</div>")


@login_required
def start_thread(request, user_id):
    from users.models import User

    other = get_object_or_404(User, id=user_id)
    thread = Thread.objects.filter(participants=request.user).filter(participants=other).first()
    if not thread:
        thread = Thread.objects.create()
        thread.participants.add(request.user, other)
    return redirect("messages")


@login_required
def poll_thread(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id, participants=request.user)
    messages = thread.messages.all().order_by("-created_at")[:10]
    return render(request, "partials/_message_bubble.jinja", {"messages": list(reversed(messages)), "user": request.user})

