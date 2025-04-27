import requests
from django.conf import settings
from twilio.rest import Client

def send_mailgun_email(to_email, subject, text):
    return requests.post(
        f"{settings.MAILGUN_BASE_URL}/messages",
        auth=("api", settings.MAILGUN_API_KEY),
        data={
            "from": settings.FROM_EMAIL,
            "to": to_email,
            "subject": subject,
            "text": text,
        }
    )

def send_whatsapp_message(to_number, message_body):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=message_body,
        from_=settings.TWILIO_WHATSAPP_FROM,
        to=f'whatsapp:{to_number}'
    )
    return message.sid

def generate_notification_message(notification_type, customer, shipment):
    total_payable = getattr(customer, 'total', (customer.shipping_cost * 1200 + customer.clearing_cost))  # fallback rate

    if notification_type == 'departure':
        return f"""
Dear {customer.name}, your Naiyuan Mart shipment with tracking number {shipment.tracking_number} has been prepared for shipping.

Weight = {customer.weight} kg  
Shipping Cost = ${customer.shipping_cost}  
Clearing Cost = ₦{customer.clearing_cost}  

Total payable today = ₦{total_payable} (Please note, this is valid for only 24 Hours due to exchange rate fluctuations)

Track your shipment: https://naiyuanmart.com/track/{shipment.tracking_number}
        """.strip()

    elif notification_type == 'arrival':
        return f"""
Dear {customer.name}, your Naiyuan Mart shipment with tracking number {shipment.tracking_number} has arrived at the Murtala Muhammed Airport and is awaiting customs clearance.
        """.strip()

    elif notification_type == 'pickup_ready':
        return f"""
Dear {customer.name}, your shipment with tracking number {shipment.tracking_number} is ready for pickup.

Total payable today = ₦{total_payable}

📍 Pickup Address:  
8/10 Musa Oyinbo Close, Off Wulemotu Agbo Central Mosque Road,  
International Airport Road, 7/8 Bus Stop, Lagos.

Track: https://naiyuanmart.com/track/{shipment.tracking_number}
        """.strip()

    return "Invalid notification type selected."
def generate_whatsapp_demo_message(customer_name, tracking_number, weight, shipping_cost, clearing_cost, total):
    return f"""
Hi {customer_name}, your Naiyuan Mart shipment (Tracking No: {tracking_number}) is now ready! 🚚

📦 Weight: {weight}kg  
💵 Shipping: ${shipping_cost}  
🔧 Clearing: ₦{clearing_cost}  
✅ Total Payable: ₦{total}

Track: https://naiyuanmart.com/track/{tracking_number}

Please confirm your pickup within 24hrs. Thank you!
""".strip()
