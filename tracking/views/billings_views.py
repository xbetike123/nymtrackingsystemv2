from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from tracking.forms import BillingForm
from django.contrib import messages

from tracking.models import ShipmentCustomer, Shipment


@login_required
def shipping_billing_view(request):
    form = BillingForm()

    if request.method == 'POST':
        form = BillingForm(request.POST)
        if form.is_valid():
            # Convert POST to dict and preserve list fields manually
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
    total = (customer.shipping_cost * exchange_rate) + customer.clearing_cost

    message = f"""Hello {customer.name}, your shipment is ready for pickup at our Warehouse, Pickup address is at 8/10 Musa Oyinbo Close, Off Wulemotu Agbo Central Mosque road, International Airport Road, 7/8 busstop, Lagos.

Weight: {customer.weight} kg  
Shipping Fee: ${customer.shipping_cost}  
Clearing Fee: ₦{customer.clearing_cost}  
Exchange Rate: ₦{exchange_rate}  
Total Payable: ₦{round(total, 2)} (Please note this amount is valid for only 24 hours due to exchange rate fluctuation)

Kindly make payment to the account account below:

2034181913

Naiyuan Mart 

First Bank of Nigeria

Thank you for your continued patronage.

You can reach the warehouse on +234 816 809 4074
"""

    bill_data = [{
        'name': customer.name,
        'phone': customer.phone,
        'weight': customer.weight,
        'shipping_fee': customer.shipping_cost,
        'clearing_fee': customer.clearing_cost,
        'total_payable': round(total, 2),
        'message': message,
    }]

    return render(request, 'admin_views/shipping_billing_preview.html', {
        'form': form,
        'bill_type': bill_type,
        'shipment': shipment,
        'bill_data': bill_data,
        'exchange_rate': exchange_rate,
        'channels': channels,
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
        # Process the session data and send via email/WhatsApp/etc
        # ...
        messages.success(request, "Bill sent successfully!")
        return redirect('shipping_billing')
    return redirect('shipping_billing')
