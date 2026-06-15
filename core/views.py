import json
from django.shortcuts import render, redirect, get_object_or_404
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


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('staff_login')
        try:
            if not request.user.profile.is_admin():
                messages.error(request, "Admin access required.")
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


def get_role(request):
    try:
        return request.user.profile.role
    except Exception:
        return None


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
                    if i > 0: break
                    i += 1; continue
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


# ── Staff auth ────────────────────────────────────────────────
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


# ── Main Dashboard ────────────────────────────────────────────
@staff_required
def dashboard(request):
    now         = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    week_start  = now - timedelta(days=7)
    user_role   = get_role(request)

    volunteers       = VolunteerSignup.objects.order_by('-created_at')
    total_volunteers = volunteers.count()
    new_volunteers   = volunteers.filter(created_at__gte=week_start).count()

    volunteers_with_futures = []
    for v in volunteers[:10]:
        try: futures = json.loads(v.future_dates) if v.future_dates else []
        except: futures = []
        volunteers_with_futures.append({'vol': v, 'futures': futures})

    businesses        = BusinessSignup.objects.order_by('-created_at')
    total_businesses  = businesses.count()
    new_businesses    = businesses.filter(created_at__gte=week_start).count()
    recent_businesses = businesses[:10]

    total_donations = month_donations = donation_count = 0
    recent_donations = by_method = recent_episodes = []
    total_episodes = testimonial_count = 0
    staff_members = []
    testimonials  = []

    if user_role in ('owner', 'admin'):
        total_donations   = DonationRecord.objects.aggregate(s=Sum('amount'))['s'] or 0
        month_donations   = DonationRecord.objects.filter(created_at__gte=month_start).aggregate(s=Sum('amount'))['s'] or 0
        donation_count    = DonationRecord.objects.count()
        recent_donations  = DonationRecord.objects.order_by('-created_at')[:10]
        by_method         = DonationRecord.objects.values('method').annotate(total=Sum('amount'), count=Count('id')).order_by('-total')
        total_episodes    = PodcastEpisode.objects.count()
        recent_episodes   = PodcastEpisode.objects.order_by('-published_date')[:10]
        testimonial_count = Testimonial.objects.count()
        testimonials      = Testimonial.objects.order_by('-created_at')[:10]

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
        'testimonial_count': testimonial_count, 'testimonials': testimonials,
        'staff_members': staff_members,
    }
    return render(request, 'core/dashboard.html', ctx)


# ── Volunteer CRUD ────────────────────────────────────────────
@admin_required
def volunteer_edit(request, pk):
    vol = get_object_or_404(VolunteerSignup, pk=pk)
    if request.method == 'POST':
        for field in ['first_name','last_name','email','phone','school','avail_days','avail_start','avail_end']:
            val = request.POST.get(field, '').strip()
            if val is not None:
                setattr(vol, field, val)
        vol.save()
        messages.success(request, f"Volunteer {vol.first_name} {vol.last_name} updated.")
        return redirect('dashboard')
    return render(request, 'core/volunteer_edit.html', {'vol': vol, 'user_role': get_role(request)})

@owner_required
def volunteer_delete(request, pk):
    vol = get_object_or_404(VolunteerSignup, pk=pk)
    name = f"{vol.first_name} {vol.last_name}"
    vol.delete()
    messages.success(request, f"Volunteer '{name}' deleted.")
    return redirect('dashboard')


# ── Business CRUD ─────────────────────────────────────────────
@admin_required
def business_edit(request, pk):
    biz = get_object_or_404(BusinessSignup, pk=pk)
    if request.method == 'POST':
        for field in ['business_name','contact_name','email','phone','business_type','street_address','city','state','zip_code','frequency','food_types','message']:
            val = request.POST.get(field, '').strip()
            if val is not None:
                setattr(biz, field, val)
        biz.save()
        messages.success(request, f"{biz.business_name} updated.")
        return redirect('dashboard')
    return render(request, 'core/business_edit.html', {'biz': biz, 'user_role': get_role(request)})

@owner_required
def business_delete(request, pk):
    biz = get_object_or_404(BusinessSignup, pk=pk)
    name = biz.business_name
    biz.delete()
    messages.success(request, f"Business '{name}' deleted.")
    return redirect('dashboard')


# ── Podcast CRUD ──────────────────────────────────────────────
@admin_required
def podcast_add(request):
    if request.method == 'POST':
        ep = PodcastEpisode(
            title          = request.POST.get('title','').strip(),
            guest_name     = request.POST.get('guest_name','').strip(),
            guest_title    = request.POST.get('guest_title','').strip(),
            episode_type   = request.POST.get('episode_type','video'),
            description    = request.POST.get('description','').strip(),
            content        = request.POST.get('content','').strip(),
            youtube_url    = request.POST.get('youtube_url','').strip(),
            spotify_url    = request.POST.get('spotify_url','').strip(),
            published_date = request.POST.get('published_date'),
            is_featured    = request.POST.get('is_featured') == 'on',
        )
        ep.save()
        messages.success(request, f"Episode '{ep.title}' added!")
        return redirect('dashboard')
    return render(request, 'core/podcast_form.html', {'user_role': get_role(request), 'ep': None})

