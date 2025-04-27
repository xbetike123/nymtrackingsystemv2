from django.shortcuts import render

def cbm_calculator(request):
    return render(request, 'cbm_calculator.html')

def address_generator(request):
    return render(request, 'address_generator.html')

def contact_us(request):
    return render(request, 'contact_us.html')
