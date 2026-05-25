import json
from django.core.mail import send_mail
from django.conf import settings

ORG_EMAIL = getattr(settings, 'STIRFORCHANGE_EMAIL', 'stir4change@gmail.com')


def send_volunteer_confirmation(volunteer):
    """Send confirmation to volunteer + notification to org."""

    # Parse future dates
    try:
        futures = json.loads(volunteer.future_dates) if volunteer.future_dates else []
    except Exception:
        futures = []

    future_lines = ''
    if futures:
        future_lines = '\n  Specific dates you can volunteer:'
        for f in futures:
            time_str = f"{f.get('start','')} – {f.get('end','')}" if f.get('start') else ''
            future_lines += f"\n    • {f.get('date','')} {time_str}"
    else:
        future_lines = '\n  Specific dates: None added'

    # Email to volunteer
    subject   = "You're in! Welcome to StirForChange 🎉"
    text_body = f"""Hi {volunteer.first_name},

Thank you for signing up to volunteer with StirForChange! We're so excited to have you on the team.

Here's what you submitted:
  Name:     {volunteer.first_name} {volunteer.last_name}
  Email:    {volunteer.email}
  Phone:    {volunteer.phone or 'N/A'}
  Age:      {volunteer.age}
  School:   {volunteer.school or 'N/A'}

General availability:
  Days:     {volunteer.avail_days or 'Not specified'}
  Time:     {volunteer.avail_start or '—'} – {volunteer.avail_end or '—'}
{future_lines}

A member of our team will be in touch soon. Follow us on Instagram @stirforchange for updates!

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
        print(f"[Email] Volunteer confirmation failed: {e}")

    # Notification to org
    org_subject = f"New Volunteer: {volunteer.first_name} {volunteer.last_name}"
    org_body    = f"""New volunteer signup!

Name:      {volunteer.first_name} {volunteer.last_name}
Email:     {volunteer.email}
Phone:     {volunteer.phone or 'N/A'}
Age:       {volunteer.age}
Birthdate: {volunteer.birthdate}
School:    {volunteer.school or 'N/A'}

General availability:
  Days:  {volunteer.avail_days or 'Not specified'}
  Time:  {volunteer.avail_start or '—'} – {volunteer.avail_end or '—'}
{future_lines}

Signed up: {volunteer.created_at.strftime('%B %d, %Y at %I:%M %p')}
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
        print(f"[Email] Org volunteer notification failed: {e}")


def send_business_confirmation(business):
    """Send confirmation to business + notification to org."""
    subject   = "Partnership Application Received — StirForChange"
    text_body = f"""Hi {business.contact_name},

Thank you for applying to become a food recovery partner with StirForChange!
We're thrilled to work with {business.business_name}.

Your application summary:
  Business:     {business.business_name}
  Type:         {business.get_business_type_display()}
  Contact:      {business.contact_name}
  Email:        {business.email}
  Phone:        {business.phone}
  Address:      {business.full_address}
  Frequency:    {business.frequency or 'N/A'}
  Surplus food: {business.food_types or 'N/A'}

By submitting this application you have agreed to our Food Recovery Agreement,
in accordance with California Senate Bill 1383 and Alameda County ORRO guidelines.

A member of our team will reach out within 2–3 business days to schedule your
first pickup and finalize logistics.

Thank you for helping us fight food waste and hunger in our community!

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
        print(f"[Email] Business confirmation failed: {e}")

    # Notification to org
    org_subject = f"New Business Partner: {business.business_name}"
    org_body    = f"""New business partner application!

Business:     {business.business_name}
Type:         {business.get_business_type_display()}
Contact:      {business.contact_name}
Email:        {business.email}
Phone:        {business.phone}
Address:      {business.full_address}
Frequency:    {business.frequency or 'N/A'}
Surplus food: {business.food_types or 'N/A'}
Notes:        {business.message or 'N/A'}

Agreed to Food Recovery Agreement: YES
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
