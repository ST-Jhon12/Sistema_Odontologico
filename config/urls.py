"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from django.contrib.auth.views import LogoutView
from django.urls import path, reverse_lazy
from django.views.generic import RedirectView

from control import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url=reverse_lazy('dashboard'), permanent=False)),
    path('cuenta/ingresar/', views.RememberMeLoginView.as_view(), name='login'),
    path('cuenta/registrar/', views.register, name='register'),
    path('cuenta/salir/', LogoutView.as_view(), name='logout'),
    path('panel/', views.dashboard, name='dashboard'),
    path('reportes/', views.reports, name='reports'),
    path('reportes/<slug:slug>/', views.report_detail, name='report_detail'),
    path('<slug:slug>/', views.RecordListView.as_view(), name='records'),
    path('<slug:slug>/nuevo/', views.RecordFormView.as_view(), name='record_create'),
    path(
        '<slug:slug>/<int:pk>/editar/',
        views.RecordFormView.as_view(),
        name='record_update',
    ),
    path(
        '<slug:slug>/<int:pk>/eliminar/',
        views.RecordDeleteView.as_view(),
        name='record_delete',
    ),
]
