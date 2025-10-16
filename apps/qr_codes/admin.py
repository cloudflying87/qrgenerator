"""
Admin interface for QR Code management.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import QRCode, QRScan


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    """Admin interface for QR codes."""

    list_display = [
        'name',
        'qr_type',
        'user',
        'status',
        'total_scans',
        'unique_scans',
        'short_code_link',
        'created_at',
    ]
    list_filter = ['qr_type', 'status', 'created_at']
    search_fields = ['name', 'destination_url', 'short_code', 'tags']
    readonly_fields = [
        'short_code',
        'total_scans',
        'unique_scans',
        'last_scanned_at',
        'created_at',
        'updated_at',
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'qr_type', 'description', 'tags')
        }),
        ('URLs', {
            'fields': ('destination_url', 'short_code')
        }),
        ('Customization', {
            'fields': (
                'size',
                'error_correction',
                'foreground_color',
                'background_color',
            ),
            'classes': ('collapse',),
        }),
        ('Status & Limits', {
            'fields': ('status', 'max_scans', 'expires_at', 'password')
        }),
        ('Statistics', {
            'fields': (
                'total_scans',
                'unique_scans',
                'last_scanned_at',
            ),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def short_code_link(self, obj):
        """Display clickable short code link."""
        if obj.qr_type == 'dynamic' and obj.short_code:
            url = reverse('qr_codes:redirect', kwargs={'short_code': obj.short_code})
            return format_html('<a href="{}" target="_blank">{}</a>', url, obj.short_code)
        return '-'
    short_code_link.short_description = 'Short URL'


@admin.register(QRScan)
class QRScanAdmin(admin.ModelAdmin):
    """Admin interface for QR scans."""

    list_display = [
        'qr_code',
        'device_type',
        'browser',
        'operating_system',
        'ip_address',
        'was_successful',
        'scanned_at',
    ]
    list_filter = ['was_successful', 'device_type', 'browser', 'scanned_at']
    search_fields = ['qr_code__name', 'ip_address', 'user_agent']
    readonly_fields = [
        'qr_code',
        'ip_address',
        'user_agent',
        'referer',
        'device_type',
        'browser',
        'operating_system',
        'country',
        'city',
        'was_successful',
        'error_message',
        'visitor_id',
        'is_unique_visitor',
        'scanned_at',
    ]

    def has_add_permission(self, request):
        """Scans are created automatically, not manually."""
        return False

    def has_change_permission(self, request, obj=None):
        """Scans are read-only."""
        return False
