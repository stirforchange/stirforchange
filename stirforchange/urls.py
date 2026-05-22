from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('admin/',     admin.site.urls),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('',           views.home,      name='home'),
    path('about/',     views.about,     name='about'),
    path('podcast/',   views.podcast,   name='podcast'),
    path('volunteer/', views.volunteer, name='volunteer'),
    path('business/',  views.business,  name='business'),
    path('donate/',    views.donate,    name='donate'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
