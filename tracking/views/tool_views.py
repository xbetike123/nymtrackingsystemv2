from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages


@login_required
def instant_quote_view(request):
    result = None
    context = {}

    if request.method == 'POST':
        try:
            if 'shipment_size' in request.POST:  # Sea shipping
                shipment_size = float(request.POST.get('shipment_size'))
                shipping_rate = float(request.POST.get('shipping_rate'))
                exchange_rate = float(request.POST.get('exchange_rate'))

                result = shipment_size * shipping_rate * exchange_rate

                context.update({
                    'result': result,
                    'shipment_size': shipment_size,
                    'shipping_rate': shipping_rate,
                    'exchange_rate': exchange_rate,
                    'type': 'sea',
                })
            else:  # Air shipping
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
                    'type': 'air',
                })

        except Exception as e:
            context['error'] = f"Calculation error: {str(e)}"

    return render(request, 'admin_views/instant_quote.html', context)


@login_required
def add_user_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_level = request.POST.get('user_level')  # "superadmin" or "staff"

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            user = User.objects.create_user(username=username, password=password)
            user.is_staff = True
            user.is_superuser = (user_level == 'superadmin')
            user.save()
            messages.success(request, "User created successfully.")
            return redirect('add_user')

    return render(request, 'admin_views/add_user.html')
