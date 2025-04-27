from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils.timezone import now, timedelta
from django.db.models import Count
from tracking.models import Shipment, ShipmentStatus, ShippingStatusTemplate, NotificationLog

# ✅ Admin Dashboard
@login_required
def admin_dashboard(request):
    return render(request, 'admin_views/admin_dashboard.html', {
        'add_url': '/add-shipment/',
        'view_url': '/shipments/',
        'status_url': '/update-status/',
    })

# ✅ Dummy Coming Soon Page
@login_required
def dummy_view(request):
    return HttpResponse("<h1>This page will be built soon...</h1>")

# ✅ Delivery Status Page
from django.db.models import Count
from tracking.models import NotificationLog
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def delivery_status_view(request):
    logs = NotificationLog.objects.all().order_by('-sent_at')

    summary = {}

    for log in logs:
        # Analyze message content to determine message type
        if 'prepared for shipping' in log.message.lower():
            message_type = 'Departure'
        elif 'arrived at the murtala' in log.message.lower():
            message_type = 'Arrival'
        elif 'ready for pickup' in log.message.lower():
            message_type = 'Pickup Ready'
        else:
            message_type = 'Other'

        key = (message_type, log.sent_at.date())

        if key not in summary:
            summary[key] = {
                'message_type': message_type,
                'recipients': 0,
                'email': False,
                'whatsapp': False,
                'failed': 0,
                'date': log.sent_at.strftime("%d-%m-%Y"),
            }

        summary[key]['recipients'] += 1

        if log.channel == 'email':
            summary[key]['email'] = True
        elif log.channel == 'whatsapp':
            summary[key]['whatsapp'] = True

        if log.status == 'failed':
            summary[key]['failed'] += 1

    summary_list = list(summary.values())

    return render(request, 'admin_views/delivery_status.html', {
        'summary': summary_list
    })

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tracking.models import NotificationLog
from django.utils.timezone import now
from django.db.models import Count

@login_required
def admin_dashboard(request):
    # 📦 Fetch recent notification summary for dashboard
    today = now()
    past_7_days = today - timedelta(days=7)

    logs = NotificationLog.objects.filter(sent_at__range=[past_7_days, today])

    summary = {}

    for log in logs:
        if 'prepared for shipping' in log.message.lower():
            message_type = 'Departure'
        elif 'arrived at the murtala' in log.message.lower():
            message_type = 'Arrival'
        elif 'ready for pickup' in log.message.lower():
            message_type = 'Pickup Ready'
        else:
            message_type = 'Other'

        key = (message_type, log.sent_at.date())

        if key not in summary:
            summary[key] = {
                'message_type': message_type,
                'recipients': 0,
                'email': False,
                'whatsapp': False,
                'failed': 0,
                'date': log.sent_at.strftime("%d-%m-%Y"),
            }

        summary[key]['recipients'] += 1

        if log.channel == 'email':
            summary[key]['email'] = True
        elif log.channel == 'whatsapp':
            summary[key]['whatsapp'] = True

    summary_list = list(summary.values())

    return render(request, 'admin_views/admin_dashboard.html', {
        'add_url': '/admin/add-shipment/',
        'view_url': '/admin/shipments/',
        'status_url': '/admin/update-status/',
        'summary': summary_list  # ✅ Send summary to dashboard
    })
