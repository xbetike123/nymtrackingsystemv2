import csv
import io
import requests
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone

from tracking.models import Subscriber, Segment, SubscriberSegment

# === Upload Subscribers ===
def upload_subscribers_view(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('subscriber_csv')

        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, "Please upload a valid CSV file.")
            return redirect('upload_subscribers')

        decoded_file = csv_file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded_file))

        new_subscriber_count = 0
        new_segment_count = 0

        for row in reader:
            email = row.get('email', '').strip()
            name = row.get('name', '').strip()
            segments_raw = row.get('segment', '').strip()

            if email:
                subscriber, created = Subscriber.objects.get_or_create(email=email, defaults={'name': name})
                if created:
                    new_subscriber_count += 1

                if segments_raw:
                    segment_names = [s.strip() for s in segments_raw.split(',') if s.strip()]
                    for seg_name in segment_names:
                        segment, created_seg = Segment.objects.get_or_create(name=seg_name)
                        if created_seg:
                            new_segment_count += 1
                        SubscriberSegment.objects.get_or_create(subscriber=subscriber, segment=segment)

        messages.success(request, f"✅ {new_subscriber_count} subscriber(s) and {new_segment_count} new segment(s) created.")
        return redirect('upload_subscribers')

    return render(request, 'admin_views/upload_subscribers.html')


# === Assign Subscribers to Segment ===
def assign_segment_view(request):
    subscribers = Subscriber.objects.all()
    segments = Segment.objects.all()

    if request.method == 'POST':
        selected_subscriber_ids = request.POST.getlist('subscriber_ids')
        segment_id = request.POST.get('segment_id')

        if not segment_id or not selected_subscriber_ids:
            messages.error(request, "Please select both subscribers and a segment.")
            return redirect('assign_segment')

        segment = get_object_or_404(Segment, id=segment_id)
        count = 0

        for sid in selected_subscriber_ids:
            subscriber = get_object_or_404(Subscriber, id=sid)
            _, created = SubscriberSegment.objects.get_or_create(subscriber=subscriber, segment=segment)
            if created:
                count += 1

        messages.success(request, f"✅ {count} subscriber(s) assigned to '{segment.name}'.")
        return redirect('assign_segment')

    return render(request, 'admin_views/assign_segment.html', {
        'subscribers': subscribers,
        'segments': segments
    })


# === Create New Segment ===
def create_segment_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()

        if not name:
            messages.error(request, "Segment name is required.")
            return redirect('create_segment')

        if Segment.objects.filter(name__iexact=name).exists():
            messages.warning(request, "Segment already exists.")
            return redirect('create_segment')

        Segment.objects.create(name=name)
        messages.success(request, f"✅ Segment '{name}' created successfully.")
        return redirect('view_segments')

    return render(request, 'admin_views/create_segment.html')


# === Newsletter Dashboard ===
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from tracking.models import SubscriberSegment, Subscriber

def newsletter_dashboard_view(request):
    today = timezone.now().date()
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)

    stats = {
        'today': Subscriber.objects.filter(subscribed_at__date=today).count(),
        'week': Subscriber.objects.filter(subscribed_at__date__gte=last_7_days).count(),
        'month': Subscriber.objects.filter(subscribed_at__date__gte=last_30_days).count(),
        'total': Subscriber.objects.count(),
    }

    # Fetch all subscriber-segment relationships, ordered by subscriber creation
    recent_subscribers = SubscriberSegment.objects.select_related('subscriber', 'segment').order_by('-subscriber__subscribed_at')

    paginator = Paginator(recent_subscribers, 10)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin_views/newsletter_dashboard.html', {
        'stats': stats,
        'page_obj': page_obj,   # Send paginated subscribers
    })


