from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import PodcastEpisode, Testimonial, DonationRecord, VolunteerSignup, VolunteerEvent, BusinessSignup, StaffProfile
from .forms import VolunteerSignupForm, BusinessForm
from .emails import send_volunteer_confirmation, send_business_confirmation


def owner_required(fn):
    def wrap(request, *a, **kw):
        if not request.user.is_authenticated:
            return redirect('staff_login')
        try:
            if not request.user.profile.is_owner():
                messages.error(request, "Owner access required.")
                return redirect('dashboard')
        except Exception:
            return redirect('staff_login')
        return fn(request, *a, **kw)
    wrap.__name__ = fn.__name__
    return wrap


def admin_required(fn):
    def wrap(request, *a, **kw):
        if not request.user.is_authenticated:
            return redirect('staff_login')
        try:
            if not request.user.profile.is_admin():
                messages.error(request, "Admin access required.")
                return redirect('dashboard')
        except Exception:
            return redirect('staff_login')
        return fn(request, *a, **kw)
    wrap.__name__ = fn.__name__
    return wrap


def staff_required(fn):
    def wrap(request, *a, **kw):
        if not request.user.is_authenticated:
            return redirect('staff_login')
        try:
            if not request.user.profile.is_moderator():
                return redirect('staff_login')
        except Exception:
            return redirect('staff_login')
        return fn(request, *a, **kw)
    wrap.__name__ = fn.__name__
    return wrap


def get_role(request):
    try:
        return request.user.profile.role
    except Exception:
        return None


# ── Public ────────────────────────────────────────────────────
def home(request):
    testimonials = Testimonial.objects.filter(is_active=True)[:6]
    return render(request, 'core/home.html', {'testimonials': testimonials})


def about(request):
    return render(request, 'core/about.html')


def podcast(request):
    episodes = PodcastEpisode.objects.all()
    return render(request, 'core/podcast.html', {'episodes': episodes})


def donate(request):
    return render(request, 'core/donate.html')


def volunteer(request):
    today = timezone.now().date()
    events = VolunteerEvent.objects.filter(is_active=True, date__gte=today).order_by('date', 'start_time')
    return render(request, 'core/volunteer.html', {'events': events})


def event_signup(request, pk):
    event = get_object_or_404(VolunteerEvent, pk=pk, is_active=True)
    if event.is_full:
        messages.error(request, "Sorry, this event is fully booked!")
        return redirect('volunteer')
    if request.method == 'POST':
        form = VolunteerSignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if VolunteerSignup.objects.filter(event=event, email=email).exists():
                messages.error(request, "You have already signed up for this event!")
                return render(request, 'core/event_signup.html', {'event': event, 'form': form})
            conflicts = VolunteerSignup.objects.filter(
                email=email,
                event__date=event.date,
                event__start_time__lt=event.end_time,
                event__end_time__gt=event.start_time,
            ).exclude(event=event)
            if conflicts.exists():
                cn = conflicts.first().event.title
                messages.error(request, "You already have another event at this time: " + cn)
                return render(request, 'core/event_signup.html', {'event': event, 'form': form})
            if event.is_full:
                messages.error(request, "Sorry, this event just filled up!")
                return redirect('volunteer')
            signup = form.save(commit=False)
            signup.event = event
            signup.save()
            send_volunteer_confirmation(signup)
            messages.success(request, "You are registered for " + event.title + "! Check your email.")
            return redirect('volunteer')
    else:
        form = VolunteerSignupForm()
    return render(request, 'core/event_signup.html', {'event': event, 'form': form})


def business(request):
    if request.method == 'POST':
        form = BusinessForm(request.POST)
        if form.is_valid():
            biz = form.save()
            send_business_confirmation(biz)
            messages.success(request, "Thank you " + biz.business_name + "! We will be in touch soon.")
            return redirect('business')
    else:
        form = BusinessForm()
    return render(request, 'core/business.html', {'form': form})


# ── Auth ──────────────────────────────────────────────────────
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
                user.profile
                login(request, user)
                return redirect('dashboard')
            except StaffProfile.DoesNotExist:
                messages.error(request, "No staff role assigned.")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'core/staff_login.html')


def staff_logout(request):
    logout(request)
    return redirect('staff_login')


