from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Test email configuration'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email address to send test to')

    def handle(self, *args, **options):
        email = options['email'] or 'suavedef@gmail.com'
        
        try:
            result = send_mail(
                'Django Email Test',
                'This email confirms your Django email configuration is working.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            if result == 1:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Email sent successfully to {email}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ Email sending failed - result: {result}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Email sending failed: {str(e)}')
            )
"""

# 5. Updated settings.py email configuration (more explicit)
"""
# Add these to your settings.py for better debugging

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.core.mail': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

# Email settings (your current settings look correct)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'suavedef@gmail.com'
EMAIL_HOST_PASSWORD = 'fmgekozjcclhoiry'  # Your app password
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'Catholic Diocese of Enugu <suavedef@gmail.com>'

# For debugging, temporarily use console backend
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
""