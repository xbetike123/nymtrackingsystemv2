from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.template.loader import render_to_string  # ✅ Added
from tracking.forms import BillingForm
from tracking.models import ShipmentCustomer, Shipment

@login_required
def shipping_billing_view(request):
    form = BillingForm()

    if request.method == 'POST':
        form = BillingForm(request.POST)
        if form.is_valid():
            post_data = request.POST.copy()
            form_data = post_data.dict()
            form_data['shipping_channel'] = post_data.getlist('shipping_channel')

            request.session['billing_form_data'] = form_data
            request.session.modified = True
            return redirect('shipping_billing_preview')

    return render(request, 'admin_views/shipping_billing_form.html', {'form': form})

@login_required
def shipping_billing_preview(request):
    form_data = request.session.get('billing_form_data')
    if not form_data:
        return redirect('shipping_billing')

    form = BillingForm(form_data)
    if not form.is_valid():
        return redirect('shipping_billing')

    shipment_id = form_data.get('shipment')
    bill_type = form_data.get('bill_type')
    exchange_rate = float(form_data.get('exchange_rate', 0))
    channels = form_data.get('shipping_channel', [])
    selected_customer_id = form_data.get('selected_customer')

    try:
        shipment = Shipment.objects.get(id=shipment_id)
    except Shipment.DoesNotExist:
        return redirect('shipping_billing')

    customers = shipment.customers.all()
    if bill_type == 'single_customer' and selected_customer_id:
        customers = customers.filter(id=selected_customer_id)

    if not customers.exists():
        return redirect('shipping_billing')

    # Always pick the first customer (even if it's one)
    customer = customers.first()
    total_payable = (customer.shipping_cost * exchange_rate) + customer.clearing_cost

    # ✅ Build context for templates
    context = {
        'customer': customer,
        'exchange_rate': exchange_rate,
        'total_payable': round(total_payable, 2),
    }

    # ✅ Render email and WhatsApp templates
    email_preview = None
    whatsapp_preview = None

    if 'email' in channels:
        email_preview = render_to_string('emails/shipping_billing_email.html', context)

    if 'whatsapp' in channels:
        whatsapp_preview = render_to_string('whatsapp/shipping_billing.txt', context)

    return render(request, 'admin_views/shipping_billing_preview.html', {
        'form': form,
        'bill_type': bill_type,
        'shipment': shipment,
        'exchange_rate': exchange_rate,
        'channels': channels,
        'email_preview': email_preview,
        'whatsapp_preview': whatsapp_preview,
    })

@login_required
def fetch_customers_api(request):
    shipment_id = request.GET.get('shipment_id')
    if not shipment_id:
        return JsonResponse({'error': 'Missing shipment ID'}, status=400)

    try:
        shipment = Shipment.objects.get(id=shipment_id)
    except Shipment.DoesNotExist:
        return JsonResponse({'error': 'Shipment not found'}, status=404)

    customers = shipment.customers.all()
    data = [
        {'id': customer.id, 'name': customer.name, 'phone': customer.phone}
        for customer in customers
    ]
    return JsonResponse({'customers': data})

@login_required
def send_shipping_bill(request):
    if request.method == 'POST':
        messages.success(request, "✅ Bill sent successfully!")
        return redirect('shipping_billing')
    return redirect('shipping_billing')