# ── Dashboard ─────────────────────────────────────────────────
@staff_required
def dashboard(request):
    now = timezone.now()
    today = now.date()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    user_role = get_role(request)

    upcoming_events = VolunteerEvent.objects.filter(date__gte=today).order_by('date', 'start_time')
    past_events = VolunteerEvent.objects.filter(date__lt=today).order_by('-date')[:5]
    total_volunteers = VolunteerSignup.objects.count()
    new_volunteers = VolunteerSignup.objects.filter(created_at__gte=week_start).count()

    businesses = BusinessSignup.objects.order_by('-created_at')
    total_businesses = businesses.count()
    new_businesses = businesses.filter(created_at__gte=week_start).count()
    recent_businesses = businesses[:10]

    total_donations = month_donations = donation_count = 0
    recent_donations = []
    by_method = []
    total_episodes = testimonial_count = 0
    recent_episodes = []
    testimonials = []
    staff_members = []

    if user_role in ('owner', 'admin'):
        total_donations = DonationRecord.objects.aggregate(s=Sum('amount'))['s'] or 0
        month_donations = DonationRecord.objects.filter(created_at__gte=month_start).aggregate(s=Sum('amount'))['s'] or 0
        donation_count = DonationRecord.objects.count()
        recent_donations = DonationRecord.objects.order_by('-created_at')[:10]
        by_method = DonationRecord.objects.values('method').annotate(total=Sum('amount'), count=Count('id')).order_by('-total')
        total_episodes = PodcastEpisode.objects.count()
        recent_episodes = PodcastEpisode.objects.order_by('-published_date')[:10]
        testimonial_count = Testimonial.objects.count()
        testimonials = Testimonial.objects.order_by('-created_at')[:10]

    if user_role == 'owner':
        staff_members = StaffProfile.objects.select_related('user', 'created_by').order_by('role', 'user__username')

    return render(request, 'core/dashboard.html', {
        'user_role': user_role,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'total_volunteers': total_volunteers,
        'new_volunteers': new_volunteers,
        'total_businesses': total_businesses,
        'new_businesses': new_businesses,
        'recent_businesses': recent_businesses,
        'total_donations': total_donations,
        'month_donations': month_donations,
        'donation_count': donation_count,
        'recent_donations': recent_donations,
        'by_method': by_method,
        'total_episodes': total_episodes,
        'recent_episodes': recent_episodes,
        'testimonial_count': testimonial_count,
        'testimonials': testimonials,
        'staff_members': staff_members,
    })


# ── Events ────────────────────────────────────────────────────
@admin_required
def event_add(request):
    if request.method == 'POST':
        try:
            ev = VolunteerEvent(
                title=request.POST.get('title', '').strip(),
                description=request.POST.get('description', '').strip(),
                date=request.POST.get('date'),
                start_time=request.POST.get('start_time'),
                end_time=request.POST.get('end_time'),
                location=request.POST.get('location', '').strip(),
                max_volunteers=int(request.POST.get('max_volunteers', 10)),
                what_to_bring=request.POST.get('what_to_bring', '').strip(),
                food_type=request.POST.get('food_type', '').strip(),
                is_active=request.POST.get('is_active') == 'on',
                created_by=request.user,
            )
            ev.save()
            messages.success(request, "Event created!")
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, "Error: " + str(e))
    return render(request, 'core/event_form.html', {'ev': None, 'user_role': get_role(request)})


@admin_required
def event_edit(request, pk):
    ev = get_object_or_404(VolunteerEvent, pk=pk)
    if request.method == 'POST':
        try:
            ev.title = request.POST.get('title', '').strip()
            ev.description = request.POST.get('description', '').strip()
            ev.date = request.POST.get('date')
            ev.start_time = request.POST.get('start_time')
            ev.end_time = request.POST.get('end_time')
            ev.location = request.POST.get('location', '').strip()
            ev.max_volunteers = int(request.POST.get('max_volunteers', ev.max_volunteers))
            ev.what_to_bring = request.POST.get('what_to_bring', '').strip()
            ev.food_type = request.POST.get('food_type', '').strip()
            ev.is_active = request.POST.get('is_active') == 'on'
            ev.save()
            messages.success(request, "Event updated.")
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, "Error: " + str(e))
    return render(request, 'core/event_form.html', {'ev': ev, 'user_role': get_role(request)})


@owner_required
def event_delete(request, pk):
    ev = get_object_or_404(VolunteerEvent, pk=pk)
    ev.delete()
    messages.success(request, "Event deleted.")
    return redirect('dashboard')


@admin_required
def event_detail(request, pk):
    ev = get_object_or_404(VolunteerEvent, pk=pk)
    signups = ev.signups.order_by('-created_at')
    return render(request, 'core/event_detail.html', {'ev': ev, 'signups': signups, 'user_role': get_role(request)})