@admin_required
def podcast_edit(request, pk):
    ep = get_object_or_404(PodcastEpisode, pk=pk)
    if request.method == 'POST':
        ep.title         = request.POST.get('title','').strip()
        ep.guest_name    = request.POST.get('guest_name','').strip()
        ep.guest_title   = request.POST.get('guest_title','').strip()
        ep.episode_type  = request.POST.get('episode_type','video')
        ep.description   = request.POST.get('description','').strip()
        ep.content       = request.POST.get('content','').strip()
        ep.youtube_url   = request.POST.get('youtube_url','').strip()
        ep.spotify_url   = request.POST.get('spotify_url','').strip()
        ep.published_date= request.POST.get('published_date')
        ep.is_featured   = request.POST.get('is_featured') == 'on'
        ep.save()
        messages.success(request, f"Episode '{ep.title}' updated.")
        return redirect('dashboard')
    return render(request, 'core/podcast_form.html', {'ep': ep, 'user_role': get_role(request)})

@owner_required
def podcast_delete(request, pk):
    ep = get_object_or_404(PodcastEpisode, pk=pk)
    title = ep.title
    ep.delete()
    messages.success(request, f"Episode '{title}' deleted.")
    return redirect('dashboard')


# ── Testimonial CRUD ──────────────────────────────────────────
@admin_required
def testimonial_add(request):
    if request.method == 'POST':
        t = Testimonial(
            name      = request.POST.get('name','').strip(),
            role      = request.POST.get('role','').strip(),
            quote     = request.POST.get('quote','').strip(),
            is_active = request.POST.get('is_active') == 'on',
        )
        t.save()
        messages.success(request, f"Testimonial from {t.name} added!")
        return redirect('dashboard')
    return render(request, 'core/testimonial_form.html', {'t': None, 'user_role': get_role(request)})

@admin_required
def testimonial_edit(request, pk):
    t = get_object_or_404(Testimonial, pk=pk)
    if request.method == 'POST':
        t.name      = request.POST.get('name','').strip()
        t.role      = request.POST.get('role','').strip()
        t.quote     = request.POST.get('quote','').strip()
        t.is_active = request.POST.get('is_active') == 'on'
        t.save()
        messages.success(request, f"Testimonial from {t.name} updated.")
        return redirect('dashboard')
    return render(request, 'core/testimonial_form.html', {'t': t, 'user_role': get_role(request)})

@owner_required
def testimonial_delete(request, pk):
    t = get_object_or_404(Testimonial, pk=pk)
    name = t.name
    t.delete()
    messages.success(request, f"Testimonial from '{name}' deleted.")
    return redirect('dashboard')


# ── Donation CRUD ─────────────────────────────────────────────
@admin_required
def donation_add(request):
    if request.method == 'POST':
        d = DonationRecord(
            donor_name  = request.POST.get('donor_name','').strip(),
            donor_email = request.POST.get('donor_email','').strip(),
            amount      = request.POST.get('amount', 0),
            method      = request.POST.get('method','other'),
            note        = request.POST.get('note','').strip(),
        )
        d.save()
        messages.success(request, f"Donation of ${d.amount} logged!")
        return redirect('dashboard')
    return render(request, 'core/donation_form.html', {'d': None, 'user_role': get_role(request)})

@admin_required
def donation_edit(request, pk):
    d = get_object_or_404(DonationRecord, pk=pk)
    if request.method == 'POST':
        d.donor_name  = request.POST.get('donor_name','').strip()
        d.donor_email = request.POST.get('donor_email','').strip()
        d.amount      = request.POST.get('amount', d.amount)
        d.method      = request.POST.get('method', d.method)
        d.note        = request.POST.get('note','').strip()
        d.save()
        messages.success(request, f"Donation updated.")
        return redirect('dashboard')
    return render(request, 'core/donation_form.html', {'d': d, 'user_role': get_role(request)})

@owner_required
def donation_delete(request, pk):
    d = get_object_or_404(DonationRecord, pk=pk)
    d.delete()
    messages.success(request, "Donation deleted.")
    return redirect('dashboard')


# ── Staff management (owner only) ─────────────────────────────
@owner_required
def staff_manage(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            username   = request.POST.get('username','').strip()
            password   = request.POST.get('password','').strip()
            role       = request.POST.get('role','moderator')
            first_name = request.POST.get('first_name','').strip()
            last_name  = request.POST.get('last_name','').strip()
            if not username or not password:
                messages.error(request, "Username and password are required.")
            elif User.objects.filter(username=username).exists():
                messages.error(request, f"Username '{username}' is already taken.")
            elif role == 'owner':
                messages.error(request, "Cannot create another owner account.")
            else:
                user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
                StaffProfile.objects.create(user=user, role=role, created_by=request.user)
                messages.success(request, f"✅ {role.capitalize()} '{username}' created!")

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
                    messages.success(request, f"✅ '{name}' deleted.")
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
                    messages.success(request, f"✅ {target.username} is now {new_role}.")
            except User.DoesNotExist:
                messages.error(request, "User not found.")

        elif action == 'change_password':
            user_id  = request.POST.get('user_id')
            new_pass = request.POST.get('new_password','').strip()
            try:
                target = User.objects.get(id=user_id)
                if hasattr(target, 'profile') and target.profile.role == 'owner' and target != request.user:
                    messages.error(request, "Cannot change owner's password.")
                elif len(new_pass) < 6:
                    messages.error(request, "Password must be at least 6 characters.")
                else:
                    target.set_password(new_pass)
                    target.save()
                    messages.success(request, f"✅ Password changed for {target.username}.")
            except User.DoesNotExist:
                messages.error(request, "User not found.")

        return redirect('staff_manage')

    staff_members = StaffProfile.objects.select_related('user', 'created_by').order_by('role')
    return render(request, 'core/staff_manage.html', {'staff_members': staff_members})
