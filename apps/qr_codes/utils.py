"""
Utility functions for QR code generation and analytics.
"""
import io
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from PIL import Image
import structlog
from user_agents import parse

logger = structlog.get_logger(__name__)


def generate_qr_code(
    data,
    size=300,
    error_correction='M',
    foreground_color='#000000',
    background_color='#FFFFFF',
    format='PNG'
):
    """
    Generate a QR code image.

    Args:
        data: The data to encode (URL or text)
        size: Size of the QR code in pixels
        error_correction: Error correction level (L, M, Q, H)
        foreground_color: Color of QR code modules (hex)
        background_color: Background color (hex)
        format: Image format (PNG, JPEG, SVG)

    Returns:
        BytesIO object containing the QR code image
    """
    # Map error correction letters to qrcode constants
    error_correction_map = {
        'L': qrcode.constants.ERROR_CORRECT_L,
        'M': qrcode.constants.ERROR_CORRECT_M,
        'Q': qrcode.constants.ERROR_CORRECT_Q,
        'H': qrcode.constants.ERROR_CORRECT_H,
    }

    # Create QR code instance
    qr = qrcode.QRCode(
        version=None,  # Auto-detect version based on data
        error_correction=error_correction_map.get(error_correction, qrcode.constants.ERROR_CORRECT_M),
        box_size=10,
        border=4,
    )

    qr.add_data(data)
    qr.make(fit=True)

    # Create image with custom colors
    img = qr.make_image(
        fill_color=foreground_color,
        back_color=background_color,
    )

    # Resize to desired size
    img = img.resize((size, size), Image.LANCZOS)

    # Save to BytesIO
    buffer = io.BytesIO()
    img.save(buffer, format=format)
    buffer.seek(0)

    logger.info(
        "qr_code_generated",
        size=size,
        error_correction=error_correction,
        format=format
    )

    return buffer


def generate_qr_code_styled(
    data,
    size=300,
    error_correction='M',
    foreground_color='#000000',
    background_color='#FFFFFF',
    style='rounded',
    format='PNG'
):
    """
    Generate a styled QR code with rounded or custom module shapes.

    Args:
        data: The data to encode
        size: Size in pixels
        error_correction: Error correction level
        foreground_color: QR code color
        background_color: Background color
        style: Style type ('rounded', 'square')
        format: Image format

    Returns:
        BytesIO object containing the styled QR code
    """
    error_correction_map = {
        'L': qrcode.constants.ERROR_CORRECT_L,
        'M': qrcode.constants.ERROR_CORRECT_M,
        'Q': qrcode.constants.ERROR_CORRECT_Q,
        'H': qrcode.constants.ERROR_CORRECT_H,
    }

    qr = qrcode.QRCode(
        version=None,
        error_correction=error_correction_map.get(error_correction, qrcode.constants.ERROR_CORRECT_M),
        box_size=10,
        border=4,
    )

    qr.add_data(data)
    qr.make(fit=True)

    # Create styled image
    if style == 'rounded':
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            fill_color=foreground_color,
            back_color=background_color,
        )
    else:
        img = qr.make_image(
            fill_color=foreground_color,
            back_color=background_color,
        )

    # Resize
    img = img.resize((size, size), Image.LANCZOS)

    # Save to buffer
    buffer = io.BytesIO()
    img.save(buffer, format=format)
    buffer.seek(0)

    return buffer


def parse_user_agent(user_agent_string):
    """
    Parse user agent string to extract device information.

    Args:
        user_agent_string: The user agent string from request

    Returns:
        dict with device_type, browser, os information
    """
    user_agent = parse(user_agent_string)

    # Determine device type
    if user_agent.is_mobile:
        device_type = 'mobile'
    elif user_agent.is_tablet:
        device_type = 'tablet'
    elif user_agent.is_pc:
        device_type = 'desktop'
    else:
        device_type = 'unknown'

    return {
        'device_type': device_type,
        'browser': f"{user_agent.browser.family} {user_agent.browser.version_string}",
        'operating_system': f"{user_agent.os.family} {user_agent.os.version_string}",
        'is_mobile': user_agent.is_mobile,
        'is_tablet': user_agent.is_tablet,
        'is_pc': user_agent.is_pc,
        'is_bot': user_agent.is_bot,
    }


def get_client_ip(request):
    """
    Get the client's IP address from the request.

    Handles proxies and load balancers.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def generate_visitor_id(request):
    """
    Generate a unique visitor ID based on IP and user agent.

    This is a simple implementation. For production, consider
    using cookies or more sophisticated fingerprinting.
    """
    import hashlib

    ip = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    # Create a hash of IP + User Agent
    unique_string = f"{ip}:{user_agent}"
    visitor_id = hashlib.sha256(unique_string.encode()).hexdigest()

    return visitor_id


def check_password(stored_password, input_password):
    """
    Check if the input password matches the stored password.

    For simple implementation, we're using plain text comparison.
    For production, consider using Django's password hashing.
    """
    return stored_password == input_password