@owner_required
def signup_delete(request, pk):
    signup = get_object_or_404(VolunteerSignup, pk=pk)
    event_pk = signup.event.pk
    signup.delete()
    messages.success(request, "Volunteer removed.")
    return redirect('event_detail', pk=event_pk)


# ── Business ──────────────────────────────────────────────────
@admin_required
def business_edit(request, pk):
    biz = get_object_or_404(BusinessSignup, pk=pk)
    if request.method == 'POST':
        for f in ['business_name', 'contact_name', 'email', 'phone', 'business_type',
                  'street_address', 'city', 'state', 'zip_code', 'frequency', 'food_types', 'message']:
            setattr(biz, f, request.POST.get(f, '').strip())
        biz.save()
        messages.success(request, "Business updated.")
        return redirect('dashboard')
    return render(request, 'core/business_edit.html', {'biz': biz, 'user_role': get_role(request)})


@owner_required
def business_delete(request, pk):
    get_object_or_404(BusinessSignup, pk=pk).delete()
    messages.success(request, "Business deleted.")
    return redirect('dashboard')


# ── Podcast ───────────────────────────────────────────────────
@admin_required
def podcast_add(request):
    if request.method == 'POST':
        try:
            ep = PodcastEpisode(
                title=request.POST.get('title', '').strip(),
                guest_name=request.POST.get('guest_name', '').strip(),
                guest_title=request.POST.get('guest_title', '').strip(),
                episode_type=request.POST.get('episode_type', 'video'),
                description=request.POST.get('description', '').strip(),
                content=request.POST.get('content', '').strip(),
                youtube_url=request.POST.get('youtube_url', '').strip(),
                spotify_url=request.POST.get('spotify_url', '').strip(),
                published_date=request.POST.get('published_date'),
                is_featured=request.POST.get('is_featured') == 'on',
            )
            ep.save()
            messages.success(request, "Episode added!")
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, "Error: " + str(e))
    return render(request, 'core/podcast_form.html', {'ep': None, 'user_role': get_role(request)})


@admin_required
def podcast_edit(request, pk):
    ep = get_object_or_404(PodcastEpisode, pk=pk)
    if request.method == 'POST':
        ep.title = request.POST.get('title', '').strip()
        ep.guest_name = request.POST.get('guest_name', '').strip()
        ep.guest_title = request.POST.get('guest_title', '').strip()
        ep.episode_type = request.POST.get('episode_type', 'video')
        ep.description = request.POST.get('description', '').strip()
        ep.content = request.POST.get('content', '').strip()
        ep.youtube_url = request.POST.get('youtube_url', '').strip()
        ep.spotify_url = request.POST.get('spotify_url', '').strip()
        ep.published_date = request.POST.get('published_date')
        ep.is_featured = request.POST.get('is_featured') == 'on'
        ep.save()
        messages.success(request, "Episode updated.")
        return redirect('dashboard')
    return render(request, 'core/podcast_form.html', {'ep': ep, 'user_role': get_role(request)})


@owner_required
def podcast_delete(request, pk):
    get_object_or_404(PodcastEpisode, pk=pk).delete()
    messages.success(request, "Episode deleted.")
    return redirect('dashboard')


# ── Testimonials ──────────────────────────────────────────────
@admin_required
def testimonial_add(request):
    if request.method == 'POST':
        t = Testimonial(
            name=request.POST.get('name', '').strip(),
            role=request.POST.get('role', '').strip(),
            quote=request.POST.get('quote', '').strip(),
            is_active=request.POST.get('is_active') == 'on',
        )
        t.save()
        messages.success(request, "Testimonial added!")
        return redirect('dashboard')
    return render(request, 'core/testimonial_form.html', {'t': None, 'user_role': get_role(request)})


@admin_required
def testimonial_edit(request, pk):
    t = get_object_or_404(Testimonial, pk=pk)
    if request.method == 'POST':
        t.name = request.POST.get('name', '').strip()
        t.role = request.POST.get('role', '').strip()
        t.quote = request.POST.get('quote', '').strip()
        t.is_active = request.POST.get('is_active') == 'on'
        t.save()
        messages.success(request, "Testimonial updated.")
        return redirect('dashboard')
    return render(request, 'core/testimonial_form.html', {'t': t, 'user_role': get_role(request)})


@owner_required
def testimonial_delete(request, pk):
    get_object_or_404(Testimonial, pk=pk).delete()
    messages.success(request, "Testimonial deleted.")
    return redirect('dashboard')