# === View All Subscribers ===
def view_all_subscribers_view(request):
    query = request.GET.get('q', '')

    subscribers = Subscriber.objects.all()
    if query:
        subscribers = subscribers.filter(
            Q(name__icontains=query) | Q(email__icontains=query)
        )

    paginator = Paginator(subscribers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    segments = Segment.objects.all()

    return render(request, 'admin_views/view_all_subscribers.html', {
        'page_obj': page_obj,
        'query': query,
        'segments': segments
    })


# === Bulk Action on Subscribers ===
def bulk_action_subscribers_view(request):
    if request.method == 'POST':
        action = request.POST.get('bulkAction')
        subscriber_ids = request.POST.getlist('selected_subscribers')

        if not action or not subscriber_ids:
            messages.error(request, "Please select an action and at least one subscriber.")
            return redirect('view_all_subscribers')

        if action == 'delete':
            Subscriber.objects.filter(id__in=subscriber_ids).delete()
            messages.success(request, f"✅ {len(subscriber_ids)} subscriber(s) deleted.")
        elif action == 'move':
            segment_id = request.POST.get('segment_id')
            if not segment_id:
                messages.error(request, "Please select a segment to move to.")
                return redirect('view_all_subscribers')

            segment = get_object_or_404(Segment, id=segment_id)
            for sid in subscriber_ids:
                subscriber = get_object_or_404(Subscriber, id=sid)
                SubscriberSegment.objects.get_or_create(subscriber=subscriber, segment=segment)

            messages.success(request, f"✅ {len(subscriber_ids)} subscriber(s) moved to '{segment.name}'.")
        else:
            messages.error(request, "Unknown action selected.")

        return redirect('view_all_subscribers')

    return redirect('view_all_subscribers')


# === View All Segments ===
def view_segments(request):
    segments = Segment.objects.annotate(subscribers_count=Count('subscribers'))
    return render(request, 'admin_views/view_segments.html', {'segments': segments})


# === View Subscribers in a Segment ===
def view_segment_subscribers(request, segment_id):
    segment = get_object_or_404(Segment, id=segment_id)
    subscribers = SubscriberSegment.objects.filter(segment=segment).select_related('subscriber')

    return render(request, 'admin_views/view_segment_subscribers.html', {
        'segment': segment,
        'subscribers': subscribers
    })


# === Bulk Remove Subscribers from Segment ===
def bulk_remove_from_segment(request, segment_id):
    if request.method == 'POST':
        subscriber_ids = request.POST.getlist('subscriber_ids')
        segment = get_object_or_404(Segment, id=segment_id)

        SubscriberSegment.objects.filter(
            segment=segment,
            subscriber_id__in=subscriber_ids
        ).delete()

        messages.success(request, f"✅ {len(subscriber_ids)} subscriber(s) removed from '{segment.name}'.")
        return redirect('view_segment_subscribers', segment_id=segment.id)

    return redirect('view_segments')


# === Send Newsletter ===
def send_newsletter_view(request):
    db_segments = Segment.objects.all()
    segments = [{'id': 0, 'name': 'All Subscribers'}] + list(db_segments)

    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        segment_id = request.POST.get('segment_id')

        if not subject or not message or segment_id is None:
            messages.error(request, "Please complete all fields.")
            return redirect('send_newsletter')

        if segment_id == '0':
            recipients = Subscriber.objects.all()
        else:
            segment = get_object_or_404(Segment, id=segment_id)
            recipients = SubscriberSegment.objects.filter(segment=segment).select_related('subscriber')

        count = 0

        for sub in recipients:
            email = sub.email if hasattr(sub, 'email') else sub.subscriber.email

            if email:
                response = requests.post(
                    f"https://api.mailgun.net/v3/{settings.MAILGUN_DOMAIN}/messages",
                    auth=("api", settings.MAILGUN_API_KEY),
                    data={
                        "from": f"Naiyuan Mart <{settings.MAILGUN_FROM_EMAIL}>",
                        "to": email,
                        "subject": subject,
                        "text": message,
                        "html": f"<html><body>{message}</body></html>",
                    },
                )
                if response.status_code == 200:
                    count += 1
                else:
                    messages.warning(request, f"Failed to send to {email}: {response.text}")

        if segment_id == '0':
            messages.success(request, f"✅ Newsletter sent to {count} total subscriber(s).")
        else:
            messages.success(request, f"✅ Newsletter sent to {count} subscriber(s) in '{segment.name}'.")

        return redirect('send_newsletter')

    return render(request, 'admin_views/send_newsletter.html', {'segments': segments})
