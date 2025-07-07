# from twilio.rest import Client
# from django.conf import settings

# def send_sms_otp(phone_number, otp):
#     if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
#         return False  # Skip in development
    
#     client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
#     try:
#         message = client.messages.create(
#             body=f"Your OTP for ECD Registry is: {otp}",
#             from_=settings.TWILIO_PHONE_NUMBER,
#             to=phone_number
#         )
#         return True
#     except Exception as e:
#         print(f"Failed to send SMS: {e}")
#         return False



# for development
from django.conf import settings

def send_sms_otp(phone_number, otp):
    """
    Send OTP via SMS. In development, just print to console.
    In production, you would use a service like Twilio.
    """
    if settings.DEBUG:
        # In development, just print the OTP to console
        print(f"[DEV] SMS OTP for {phone_number}: {otp}")
        return True
    else:
        # Production code would go here (e.g., using Twilio)
        # from twilio.rest import Client
        # try:
        #     client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        #     message = client.messages.create(
        #         body=f"Your OTP for ECD Registry is: {otp}",
        #         from_=settings.TWILIO_PHONE_NUMBER,
        #         to=phone_number
        #     )
        #     return True
        # except Exception as e:
        #     print(f"Failed to send SMS: {e}")
        #     return False
        return False  # Change this when implementing production SMS