"""
URL patterns for QR codes app.
"""
from django.urls import path
from . import views

app_name = 'qr_codes'

urlpatterns = [
    # QR code management (authenticated)
    path('', views.qr_code_list, name='list'),
    path('create/', views.qr_code_create, name='create'),
    path('<int:pk>/', views.qr_code_detail, name='detail'),
    path('<int:pk>/edit/', views.qr_code_edit, name='edit'),
    path('<int:pk>/delete/', views.qr_code_delete, name='delete'),
    path('<int:pk>/download/', views.qr_code_download, name='download'),
    path('<int:pk>/analytics/', views.qr_analytics, name='analytics'),

    # Public redirect (no authentication required)
    path('r/<str:short_code>/', views.qr_redirect, name='redirect'),
]
