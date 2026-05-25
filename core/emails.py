import json
from django.core.mail import send_mail
from django.conf import settings

ORG_EMAIL = getattr(settings, 'STIRFORCHANGE_EMAIL', 'stir4change@gmail.com')


def send_volunteer_confirmation(volunteer):
    """Send warm confirmation to volunteer + detailed notification to org."""

    # Parse future dates
    try:
        futures = json.loads(volunteer.future_dates) if volunteer.future_dates else []
    except Exception:
        futures = []

    future_text = ''
    if futures:
        future_text = '\nYour scheduled volunteer dates:\n'
        for f in futures:
            time_str = f"{f.get('start','')} – {f.get('end','')}" if f.get('start') else 'Time TBD'
            future_text += f"  • {f.get('date', '')}  |  {time_str}\n"
    else:
        future_text = '\nNo specific dates added yet — we will be in touch to schedule!\n'

    general_avail = ''
    if volunteer.avail_days:
        general_avail = f"\nGeneral availability:\n  Days: {volunteer.avail_days}"
        if volunteer.avail_start and volunteer.avail_end:
            general_avail += f"\n  Time: {volunteer.avail_start} – {volunteer.avail_end}"

    # ── Email to volunteer ──────────────────────────────
    subject = "You're officially a StirForChange volunteer! 🎉"
    text_body = f"""Hi {volunteer.first_name}!

Thank you so much for signing up to volunteer with StirForChange. We are beyond excited to have you join our team! 💚

You are now part of a growing movement of young people who believe that no good food should go to waste while people go hungry. Every hour you give will turn into real meals for real families in our community.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR APPLICATION DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name:     {volunteer.first_name} {volunteer.last_name}
Email:    {volunteer.email}
Phone:    {volunteer.phone or 'Not provided'}
Age:      {volunteer.age}
School:   {volunteer.school or 'Not provided'}
{general_avail}
{future_text}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT HAPPENS NEXT?

A member of our team will reach out to you within 2–3 days to:
  ✅ Confirm your schedule
  ✅ Share volunteer guidelines
  ✅ Add you to our volunteer group

In the meantime, follow us on Instagram @stirforchange for updates on
pickups, events, and community highlights!

Thank you for choosing to make a difference. We can't wait to work with you!

With love and gratitude,
Aarohi Jain
Founder, StirForChange
stir4change@gmail.com
stirforchange.org
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
        print(f"[Email] Volunteer confirmation to {volunteer.email} failed: {e}")

    # ── Notification to org ─────────────────────────────
    org_subject = f"🙋 New Volunteer: {volunteer.first_name} {volunteer.last_name}"
    org_body    = f"""New volunteer signup on stirforchange.org!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PERSONAL INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name:       {volunteer.first_name} {volunteer.last_name}
Email:      {volunteer.email}
Phone:      {volunteer.phone or 'Not provided'}
Age:        {volunteer.age}
Birthdate:  {volunteer.birthdate}
School:     {volunteer.school or 'Not provided'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AVAILABILITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
General days:  {volunteer.avail_days or 'Not specified'}
General time:  {volunteer.avail_start or '—'} – {volunteer.avail_end or '—'}
{future_text}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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
    """Send warm confirmation to business + detailed notification to org."""

    # ── Email to business ───────────────────────────────
    subject   = f"Welcome to StirForChange, {business.business_name}! 🤝"
    text_body = f"""Dear {business.contact_name},

Thank you so much for partnering with StirForChange! We are truly grateful that {business.business_name} is joining our mission to fight food waste and hunger in our community.

Your partnership means the world to us. Every donation of surplus food from your business will be carefully packed and delivered — same day — to homeless individuals and families in need. Together, we are turning what would have been waste into life-changing meals.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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

FOOD RECOVERY AGREEMENT

By submitting your application, you have agreed to our Food Recovery Agreement
in accordance with California Senate Bill 1383 and Alameda County ORRO guidelines.
This agreement protects both parties under the Bill Emerson Good Samaritan
Food Donation Act.

WHAT HAPPENS NEXT?

A member of our team will reach out within 2–3 business days to:
  ✅ Schedule your first pickup
  ✅ Confirm food handling logistics
  ✅ Provide you with a tax-deductible donation receipt setup
  ✅ Feature your business as an official StirForChange partner

We accept fresh, properly stored, or unopened food only. Our volunteers are
trained in safe food handling and will always arrive on time.

Thank you for making a difference in our community. We are so proud to call
{business.business_name} a StirForChange partner!

Warmly,
Aarohi Jain
Founder, StirForChange
stir4change@gmail.com
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
        print(f"[Email] Business confirmation to {business.email} failed: {e}")

    # ── Notification to org ─────────────────────────────
    org_subject = f"🏪 New Partner: {business.business_name}"
    org_body    = f"""New business partner signup on stirforchange.org!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BUSINESS INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Business:     {business.business_name}
Type:         {business.get_business_type_display()}
Contact:      {business.contact_name}
Email:        {business.email}
Phone:        {business.phone}
Address:      {business.full_address}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FOOD DONATION DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Frequency:    {business.frequency or 'Not specified'}
Food types:   {business.food_types or 'Not specified'}
Notes:        {business.message or 'None'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Agreed to Food Recovery Agreement: YES ✅
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
