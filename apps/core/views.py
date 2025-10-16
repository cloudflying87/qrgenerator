"""
Core app views.
"""
from django.shortcuts import render


def home(request):
    """Homepage view."""
    context = {
        'project_name': 'qrgenerator',
    }
    return render(request, 'core/home.html', context)
