import json
from django.core.mail import send_mail
from django.conf import settings

ORG_EMAIL = getattr(settings, 'STIRFORCHANGE_EMAIL', 'aarohi@stirforchange.org')


def send_volunteer_confirmation(signup):
    """Send confirmation to volunteer + notification to org."""
    event = signup.event

    subject = f"You're registered for {event.title}! 🎉"
    text_body = f"""Hi {signup.first_name}!

Thank you for signing up to volunteer with StirForChange! We're so excited to have you at this event.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EVENT DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Event:     {event.title}
Date:      {event.date.strftime('%A, %B %d, %Y')}
Time:      {event.start_time.strftime('%I:%M %p')} – {event.end_time.strftime('%I:%M %p')}
Location:  {event.location}
{f'Food type: {event.food_type}' if event.food_type else ''}
{f'What to bring: {event.what_to_bring}' if event.what_to_bring else ''}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

YOUR DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name:   {signup.first_name} {signup.last_name}
Email:  {signup.email}
Phone:  {signup.phone or 'Not provided'}
Age:    {signup.age}
School: {signup.school or 'Not provided'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A member of our team will reach out as soon as possible if there are any updates.
Follow us on Instagram @stirforchange for more!

Thank you for choosing to make a difference. We cannot wait to work with you!

With love and gratitude,
Aarohi Jain
Founder, StirForChange
aarohi@stirforchange.org
stirforchange.org
"""
    try:
        send_mail(
            subject=subject,
            message=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[signup.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"[Email] Volunteer confirmation failed: {e}")

    # Org notification
    org_subject = f"🙋 New Volunteer: {signup.first_name} {signup.last_name} → {event.title}"
    org_body = f"""New volunteer signup!

EVENT: {event.title} on {event.date.strftime('%B %d, %Y')}
Spots: {event.spots_taken}/{event.max_volunteers} filled

VOLUNTEER DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name:      {signup.first_name} {signup.last_name}
Email:     {signup.email}
Phone:     {signup.phone or 'Not provided'}
Age:       {signup.age}
Birthdate: {signup.birthdate}
School:    {signup.school or 'Not provided'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Signed up: {signup.created_at.strftime('%B %d, %Y at %I:%M %p')}
Dashboard: https://stirforchange.org/dashboard/
"""
    try:
        send_mail(
            subject=org_subject,
            message=org_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[ORG_EMAIL],
            fail_silently=False,
        )
    except Exception as e:
        print(f"[Email] Org notification failed: {e}")


def send_business_confirmation(business):
    subject = f"Welcome to StirForChange, {business.business_name}! 🤝"
    text_body = f"""Dear {business.contact_name},

Thank you so much for choosing to partner with StirForChange! We are truly grateful that {business.business_name} is joining our mission to fight food waste and hunger in our community.

YOUR APPLICATION DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Business:      {business.business_name}
Type:          {business.get_business_type_display()}
Contact:       {business.contact_name}
Email:         {business.email}
Phone:         {business.phone}
Address:       {business.full_address}
Frequency:     {business.frequency or 'To be confirmed'}
Surplus food:  {business.food_types or 'To be confirmed'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A member of our team will reach out as soon as possible to schedule your first pickup.

Thank you for making a difference!

Warmly,
Aarohi Jain
Founder, StirForChange
aarohi@stirforchange.org
stirforchange.org
"""
    try:
        send_mail(
            subject=subject,
            message=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[business.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"[Email] Business confirmation failed: {e}")

    org_subject = f"🏪 New Partner: {business.business_name}"
    org_body = f"""New business partner signup!

Business:  {business.business_name}
Type:      {business.get_business_type_display()}
Contact:   {business.contact_name}
Email:     {business.email}
Phone:     {business.phone}
Address:   {business.full_address}
Frequency: {business.frequency or 'Not specified'}
Food:      {business.food_types or 'Not specified'}
Notes:     {business.message or 'None'}

Submitted: {business.created_at.strftime('%B %d, %Y at %I:%M %p')}
Dashboard: https://stirforchange.org/dashboard/
"""
    try:
        send_mail(
            subject=org_subject,
            message=org_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[ORG_EMAIL],
            fail_silently=False,
        )
    except Exception as e:
        print(f"[Email] Org business notification failed: {e}")
