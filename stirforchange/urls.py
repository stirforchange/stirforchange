from django.urls import path
from core import views

urlpatterns = [
    # Public
    path('',              views.home,         name='home'),
    path('about/',        views.about,        name='about'),
    path('podcast/',      views.podcast,      name='podcast'),
    path('volunteer/',    views.volunteer,    name='volunteer'),
    path('volunteer/<int:pk>/signup/', views.event_signup, name='event_signup'),
    path('business/',     views.business,     name='business'),
    path('donate/',       views.donate,       name='donate'),
    # Staff auth
    path('staff/login/',  views.staff_login,  name='staff_login'),
    path('staff/logout/', views.staff_logout, name='staff_logout'),
    path('staff/manage/', views.staff_manage, name='staff_manage'),
    # Dashboard
    path('dashboard/',    views.dashboard,    name='dashboard'),
    # Event CRUD
    path('dashboard/event/add/',                views.event_add,    name='event_add'),
    path('dashboard/event/<int:pk>/edit/',      views.event_edit,   name='event_edit'),
    path('dashboard/event/<int:pk>/delete/',    views.event_delete, name='event_delete'),
    path('dashboard/event/<int:pk>/',           views.event_detail, name='event_detail'),
    path('dashboard/signup/<int:pk>/delete/',   views.signup_delete, name='signup_delete'),
    # Business CRUD
    path('dashboard/business/<int:pk>/edit/',   views.business_edit,   name='business_edit'),
    path('dashboard/business/<int:pk>/delete/', views.business_delete, name='business_delete'),
    # Podcast CRUD
    path('dashboard/podcast/add/',              views.podcast_add,    name='podcast_add'),
    path('dashboard/podcast/<int:pk>/edit/',    views.podcast_edit,   name='podcast_edit'),
    path('dashboard/podcast/<int:pk>/delete/',  views.podcast_delete, name='podcast_delete'),
    # Testimonial CRUD
    path('dashboard/testimonial/add/',              views.testimonial_add,    name='testimonial_add'),
    path('dashboard/testimonial/<int:pk>/edit/',    views.testimonial_edit,   name='testimonial_edit'),
    path('dashboard/testimonial/<int:pk>/delete/',  views.testimonial_delete, name='testimonial_delete'),
    # Donation CRUD
    path('dashboard/donation/add/',             views.donation_add,    name='donation_add'),
    path('dashboard/donation/<int:pk>/edit/',   views.donation_edit,   name='donation_edit'),
    path('dashboard/donation/<int:pk>/delete/', views.donation_delete, name='donation_delete'),
]