# ── Donations ─────────────────────────────────────────────────
@admin_required
def donation_add(request):
    if request.method == 'POST':
        try:
            d = DonationRecord(
                donor_name=request.POST.get('donor_name', '').strip(),
                donor_email=request.POST.get('donor_email', '').strip(),
                amount=request.POST.get('amount', 0),
                method=request.POST.get('method', 'other'),
                note=request.POST.get('note', '').strip(),
            )
            d.save()
            messages.success(request, "Donation logged!")
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, "Error: " + str(e))
    return render(request, 'core/donation_form.html', {'d': None, 'user_role': get_role(request)})


@admin_required
def donation_edit(request, pk):
    d = get_object_or_404(DonationRecord, pk=pk)
    if request.method == 'POST':
        d.donor_name = request.POST.get('donor_name', '').strip()
        d.donor_email = request.POST.get('donor_email', '').strip()
        d.amount = request.POST.get('amount', d.amount)
        d.method = request.POST.get('method', d.method)
        d.note = request.POST.get('note', '').strip()
        d.save()
        messages.success(request, "Donation updated.")
        return redirect('dashboard')
    return render(request, 'core/donation_form.html', {'d': d, 'user_role': get_role(request)})


@owner_required
def donation_delete(request, pk):
    get_object_or_404(DonationRecord, pk=pk).delete()
    messages.success(request, "Donation deleted.")
    return redirect('dashboard')


# ── Staff ─────────────────────────────────────────────────────
@owner_required
def staff_manage(request):
    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'create':
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()
            role = request.POST.get('role', 'moderator')
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            if not username or not password:
                messages.error(request, "Username and password required.")
            elif User.objects.filter(username=username).exists():
                messages.error(request, "Username already taken.")
            elif role == 'owner':
                messages.error(request, "Cannot create another owner.")
            else:
                u = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
                StaffProfile.objects.create(user=u, role=role, created_by=request.user)
                messages.success(request, "Account created!")

        elif action == 'edit_info':
            try:
                target = User.objects.get(id=request.POST.get('user_id'))
                if hasattr(target, 'profile') and target.profile.role == 'owner':
                    messages.error(request, "Cannot edit owner account.")
                else:
                    fn = request.POST.get('first_name', '').strip()
                    ln = request.POST.get('last_name', '').strip()
                    un = request.POST.get('username', '').strip()
                    if un and User.objects.filter(username=un).exclude(id=target.id).exists():
                        messages.error(request, "Username already taken.")
                    else:
                        if fn: target.first_name = fn
                        if ln: target.last_name = ln
                        if un: target.username = un
                        target.save()
                        messages.success(request, "Updated.")
            except User.DoesNotExist:
                messages.error(request, "User not found.")

        elif action == 'change_role':
            try:
                target = User.objects.get(id=request.POST.get('user_id'))
                new_role = request.POST.get('new_role', '')
                if new_role == 'owner':
                    messages.error(request, "Cannot assign owner role.")
                elif hasattr(target, 'profile') and target.profile.role == 'owner':
                    messages.error(request, "Cannot change owner role.")
                else:
                    target.profile.role = new_role
                    target.profile.save()
                    messages.success(request, target.username + " is now " + new_role + ".")
            except User.DoesNotExist:
                messages.error(request, "User not found.")

        elif action == 'change_password':
            try:
                target = User.objects.get(id=request.POST.get('user_id'))
                new_pass = request.POST.get('new_password', '').strip()
                if hasattr(target, 'profile') and target.profile.role == 'owner' and target != request.user:
                    messages.error(request, "Cannot change owner password.")
                elif len(new_pass) < 6:
                    messages.error(request, "Password must be at least 6 characters.")
                else:
                    target.set_password(new_pass)
                    target.save()
                    messages.success(request, "Password changed.")
            except User.DoesNotExist:
                messages.error(request, "User not found.")

        elif action == 'delete':
            try:
                target = User.objects.get(id=request.POST.get('user_id'))
                if target == request.user:
                    messages.error(request, "Cannot delete your own account.")
                elif hasattr(target, 'profile') and target.profile.role == 'owner':
                    messages.error(request, "Cannot delete owner.")
                else:
                    name = target.username
                    target.delete()
                    messages.success(request, name + " deleted.")
            except User.DoesNotExist:
                messages.error(request, "User not found.")

        return redirect('staff_manage')

    staff_members = StaffProfile.objects.select_related('user', 'created_by').order_by('role')
    return render(request, 'core/staff_manage.html', {'staff_members': staff_members})
