import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import PodcastEpisode, Testimonial, DonationRecord, VolunteerSignup, BusinessSignup, StaffProfile
from .forms import VolunteerForm, BusinessForm
from .emails import send_volunteer_confirmation, send_business_confirmation


# ── Role decorators ───────────────────────────────────────────
def owner_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('staff_login')
        try:
            if not request.user.profile.is_owner():
                messages.error(request, "Only the owner can access this.")
                return redirect('dashboard')
        except Exception:
            return redirect('staff_login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def staff_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('staff_login')
        try:
            if not request.user.profile.is_moderator():
                return redirect('staff_login')
        except Exception:
            return redirect('staff_login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


# ── Public pages ──────────────────────────────────────────────
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
            messages.success(request, f"Thank you, {biz.business_name}! We'll be in touch as soon as possible.")
            return redirect('business')
        else:
            error_list = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_list.append(f"{field}: {error}")
            if error_list:
                messages.error(request, f"Please fix: {', '.join(error_list)}")
    else:
        form = BusinessForm()
    return render(request, 'core/business.html', {'form': form})


def donate(request):
    return render(request, 'core/donate.html')


# ── Staff login / logout ──────────────────────────────────────
def staff_login(request):
    if request.user.is_authenticated:
        try:
            if request.user.profile:
                return redirect('dashboard')
        except Exception:
            pass
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            try:
                profile = user.profile
                login(request, user)
                return redirect('dashboard')
            except StaffProfile.DoesNotExist:
                messages.error(request, "Your account does not have a staff role. Contact the owner.")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'core/staff_login.html')


def staff_logout(request):
    logout(request)
    return redirect('staff_login')


# ── Dashboard ─────────────────────────────────────────────────
@staff_required
def dashboard(request):
    now         = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    week_start  = now - timedelta(days=7)

    try:
        user_role = request.user.profile.role
    except Exception:
        user_role = 'moderator'

    # Everyone sees volunteers and businesses
    volunteers       = VolunteerSignup.objects.order_by('-created_at')
    total_volunteers = volunteers.count()
    new_volunteers   = volunteers.filter(created_at__gte=week_start).count()

    volunteers_with_futures = []
    for v in volunteers[:10]:
        try:
            futures = json.loads(v.future_dates) if v.future_dates else []
        except Exception:
            futures = []
        volunteers_with_futures.append({'vol': v, 'futures': futures})

    businesses        = BusinessSignup.objects.order_by('-created_at')
    total_businesses  = businesses.count()
    new_businesses    = businesses.filter(created_at__gte=week_start).count()
    recent_businesses = businesses[:10]

    # Admin + owner only
    total_donations  = 0
    month_donations  = 0
    donation_count   = 0
    recent_donations = []
    by_method        = []
    total_episodes   = 0
    recent_episodes  = []
    testimonial_count = 0

    if user_role in ('owner', 'admin'):
        total_donations   = DonationRecord.objects.aggregate(s=Sum('amount'))['s'] or 0
        month_donations   = DonationRecord.objects.filter(created_at__gte=month_start).aggregate(s=Sum('amount'))['s'] or 0
        donation_count    = DonationRecord.objects.count()
        recent_donations  = DonationRecord.objects.order_by('-created_at')[:10]
        by_method         = DonationRecord.objects.values('method').annotate(total=Sum('amount'), count=Count('id')).order_by('-total')
        total_episodes    = PodcastEpisode.objects.count()
        recent_episodes   = PodcastEpisode.objects.order_by('-published_date')[:5]
        testimonial_count = Testimonial.objects.filter(is_active=True).count()

    # Owner only — staff list
    staff_members = []
    if user_role == 'owner':
        staff_members = StaffProfile.objects.select_related('user', 'created_by').order_by('role', 'user__username')

    ctx = {
        'user_role': user_role,
        'total_volunteers': total_volunteers, 'new_volunteers': new_volunteers,
        'volunteers_with_futures': volunteers_with_futures,
        'total_businesses': total_businesses, 'new_businesses': new_businesses,
        'recent_businesses': recent_businesses,
        'total_donations': total_donations, 'month_donations': month_donations,
        'donation_count': donation_count, 'recent_donations': recent_donations,
        'by_method': by_method,
        'total_episodes': total_episodes, 'recent_episodes': recent_episodes,
        'testimonial_count': testimonial_count,
        'staff_members': staff_members,
    }
    return render(request, 'core/dashboard.html', ctx)


# ── Staff management (owner only) ─────────────────────────────
@owner_required
def staff_manage(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            username   = request.POST.get('username', '').strip()
            password   = request.POST.get('password', '').strip()
            role       = request.POST.get('role', 'moderator')
            first_name = request.POST.get('first_name', '').strip()
            last_name  = request.POST.get('last_name', '').strip()

            if not username or not password:
                messages.error(request, "Username and password are required.")
            elif User.objects.filter(username=username).exists():
                messages.error(request, f"Username '{username}' is already taken.")
            elif role == 'owner':
                messages.error(request, "Cannot create another owner account.")
            else:
                user = User.objects.create_user(
                    username=username, password=password,
                    first_name=first_name, last_name=last_name
                )
                StaffProfile.objects.create(user=user, role=role, created_by=request.user)
                messages.success(request, f"✅ {role.capitalize()} '{username}' created successfully!")

        elif action == 'delete':
            user_id = request.POST.get('user_id')
            try:
                target = User.objects.get(id=user_id)
                if target == request.user:
                    messages.error(request, "You cannot delete your own account.")
                elif hasattr(target, 'profile') and target.profile.role == 'owner':
                    messages.error(request, "Cannot delete the owner account.")
                else:
                    name = target.username
                    target.delete()
                    messages.success(request, f"✅ Account '{name}' deleted.")
            except User.DoesNotExist:
                messages.error(request, "User not found.")

        elif action == 'change_role':
            user_id  = request.POST.get('user_id')
            new_role = request.POST.get('new_role')
            try:
                target = User.objects.get(id=user_id)
                if new_role == 'owner':
                    messages.error(request, "Cannot assign owner role.")
                elif hasattr(target, 'profile') and target.profile.role == 'owner':
                    messages.error(request, "Cannot change the owner's role.")
                else:
                    target.profile.role = new_role
                    target.profile.save()
                    messages.success(request, f"✅ {target.username}'s role changed to {new_role}.")
            except User.DoesNotExist:
                messages.error(request, "User not found.")

        return redirect('staff_manage')

    staff_members = StaffProfile.objects.select_related('user', 'created_by').order_by('role')
    return render(request, 'core/staff_manage.html', {'staff_members': staff_members})
