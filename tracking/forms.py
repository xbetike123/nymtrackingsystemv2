from django import forms
from tracking.models import Shipment, ShippingLocation, ShippingStatusTemplate


# 1. Shipping Location Form
class ShippingLocationForm(forms.ModelForm):
    class Meta:
        model = ShippingLocation
        fields = ['locations']
        widgets = {
            'locations': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded mt-2',
                'placeholder': 'Enter locations separated by commas (e.g., Guangzhou, HK, Lagos)'
            }),
        }
        labels = {'locations': 'Locations'}


# 2. Shipping Status Template Form
class ShippingStatusTemplateForm(forms.Form):
    SHIPMENT_TYPES = ShippingStatusTemplate.SHIPMENT_TYPES

    shipment_type = forms.ChoiceField(
        choices=SHIPMENT_TYPES,
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'})
    )
    status_labels = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border rounded mt-2',
            'placeholder': 'Enter status labels separated by commas'
        }),
        label='Status Labels'
    )


# 3. Shipment Status Update Form
class ShipmentStatusForm(forms.Form):
    shipment = forms.ModelChoiceField(
        queryset=Shipment.objects.all(),
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'})
    )
    location = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'})
    )
    status = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically populate cities from all saved routes
        all_locations = ShippingLocation.objects.all()
        city_set = set()
        for loc in all_locations:
            city_set.update([c.strip() for c in loc.locations.split(',')])
        self.fields['location'].choices = [(c, c) for c in sorted(city_set)]

        # Dynamically update statuses if shipment is selected
        if 'shipment' in self.data:
            try:
                shipment = Shipment.objects.get(id=self.data.get('shipment'))
                statuses = ShippingStatusTemplate.objects.filter(shipment_type=shipment.shipment_type)
                self.fields['status'].choices = [(s.label, s.label) for s in statuses]
            except (ValueError, Shipment.DoesNotExist):
                self.fields['status'].choices = []


# 4. Shipment Creation Form with CSV Upload
from django import forms
from tracking.models import Shipment, ShippingLocation

class ShipmentForm(forms.Form):
    shipment_type = forms.ChoiceField(
        choices=Shipment.SHIPMENT_TYPES,
        label="Shipment Type",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'})
    )
    tracking_number = forms.CharField(
        label="Tracking Number",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded',
            'placeholder': 'e.g. NY12345678'
        })
    )
    location = forms.ChoiceField(
        choices=[],  # Dynamically filled in __init__
        label="Destination City",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'})
    )
    eta = forms.DateField(
        label="Estimated Arrival Date",
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-4 py-2 border rounded'
        })
    )
    customer_csv = forms.FileField(
        required=True,
        label="Upload Client CSV",
        widget=forms.ClearableFileInput(attrs={'class': 'w-full mt-2'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        city_set = set()
        for record in ShippingLocation.objects.all():
            for city in record.locations.split(','):
                city_set.add(city.strip())
        self.fields['location'].choices = [(city, city) for city in sorted(city_set)]

    def save(self):
        data = self.cleaned_data
        shipment = Shipment.objects.create(
            shipment_type=data['shipment_type'],
            tracking_number=data['tracking_number'],
            location=data['location'],
            eta=data['eta']
        )
        return shipment

from django import forms
from tracking.models import Shipment, ShippingLocation

class ShipmentForm(forms.Form):
    shipment_type = forms.ChoiceField(
        choices=Shipment.SHIPMENT_TYPES,
        label="Shipment Type",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'})
    )
    tracking_number = forms.CharField(
        label="Tracking Number",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded',
            'placeholder': 'e.g. NY12345678'
        })
    )
    location = forms.ChoiceField(
        choices=[],
        label="Destination City",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'})
    )
    eta = forms.DateField(
        label="Estimated Arrival Date",
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-4 py-2 border rounded'
        })
    )
    customer_csv = forms.FileField(
        required=True,
        label="Upload Client CSV",
        widget=forms.ClearableFileInput(attrs={'class': 'w-full mt-2'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        city_set = set()
        for record in ShippingLocation.objects.all():
            for city in record.locations.split(','):
                city = city.strip()
                if city:
                    city_set.add(city)
        self.fields['location'].choices = [(city, city) for city in sorted(city_set)]

    # ✅ Add this to make .save() available
    def save(self):
        data = self.cleaned_data
        shipment = Shipment.objects.create(
            shipment_type=data['shipment_type'],
            tracking_number=data['tracking_number'],
            location=data['location'],
            eta=data['eta']
        )
        return shipment
from django import forms
from tracking.models import Shipment

class BillingForm(forms.Form):
    BILL_TYPES = [
        ('full_list', 'Full List (All Customers)'),
        ('single_customer', 'Single Customer')

    ]

    shipment = forms.ModelChoiceField(
        queryset=Shipment.objects.all(),
        label="Select Shipment",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'})
    )
    bill_type = forms.ChoiceField(
        choices=BILL_TYPES,
        label="Bill Type",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'})
    )
    exchange_rate = forms.FloatField(
        label="Exchange Rate (₦/$)",
        widget=forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded', 'placeholder': 'Enter exchange rate'})
    )
    shipping_channel = forms.MultipleChoiceField(
        choices=[('email', 'Email'), ('whatsapp', 'WhatsApp')],
        label="Send Channels",
        widget=forms.CheckboxSelectMultiple()
    )
