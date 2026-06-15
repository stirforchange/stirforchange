from django.urls import path
from core import views

urlpatterns = [
    # Public pages
    path('',              views.home,         name='home'),
    path('about/',        views.about,        name='about'),
    path('podcast/',      views.podcast,      name='podcast'),
    path('volunteer/',    views.volunteer,    name='volunteer'),
    path('business/',     views.business,     name='business'),
    path('donate/',       views.donate,       name='donate'),
    # Staff
    path('staff/login/',  views.staff_login,  name='staff_login'),
    path('staff/logout/', views.staff_logout, name='staff_logout'),
    path('staff/manage/', views.staff_manage, name='staff_manage'),
    path('dashboard/',    views.dashboard,    name='dashboard'),
]
