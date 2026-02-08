"""
URL configuration for dpc_fam_and_struct_webapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('search/', views.search, name='search'),
    path('pfam/<str:pfam_id>/', views.pfam_detail, name='pfam_detail'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('faqs/', TemplateView.as_view(template_name='faqs.html'), name='faqs'),
    path('admin/', admin.site.urls),
    path('dpcfam/', include('dpcfam.urls')),
    path('dpcstruct/', include('dpcstruct.urls')),
]
