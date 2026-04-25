from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import time

@shared_task
def send_registration_confirmation_email(user_email, activity_name, username):
    """
    Simulates sending an email confirmation in the background.
    """
    subject = f'Registration Confirmed: {activity_name}'
    message = f'Hi {username},\n\nYou have successfully registered for "{activity_name}".\n\nThank you for volunteering!'
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]
    
    # Simulate some processing time
    time.sleep(2) 
    
    send_mail(subject, message, email_from, recipient_list)
    return f"Email sent to {user_email} for {activity_name}"

@shared_task
def broadcast_notification(message):
    """
    Placeholder for a scheduled broadcast task.
    """
    return f"Broadcast: {message}"
