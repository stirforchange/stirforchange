from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string


ORG_EMAIL = getattr(settings, 'STIRFORCHANGE_EMAIL', 'stir4change@gmail.com')


def send_volunteer_confirmation(volunteer):
    """Send confirmation to volunteer + notification to org."""
    subject = "You're in! Welcome to StirForChange 🎉"

    # --- Email to the volunteer ---
    text_body = f"""Hi {volunteer.first_name},

Thank you for signing up to volunteer with StirForChange! We're so excited to have you on the team.

Here's what you submitted:
  Name:         {volunteer.first_name} {volunteer.last_name}
  Email:        {volunteer.email}
  Age:          {volunteer.age}
  School:       {volunteer.school or 'N/A'}
  Days:         {volunteer.avail_days or 'N/A'}
  Time slot:    {volunteer.avail_time_slots or 'N/A'}
  Hours/week:   {volunteer.avail_hours_week or 'N/A'}
  Specific dates: {volunteer.avail_dates or 'N/A'}

A member of our team will be in touch soon with next steps. In the meantime, follow us on Instagram @stirforchange for updates.

Together we can make a difference — one meal at a time.

Warmly,
Aarohi Jain
Founder, StirForChange
stir4change@gmail.com
"""
    try:
        send_mail(
            subject=subject,
            message=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[volunteer.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"[Email] Could not send volunteer confirmation: {e}")

    # --- Notification to org ---
    org_subject = f"New Volunteer Signup: {volunteer.first_name} {volunteer.last_name}"
    org_body = f"""New volunteer signup received!

Name:         {volunteer.first_name} {volunteer.last_name}
Email:        {volunteer.email}
Phone:        {volunteer.phone or 'N/A'}
Birthdate:    {volunteer.birthdate} (Age: {volunteer.age})
School:       {volunteer.school or 'N/A'}
Availability: {volunteer.availability or 'N/A'}
Why they want to join:
{volunteer.why_join or 'N/A'}

Signed up at: {volunteer.created_at.strftime('%B %d, %Y at %I:%M %p')}

View in dashboard: http://127.0.0.1:8000/dashboard/
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
        print(f"[Email] Could not send org volunteer notification: {e}")


def send_business_confirmation(business):
    """Send confirmation to business + notification to org."""
    subject = "Partnership Application Received — StirForChange"

    text_body = f"""Hi {business.contact_name},

Thank you for applying to become a food recovery partner with StirForChange! We're thrilled to work with {business.business_name}.

Here's a summary of your application:
  Business:      {business.business_name}
  Type:          {business.get_business_type_display()}
  Contact:       {business.contact_name}
  Email:         {business.email}
  Phone:         {business.phone}
  Address:       {business.full_address}
  Frequency:     {business.frequency or 'N/A'}
  Surplus food:  {business.food_types or 'N/A'}

By submitting this application, you have agreed to our Food Recovery Agreement, which is in accordance with California Senate Bill 1383 and Alameda County ORRO guidelines.

A member of our team will reach out within 2–3 business days to schedule your first pickup and finalize logistics.

Your partnership will directly help us fight food waste and hunger in our community. Thank you for making a difference!

Warmly,
Aarohi Jain
Founder, StirForChange
stir4change@gmail.com
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
        print(f"[Email] Could not send business confirmation: {e}")

    # --- Notification to org ---
    org_subject = f"New Business Partner: {business.business_name}"
    org_body = f"""New business partner application received!

Business:      {business.business_name}
Type:          {business.get_business_type_display()}
Contact:       {business.contact_name}
Email:         {business.email}
Phone:         {business.phone}
Address:       {business.full_address}
Frequency:     {business.frequency or 'N/A'}
Surplus food:  {business.food_types or 'N/A'}

Additional notes:
{business.message or 'N/A'}

Agreed to Food Recovery Agreement: YES
Submitted at: {business.created_at.strftime('%B %d, %Y at %I:%M %p')}

View in dashboard: http://127.0.0.1:8000/dashboard/
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
        print(f"[Email] Could not send org business notification: {e}")
