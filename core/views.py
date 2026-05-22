import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import PodcastEpisode, Testimonial, DonationRecord, VolunteerSignup, BusinessSignup
from .forms import VolunteerForm, BusinessForm
from .emails import send_volunteer_confirmation, send_business_confirmation


def home(request):
    testimonials = Testimonial.objects.filter(is_active=True)[:6]
    return render(request, 'core/home.html', {'testimonials': testimonials})


def about(request):
    return render(request, 'core/about.html')


def podcast(request):
    episodes = PodcastEpisode.objects.all()
    return render(request, 'core/podcast.html', {'episodes': episodes})


def volunteer(request):
    if request.method == 'POST':
        form = VolunteerForm(request.POST)
        if form.is_valid():
            vol = form.save(commit=False)
            # Collect future date rows
            future_entries = []
            i = 0
            while i <= 20:
                d     = request.POST.get(f'future_date_{i}', '').strip()
                start = request.POST.get(f'future_start_{i}', '').strip()
                end   = request.POST.get(f'future_end_{i}', '').strip()
                if not d and not start and not end:
                    if i > 0:
                        break
                    i += 1
                    continue
                if d:
                    future_entries.append({'date': d, 'start': start, 'end': end})
                i += 1
            vol.future_dates = json.dumps(future_entries)
            vol.save()
            send_volunteer_confirmation(vol)
            messages.success(request, f"Thank you {vol.first_name}! Confirmation sent to {vol.email}.")
            return redirect('volunteer')
    else:
        form = VolunteerForm()
    return render(request, 'core/volunteer.html', {'form': form})


def business(request):
    if request.method == 'POST':
        form = BusinessForm(request.POST)
        if form.is_valid():
            biz = form.save()
            send_business_confirmation(biz)
            messages.success(request, f"Thank you, {biz.business_name}! We'll reach out within 2–3 business days.")
            return redirect('business')
    else:
        form = BusinessForm()
    return render(request, 'core/business.html', {'form': form})


def donate(request):
    return render(request, 'core/donate.html')


@staff_member_required(login_url='/admin/login/')
def dashboard(request):
    now         = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    week_start  = now - timedelta(days=7)

    volunteers        = VolunteerSignup.objects.order_by('-created_at')
    total_volunteers  = volunteers.count()
    new_volunteers    = volunteers.filter(created_at__gte=week_start).count()
    recent_volunteers = volunteers[:10]

    # Parse future_dates JSON for display
    volunteers_with_futures = []
    for v in recent_volunteers:
        try:
            futures = json.loads(v.future_dates) if v.future_dates else []
        except Exception:
            futures = []
        volunteers_with_futures.append({'vol': v, 'futures': futures})

    businesses        = BusinessSignup.objects.order_by('-created_at')
    total_businesses  = businesses.count()
    new_businesses    = businesses.filter(created_at__gte=week_start).count()
    recent_businesses = businesses[:10]

    total_donations  = DonationRecord.objects.aggregate(s=Sum('amount'))['s'] or 0
    month_donations  = DonationRecord.objects.filter(created_at__gte=month_start).aggregate(s=Sum('amount'))['s'] or 0
    donation_count   = DonationRecord.objects.count()
    recent_donations = DonationRecord.objects.order_by('-created_at')[:10]
    by_method        = DonationRecord.objects.values('method').annotate(
                           total=Sum('amount'), count=Count('id')).order_by('-total')

    total_episodes  = PodcastEpisode.objects.count()
    recent_episodes = PodcastEpisode.objects.order_by('-published_date')[:5]

    ctx = {
        'total_volunteers': total_volunteers, 'new_volunteers': new_volunteers,
        'volunteers_with_futures': volunteers_with_futures,
        'total_businesses': total_businesses, 'new_businesses': new_businesses,
        'recent_businesses': recent_businesses,
        'total_donations': total_donations, 'month_donations': month_donations,
        'donation_count': donation_count, 'recent_donations': recent_donations,
        'by_method': by_method,
        'total_episodes': total_episodes, 'recent_episodes': recent_episodes,
        'testimonial_count': Testimonial.objects.filter(is_active=True).count(),
    }
    return render(request, 'core/dashboard.html', ctx)
