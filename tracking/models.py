from django.db import models
from django.utils import timezone


# 1. Shipping Routes
class ShippingLocation(models.Model):
    locations = models.TextField(
        help_text="Comma-separated locations (e.g., Guangzhou, HK, Lagos)"
    )

    def __str__(self):
        parts = self.locations.split(',')
        return f"Route: {parts[0].strip()} → {parts[-1].strip()}" if len(parts) > 1 else self.locations


# 2. Shipping Status Templates
class ShippingStatusTemplate(models.Model):
    SHIPMENT_TYPES = [
        ('air_normal', 'Air Normal'),
        ('air_hk', 'Air HK'),
        ('sea', 'Sea'),
    ]

    shipment_type = models.CharField(max_length=50, choices=SHIPMENT_TYPES)
    label = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.label} ({self.get_shipment_type_display()})"


# 3. Shipment Model
class Shipment(models.Model):
    SHIPMENT_TYPES = [
        ('air_normal', 'Air Normal'),
        ('air_hk', 'Air HK'),
        ('sea', 'Sea'),
    ]

    shipment_type = models.CharField(max_length=50, choices=SHIPMENT_TYPES)
    tracking_number = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    eta = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.tracking_number} - {self.location}"


# 4. Shipment Status Updates
class ShipmentStatus(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='statuses')
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.shipment.tracking_number} - {self.status} @ {self.location}"


# 5. Shipment Customers
class ShipmentCustomer(models.Model):
    shipment = models.ForeignKey(Shipment, related_name="customers", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    weight = models.FloatField()
    shipping_cost = models.FloatField()
    clearing_cost = models.FloatField()
    total = models.FloatField()
    email = models.EmailField()

    def __str__(self):
        return f"{self.name} ({self.phone}) - ₦{self.total}"


# 6. Notification Log
class NotificationLog(models.Model):
    customer = models.ForeignKey(ShipmentCustomer, on_delete=models.CASCADE, related_name="notifications")
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)
    channel = models.CharField(max_length=20)  # 'email' or 'whatsapp'
    message = models.TextField()
    sid = models.CharField(max_length=255, blank=True, null=True)

    sent_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, default="pending")  # 'sent' or 'failed'

    def __str__(self):
        return f"{self.customer.name} - {self.channel} - {self.status}"


# 7. Newsletter Management
class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    subscribed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.email


class Segment(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class SubscriberSegment(models.Model):
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name='segments')
    segment = models.ForeignKey(Segment, on_delete=models.CASCADE, related_name='subscribers')
    added_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('subscriber', 'segment')

    def __str__(self):
        return f"{self.subscriber.email} → {self.segment.name}"
created_at = models.DateTimeField(auto_now_add=True)
