from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.loader import render_to_string
from tracking.models import Shipment, ShipmentCustomer, NotificationLog
from tracking.utils.notification_utils import send_mailgun_email, send_whatsapp_message

# === Notification Template Mapping ===
NOTIFICATION_TEMPLATE_MAPPING = {
    'departure': {
        'email': 'emails/departure_notification.html',
        'whatsapp': 'whatsapp/departure_notification.txt',
    },
    'arrival': {
        'email': 'emails/arrival_notification_email.html',
        'whatsapp': 'whatsapp/arrival_notification.txt',
    },
    'pickup': {
        'email': 'emails/pickup_notification_email.html',
        'whatsapp': 'whatsapp/pickup_notification.txt',
    }
}

# === Subject templates ===
SUBJECT_TEMPLATE_MAPPING = {
    'departure': '{customer_name}, your shipment is on the way to you! 📦',
    'arrival': '{customer_name}, your goods have landed! ✈️',
    'pickup': '{customer_name}, your shipment is ready for pickup! 📦',
}

# === Preview text templates ===
PREVIEW_TEMPLATE_MAPPING = {
    'departure': 'Your shipment is on the way. Track it easily here!',
    'arrival': 'Your goods have landed. Get ready!',
    'pickup': 'Your shipment is ready for pickup!',
}

@login_required
def send_notifications_view(request):
    shipments = Shipment.objects.all()

    if request.method == 'POST':
        request.session['notification_data'] = {
            'shipment_id': request.POST.get('shipment_id'),
            'notification_type': request.POST.get('notification_type'),
            'channels': request.POST.getlist('channels'),
        }
        return redirect('preview_notification')

    return render(request, 'admin_views/send_notification.html', {'shipments': shipments})


@login_required
def preview_notification_view(request):
    data = request.session.get('notification_data')

    if not data:
        messages.error(request, "Session expired or invalid. Please re-submit the notification form.")
        return redirect('send_notification')

    shipment = get_object_or_404(Shipment, id=data['shipment_id'])
    customer = shipment.customers.first()

    if not customer:
        return render(request, 'admin_views/preview_notification.html', {
            'error': 'No customers found for this shipment.'
        })

    context = {
        'customer_name': customer.name,
        'tracking_number': shipment.tracking_number,
        'tracking_url': f"https://naiyuanmart.com/track/{shipment.tracking_number}",
        'weight': customer.weight,
        'shipping_cost': customer.shipping_cost,
        'clearing_cost': customer.clearing_cost,
        'total_today': customer.total,
    }

    templates = NOTIFICATION_TEMPLATE_MAPPING.get(data['notification_type'], {})

    email_preview = None
    whatsapp_preview = None

    selected_channels = [c.lower() for c in data['channels']]

    if 'email' in selected_channels and templates.get('email'):
        email_preview = render_to_string(templates['email'], context)

    if 'whatsapp' in selected_channels and templates.get('whatsapp'):
        whatsapp_preview = render_to_string(templates['whatsapp'], context).strip()

    return render(request, 'admin_views/preview_notification.html', {
        'shipment': shipment,
        'notification_type': data['notification_type'],
        'channels': selected_channels,
        'email_preview': email_preview,
        'whatsapp_preview': whatsapp_preview,
    })


@login_required
def send_notifications(request):
    data = request.session.pop('notification_data', None)

    if not data:
        messages.error(request, "No notification data to send.")
        return redirect('send_notification')

    shipment = get_object_or_404(Shipment, id=data['shipment_id'])

    for customer in shipment.customers.all():
        context = {
            'customer_name': customer.name,
            'tracking_number': shipment.tracking_number,
            'tracking_url': f"https://naiyuanmart.com/track/{shipment.tracking_number}",
            'weight': customer.weight,
            'shipping_cost': customer.shipping_cost,
            'clearing_cost': customer.clearing_cost,
            'total_today': customer.total,
        }

        templates = NOTIFICATION_TEMPLATE_MAPPING.get(data['notification_type'], {})
        selected_channels = [c.lower() for c in data['channels']]

        subject_template = SUBJECT_TEMPLATE_MAPPING.get(data['notification_type'], 'Naiyuan Mart Shipment Update')
        subject = subject_template.format(customer_name=customer.name)

        preview_text = PREVIEW_TEMPLATE_MAPPING.get(data['notification_type'], '')

        for channel in selected_channels:
            try:
                if channel == 'email' and templates.get('email'):
                    email_html = render_to_string(templates['email'], {**context, 'preview_text': preview_text})
                    response = send_mailgun_email(
                        to_email=customer.email,
                        subject=subject,
                        text=email_html,
                    )
                    status = "sent" if response.status_code == 200 else "failed"

                elif channel == 'whatsapp' and templates.get('whatsapp'):
                    whatsapp_message = render_to_string(templates['whatsapp'], context).strip()
                    sid = send_whatsapp_message(
                        to_number=customer.phone,
                        message_body=whatsapp_message
                    )
                    status = "sent" if sid else "failed"
                else:
                    status = "unknown"
            except Exception as e:
                print("Error sending notification:", e)
                status = "failed"

            NotificationLog.objects.create(
                customer=customer,
                shipment=shipment,
                channel=channel,
                message=whatsapp_message if channel == 'whatsapp' else email_html,
                status=status,
            )

    messages.success(request, "✅ Notification sent successfully.")
    return redirect('view_shipments')
