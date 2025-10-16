"""
Authentication views for web interface.
"""
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import UserRegistrationForm, UserLoginForm


def register_view(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('qr_codes:list')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to QR Generator!')
            return redirect('qr_codes:list')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request):
    """User profile view."""
    # Calculate stats
    total_qr_codes = request.user.qr_codes.count()
    dynamic_count = request.user.qr_codes.filter(qr_type='dynamic').count()
    static_count = request.user.qr_codes.filter(qr_type='static').count()
    active_count = request.user.qr_codes.filter(status='active').count()

    context = {
        'total_qr_codes': total_qr_codes,
        'dynamic_count': dynamic_count,
        'static_count': static_count,
        'active_count': active_count,
    }

    return render(request, 'accounts/profile.html', context)
