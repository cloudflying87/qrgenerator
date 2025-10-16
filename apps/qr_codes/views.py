"""
Views for QR code generation and management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count
from django.utils import timezone
from django.urls import reverse
import structlog

from .models import QRCode, QRScan
from .utils import (
    generate_qr_code,
    parse_user_agent,
    get_client_ip,
    generate_visitor_id,
    check_password
)

logger = structlog.get_logger(__name__)


@login_required
def qr_code_list(request):
    """List all QR codes for the current user."""
    qr_codes = QRCode.objects.filter(user=request.user).select_related('user')

    # Filter by search query
    search_query = request.GET.get('search', '')
    if search_query:
        qr_codes = qr_codes.filter(
            Q(name__icontains=search_query) |
            Q(destination_url__icontains=search_query) |
            Q(tags__icontains=search_query)
        )

    # Filter by type
    qr_type = request.GET.get('type', '')
    if qr_type in ['static', 'dynamic']:
        qr_codes = qr_codes.filter(qr_type=qr_type)

    # Filter by status
    status = request.GET.get('status', '')
    if status in ['active', 'paused', 'expired']:
        qr_codes = qr_codes.filter(status=status)

    context = {
        'qr_codes': qr_codes,
        'search_query': search_query,
        'selected_type': qr_type,
        'selected_status': status,
    }

    return render(request, 'qr_codes/qr_code_list.html', context)


@login_required
def qr_code_create(request):
    """Create a new QR code."""
    if request.method == 'POST':
        # Extract form data
        name = request.POST.get('name')
        qr_type = request.POST.get('qr_type', 'dynamic')
        destination_url = request.POST.get('destination_url')
        description = request.POST.get('description', '')
        tags = request.POST.get('tags', '')

        # Customization
        size = int(request.POST.get('size', 300))
        error_correction = request.POST.get('error_correction', 'M')
        foreground_color = request.POST.get('foreground_color', '#000000')
        background_color = request.POST.get('background_color', '#FFFFFF')

        # Limits (optional)
        max_scans = request.POST.get('max_scans', '')
        expires_at = request.POST.get('expires_at', '')
        password = request.POST.get('password', '')

        # Validation
        if not name or not destination_url:
            messages.error(request, 'Name and destination URL are required.')
            return render(request, 'qr_codes/qr_code_create.html')

        # Create QR code
        qr_code = QRCode.objects.create(
            user=request.user,
            name=name,
            qr_type=qr_type,
            destination_url=destination_url,
            description=description,
            tags=tags,
            size=size,
            error_correction=error_correction,
            foreground_color=foreground_color,
            background_color=background_color,
            max_scans=int(max_scans) if max_scans else None,
            expires_at=expires_at if expires_at else None,
            password=password,
        )

        logger.info(
            "qr_code_created",
            qr_code_id=qr_code.id,
            qr_type=qr_type,
            user_id=request.user.id
        )

        messages.success(request, f'QR code "{name}" created successfully!')
        return redirect('qr_codes:detail', pk=qr_code.pk)

    return render(request, 'qr_codes/qr_code_create.html')


@login_required
def qr_code_detail(request, pk):
    """View details of a specific QR code."""
    qr_code = get_object_or_404(QRCode, pk=pk, user=request.user)

    # Get recent scans
    recent_scans = qr_code.scans.all()[:10]

    # Get scan statistics
    scan_stats = {
        'total': qr_code.total_scans,
        'unique': qr_code.unique_scans,
        'last_scan': qr_code.last_scanned_at,
    }

    # Get device breakdown
    device_stats = qr_code.scans.values('device_type').annotate(
        count=Count('id')
    ).order_by('-count')

    # Get browser breakdown
    browser_stats = qr_code.scans.values('browser').annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    context = {
        'qr_code': qr_code,
        'recent_scans': recent_scans,
        'scan_stats': scan_stats,
        'device_stats': device_stats,
        'browser_stats': browser_stats,
        'short_url': qr_code.get_full_short_url(request) if qr_code.qr_type == 'dynamic' else None,
    }

    return render(request, 'qr_codes/qr_code_detail.html', context)


@login_required
def qr_code_edit(request, pk):
    """Edit an existing QR code."""
    qr_code = get_object_or_404(QRCode, pk=pk, user=request.user)

    if request.method == 'POST':
        # Update fields
        qr_code.name = request.POST.get('name', qr_code.name)
        qr_code.destination_url = request.POST.get('destination_url', qr_code.destination_url)
        qr_code.description = request.POST.get('description', '')
        qr_code.tags = request.POST.get('tags', '')
        qr_code.status = request.POST.get('status', qr_code.status)

        # Customization
        qr_code.size = int(request.POST.get('size', qr_code.size))
        qr_code.error_correction = request.POST.get('error_correction', qr_code.error_correction)
        qr_code.foreground_color = request.POST.get('foreground_color', qr_code.foreground_color)
        qr_code.background_color = request.POST.get('background_color', qr_code.background_color)

        # Limits
        max_scans = request.POST.get('max_scans', '')
        qr_code.max_scans = int(max_scans) if max_scans else None

        expires_at = request.POST.get('expires_at', '')
        qr_code.expires_at = expires_at if expires_at else None

        qr_code.password = request.POST.get('password', '')

        qr_code.save()

        logger.info(
            "qr_code_updated",
            qr_code_id=qr_code.id,
            user_id=request.user.id
        )

        messages.success(request, 'QR code updated successfully!')
        return redirect('qr_codes:detail', pk=qr_code.pk)

    context = {'qr_code': qr_code}
    return render(request, 'qr_codes/qr_code_edit.html', context)


@login_required
@require_http_methods(["POST"])
def qr_code_delete(request, pk):
    """Delete a QR code."""
    qr_code = get_object_or_404(QRCode, pk=pk, user=request.user)
    name = qr_code.name
    qr_code.delete()

    logger.info(
        "qr_code_deleted",
        qr_code_id=pk,
        user_id=request.user.id
    )

    messages.success(request, f'QR code "{name}" deleted successfully!')
    return redirect('qr_codes:list')


@login_required
def qr_code_download(request, pk):
    """Download QR code as image."""
    qr_code = get_object_or_404(QRCode, pk=pk, user=request.user)

    # Determine what data to encode
    if qr_code.qr_type == 'static':
        data = qr_code.destination_url
    else:
        data = qr_code.get_full_short_url(request)

    # Generate QR code
    qr_image = generate_qr_code(
        data=data,
        size=qr_code.size,
        error_correction=qr_code.error_correction,
        foreground_color=qr_code.foreground_color,
        background_color=qr_code.background_color,
    )

    # Create response
    response = HttpResponse(qr_image.getvalue(), content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="{qr_code.name}_qr.png"'

    logger.info(
        "qr_code_downloaded",
        qr_code_id=qr_code.id,
        user_id=request.user.id
    )

    return response


def qr_redirect(request, short_code):
    """
    Redirect view for dynamic QR codes.
    This is the public-facing URL that QR codes point to.
    """
    # Get QR code by short code
    try:
        qr_code = QRCode.objects.get(short_code=short_code)
    except QRCode.DoesNotExist:
        logger.warning("qr_redirect_not_found", short_code=short_code)
        raise Http404("QR code not found")

    # Check if QR code can be scanned
    can_scan, error_message = qr_code.can_scan()
    if not can_scan:
        logger.warning(
            "qr_redirect_blocked",
            short_code=short_code,
            reason=error_message
        )
        return render(request, 'qr_codes/qr_error.html', {
            'error_message': error_message,
            'qr_code': qr_code,
        })

    # Check password if required
    if qr_code.password:
        # Check if password was provided
        password = request.GET.get('password', '')
        if not password or not check_password(qr_code.password, password):
            return render(request, 'qr_codes/qr_password.html', {
                'qr_code': qr_code,
                'short_code': short_code,
            })

    # Parse user agent
    user_agent_string = request.META.get('HTTP_USER_AGENT', '')
    ua_info = parse_user_agent(user_agent_string)

    # Generate visitor ID
    visitor_id = generate_visitor_id(request)

    # Check if this is a unique visitor
    is_unique_visitor = not QRScan.objects.filter(
        qr_code=qr_code,
        visitor_id=visitor_id
    ).exists()

    # Record the scan
    scan = QRScan.objects.create(
        qr_code=qr_code,
        ip_address=get_client_ip(request),
        user_agent=user_agent_string,
        referer=request.META.get('HTTP_REFERER', ''),
        device_type=ua_info['device_type'],
        browser=ua_info['browser'],
        operating_system=ua_info['operating_system'],
        visitor_id=visitor_id,
        is_unique_visitor=is_unique_visitor,
        was_successful=True,
    )

    # Update QR code scan counts
    qr_code.increment_scan_count(is_unique=is_unique_visitor)

    logger.info(
        "qr_redirect_success",
        qr_code_id=qr_code.id,
        short_code=short_code,
        device_type=ua_info['device_type'],
        is_unique=is_unique_visitor
    )

    # Redirect to destination
    return redirect(qr_code.destination_url)


@login_required
def qr_analytics(request, pk):
    """Detailed analytics for a QR code."""
    qr_code = get_object_or_404(QRCode, pk=pk, user=request.user)

    # Time range filter
    days = int(request.GET.get('days', 7))
    start_date = timezone.now() - timezone.timedelta(days=days)

    # Get scans in time range
    scans = qr_code.scans.filter(scanned_at__gte=start_date)

    # Device breakdown
    device_stats = scans.values('device_type').annotate(
        count=Count('id')
    ).order_by('-count')

    # Browser breakdown
    browser_stats = scans.values('browser').annotate(
        count=Count('id')
    ).order_by('-count')

    # OS breakdown
    os_stats = scans.values('operating_system').annotate(
        count=Count('id')
    ).order_by('-count')

    # Scans over time (by day)
    from django.db.models.functions import TruncDate
    scans_by_date = scans.annotate(
        date=TruncDate('scanned_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')

    context = {
        'qr_code': qr_code,
        'days': days,
        'total_scans': scans.count(),
        'device_stats': device_stats,
        'browser_stats': browser_stats,
        'os_stats': os_stats,
        'scans_by_date': list(scans_by_date),
    }

    return render(request, 'qr_codes/qr_analytics.html', context)
