from django.core.mail import send_mail
from django.conf import settings

ORG_EMAIL = getattr(settings, 'STIRFORCHANGE_EMAIL', 'aarohi@stirforchange.org')


def send_volunteer_confirmation(signup):
    event = signup.event
    subject = "You are registered for " + event.title + "!"
    text_body = (
        "Hi " + signup.first_name + ",\n\n"
        "Thank you for signing up to volunteer with StirForChange!\n\n"
        "EVENT DETAILS\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Event:    " + event.title + "\n"
        "Date:     " + event.date.strftime('%A, %B %d, %Y') + "\n"
        "Time:     " + event.start_time.strftime('%I:%M %p') + " - " + event.end_time.strftime('%I:%M %p') + "\n"
        "Location: " + event.location + "\n"
    )
    if event.food_type:
        text_body += "Food:     " + event.food_type + "\n"
    if event.what_to_bring:
        text_body += "Bring:    " + event.what_to_bring + "\n"
    text_body += (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "YOUR DETAILS\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Name:   " + signup.first_name + " " + signup.last_name + "\n"
        "Email:  " + signup.email + "\n"
        "Phone:  " + (signup.phone or 'Not provided') + "\n"
        "School: " + (signup.school or 'Not provided') + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "We will reach out as soon as possible if there are any updates.\n\n"
        "With love and gratitude,\n"
        "Aarohi Jain\n"
        "Founder, StirForChange\n"
        "aarohi@stirforchange.org\n"
        "stirforchange.org\n"
    )
    try:
        send_mail(subject, text_body, settings.DEFAULT_FROM_EMAIL, [signup.email], fail_silently=False)
    except Exception as e:
        print("[Email] Volunteer confirmation failed:", e)

    org_subject = "New Volunteer: " + signup.first_name + " " + signup.last_name + " - " + event.title
    org_body = (
        "New volunteer signup!\n\n"
        "Event: " + event.title + " on " + event.date.strftime('%B %d, %Y') + "\n"
        "Spots: " + str(event.spots_taken) + "/" + str(event.max_volunteers) + "\n\n"
        "Name:   " + signup.first_name + " " + signup.last_name + "\n"
        "Email:  " + signup.email + "\n"
        "Phone:  " + (signup.phone or 'Not provided') + "\n"
        "Age:    " + str(signup.age) + "\n"
        "School: " + (signup.school or 'Not provided') + "\n\n"
        "Dashboard: https://stirforchange.org/dashboard/\n"
    )
    try:
        send_mail(org_subject, org_body, settings.DEFAULT_FROM_EMAIL, [ORG_EMAIL], fail_silently=False)
    except Exception as e:
        print("[Email] Org notification failed:", e)


def send_business_confirmation(business):
    subject = "Welcome to StirForChange, " + business.business_name + "!"
    text_body = (
        "Dear " + business.contact_name + ",\n\n"
        "Thank you for partnering with StirForChange!\n\n"
        "YOUR APPLICATION DETAILS\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Business:  " + business.business_name + "\n"
        "Type:      " + business.get_business_type_display() + "\n"
        "Contact:   " + business.contact_name + "\n"
        "Email:     " + business.email + "\n"
        "Phone:     " + business.phone + "\n"
        "Address:   " + business.full_address + "\n"
        "Frequency: " + (business.frequency or 'To be confirmed') + "\n"
        "Food:      " + (business.food_types or 'To be confirmed') + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "A member of our team will reach out as soon as possible.\n\n"
        "Warmly,\n"
        "Aarohi Jain\n"
        "Founder, StirForChange\n"
        "aarohi@stirforchange.org\n"
        "stirforchange.org\n"
    )
    try:
        send_mail(subject, text_body, settings.DEFAULT_FROM_EMAIL, [business.email], fail_silently=False)
    except Exception as e:
        print("[Email] Business confirmation failed:", e)

    org_subject = "New Partner: " + business.business_name
    org_body = (
        "New business partner signup!\n\n"
        "Business:  " + business.business_name + "\n"
        "Type:      " + business.get_business_type_display() + "\n"
        "Contact:   " + business.contact_name + "\n"
        "Email:     " + business.email + "\n"
        "Phone:     " + business.phone + "\n"
        "Address:   " + business.full_address + "\n"
        "Frequency: " + (business.frequency or 'Not specified') + "\n"
        "Food:      " + (business.food_types or 'Not specified') + "\n"
        "Notes:     " + (business.message or 'None') + "\n\n"
        "Dashboard: https://stirforchange.org/dashboard/\n"
    )
    try:
        send_mail(org_subject, org_body, settings.DEFAULT_FROM_EMAIL, [ORG_EMAIL], fail_silently=False)
    except Exception as e:
        print("[Email] Org business notification failed:", e)
