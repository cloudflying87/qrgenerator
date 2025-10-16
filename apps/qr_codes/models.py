"""
QR Code models for qrgenerator.
Supports both static and dynamic QR codes with analytics.
"""
import secrets
import string
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
import structlog

logger = structlog.get_logger(__name__)


def generate_short_code(length=8):
    """Generate a random short code for dynamic QR codes."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


class QRCode(models.Model):
    """
    Base QR Code model supporting both static and dynamic types.

    Static QR: Contains destination URL directly in the QR code
    Dynamic QR: Contains short URL that redirects to destination (trackable)
    """
    QR_TYPE_CHOICES = [
        ('static', 'Static QR Code'),
        ('dynamic', 'Dynamic QR Code'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('expired', 'Expired'),
    ]

    # Core fields
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='qr_codes',
        verbose_name=_('user')
    )
    name = models.CharField(
        _('name'),
        max_length=255,
        help_text=_('Internal name for this QR code')
    )
    qr_type = models.CharField(
        _('QR type'),
        max_length=10,
        choices=QR_TYPE_CHOICES,
        default='dynamic'
    )

    # URLs
    destination_url = models.URLField(
        _('destination URL'),
        max_length=2048,
        help_text=_('The final destination URL')
    )
    short_code = models.CharField(
        _('short code'),
        max_length=20,
        unique=True,
        blank=True,
        help_text=_('Unique short code for dynamic QR codes')
    )

    # QR code customization
    size = models.IntegerField(
        _('size'),
        default=300,
        help_text=_('Size of QR code in pixels (e.g., 300)')
    )
    error_correction = models.CharField(
        _('error correction'),
        max_length=1,
        choices=[
            ('L', 'Low (7%)'),
            ('M', 'Medium (15%)'),
            ('Q', 'Quartile (25%)'),
            ('H', 'High (30%)'),
        ],
        default='M',
        help_text=_('Error correction level')
    )
    foreground_color = models.CharField(
        _('foreground color'),
        max_length=7,
        default='#000000',
        help_text=_('QR code color in hex format')
    )
    background_color = models.CharField(
        _('background color'),
        max_length=7,
        default='#FFFFFF',
        help_text=_('Background color in hex format')
    )

    # Status and limits
    status = models.CharField(
        _('status'),
        max_length=10,
        choices=STATUS_CHOICES,
        default='active'
    )
    max_scans = models.IntegerField(
        _('max scans'),
        null=True,
        blank=True,
        help_text=_('Maximum number of scans (null = unlimited)')
    )
    expires_at = models.DateTimeField(
        _('expires at'),
        null=True,
        blank=True,
        help_text=_('Expiration date/time (null = never expires)')
    )

    # Password protection (for dynamic QR codes)
    password = models.CharField(
        _('password'),
        max_length=128,
        blank=True,
        help_text=_('Optional password to access the QR code')
    )

    # Metadata
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_('Optional description or notes')
    )
    tags = models.CharField(
        _('tags'),
        max_length=255,
        blank=True,
        help_text=_('Comma-separated tags for organization')
    )

    # Statistics (cached for performance)
    total_scans = models.IntegerField(_('total scans'), default=0)
    unique_scans = models.IntegerField(_('unique scans'), default=0)
    last_scanned_at = models.DateTimeField(
        _('last scanned at'),
        null=True,
        blank=True
    )

    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('QR code')
        verbose_name_plural = _('QR codes')
        db_table = 'qr_codes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['short_code']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.name} ({self.qr_type})"

    def save(self, *args, **kwargs):
        """Generate short code for dynamic QR codes."""
        if self.qr_type == 'dynamic' and not self.short_code:
            # Generate unique short code
            while True:
                code = generate_short_code()
                if not QRCode.objects.filter(short_code=code).exists():
                    self.short_code = code
                    break

        super().save(*args, **kwargs)

        logger.info(
            "qr_code_saved",
            qr_code_id=self.id,
            qr_type=self.qr_type,
            user_id=self.user_id,
            short_code=self.short_code
        )

    def get_short_url(self):
        """Get the short URL for this QR code (dynamic only)."""
        if self.qr_type == 'dynamic' and self.short_code:
            return reverse('qr_codes:redirect', kwargs={'short_code': self.short_code})
        return None

    def get_full_short_url(self, request=None):
        """Get the full short URL including domain."""
        short_url = self.get_short_url()
        if short_url and request:
            return request.build_absolute_uri(short_url)
        return short_url

    def can_scan(self):
        """Check if QR code can be scanned."""
        from django.utils import timezone

        if self.status != 'active':
            return False, "QR code is not active"

        if self.expires_at and self.expires_at < timezone.now():
            return False, "QR code has expired"

        if self.max_scans and self.total_scans >= self.max_scans:
            return False, "Maximum scan limit reached"

        return True, None

    def increment_scan_count(self, is_unique=False):
        """Increment scan counters."""
        self.total_scans += 1
        if is_unique:
            self.unique_scans += 1
        from django.utils import timezone
        self.last_scanned_at = timezone.now()
        self.save(update_fields=['total_scans', 'unique_scans', 'last_scanned_at'])


class QRScan(models.Model):
    """
    Individual scan tracking for analytics.
    Records each scan with metadata for detailed analytics.
    """
    qr_code = models.ForeignKey(
        QRCode,
        on_delete=models.CASCADE,
        related_name='scans',
        verbose_name=_('QR code')
    )

    # Request metadata
    ip_address = models.GenericIPAddressField(
        _('IP address'),
        null=True,
        blank=True
    )
    user_agent = models.TextField(
        _('user agent'),
        blank=True
    )
    referer = models.URLField(
        _('referer'),
        max_length=2048,
        blank=True
    )

    # Device information (parsed from user agent)
    device_type = models.CharField(
        _('device type'),
        max_length=20,
        blank=True,
        help_text=_('mobile, tablet, desktop')
    )
    browser = models.CharField(
        _('browser'),
        max_length=50,
        blank=True
    )
    operating_system = models.CharField(
        _('operating system'),
        max_length=50,
        blank=True
    )

    # Location (optional - could integrate with GeoIP)
    country = models.CharField(
        _('country'),
        max_length=100,
        blank=True
    )
    city = models.CharField(
        _('city'),
        max_length=100,
        blank=True
    )

    # Scan result
    was_successful = models.BooleanField(
        _('was successful'),
        default=True
    )
    error_message = models.TextField(
        _('error message'),
        blank=True
    )

    # Unique visitor tracking (simple cookie-based)
    visitor_id = models.CharField(
        _('visitor ID'),
        max_length=64,
        blank=True,
        help_text=_('Unique visitor identifier')
    )
    is_unique_visitor = models.BooleanField(
        _('is unique visitor'),
        default=False
    )

    # Timestamp
    scanned_at = models.DateTimeField(_('scanned at'), auto_now_add=True)

    class Meta:
        verbose_name = _('QR scan')
        verbose_name_plural = _('QR scans')
        db_table = 'qr_scans'
        ordering = ['-scanned_at']
        indexes = [
            models.Index(fields=['qr_code', '-scanned_at']),
            models.Index(fields=['visitor_id']),
            models.Index(fields=['ip_address']),
        ]

    def __str__(self):
        return f"Scan of {self.qr_code.name} at {self.scanned_at}"

    def save(self, *args, **kwargs):
        """Track scan and update QR code statistics."""
        super().save(*args, **kwargs)

        logger.info(
            "qr_scan_recorded",
            qr_code_id=self.qr_code_id,
            device_type=self.device_type,
            browser=self.browser,
            was_successful=self.was_successful
        )
