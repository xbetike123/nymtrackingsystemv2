from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def instant_quote_view(request):
    result = None
    context = {}

    if request.method == 'POST':
        try:
            if 'shipment_size' in request.POST:  # Sea quote
                shipment_size = float(request.POST.get('shipment_size'))
                shipping_rate = float(request.POST.get('shipping_rate'))
                exchange_rate = float(request.POST.get('exchange_rate'))
                result = shipment_size * shipping_rate * exchange_rate
                context.update({
                    'result': result,
                    'shipment_size': shipment_size,
                    'shipping_rate': shipping_rate,
                    'exchange_rate': exchange_rate,
                    'type': 'sea'
                })
            else:  # Air quote
                weight = float(request.POST.get('weight'))
                shipping_rate = float(request.POST.get('shipping_rate'))
                clearing_rate = float(request.POST.get('clearing_rate'))
                exchange_rate = float(request.POST.get('exchange_rate'))
                result = (shipping_rate * exchange_rate + clearing_rate) * weight
                context.update({
                    'result': result,
                    'weight': weight,
                    'shipping_rate': shipping_rate,
                    'clearing_rate': clearing_rate,
                    'exchange_rate': exchange_rate,
                    'type': 'air'
                })
        except Exception as e:
            context['error'] = f"Calculation error: {str(e)}"

    return render(request, 'admin_views/instant_quote.html', context)
