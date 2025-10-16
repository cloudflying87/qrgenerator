# PWA & Open Graph Setup

## Files Generated

- `static/manifest.json` - PWA manifest
- `static/js/service-worker.js` - Basic service worker
- `static/img/default-share.png` - Default share image

## Add to base.html

```html
<head>
    <!-- PWA Manifest -->
    <link rel="manifest" href="{% static 'manifest.json' %}">
    <meta name="theme-color" content="#18181b">

    <!-- Open Graph with defaults -->
    <meta property="og:title" content="{% block og_title %}Qrgenerator{% endblock %}">
    <meta property="og:description" content="{% block og_description %}Building my own QR generator for fun.{% endblock %}">
    <meta property="og:image" content="{% block og_image %}{{ request.scheme }}://{{ request.get_host }}{% static 'img/default-share.png' %}{% endblock %}">
    <meta property="og:url" content="{{ request.build_absolute_uri }}">
    <meta property="og:type" content="website">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:image" content="{% block twitter_image %}{{ request.scheme }}://{{ request.get_host }}{% static 'img/default-share.png' %}{% endblock %}">

    <!-- Apple Touch Icon -->
    <link rel="apple-touch-icon" href="{% static 'img/default-share.png' %}">
</head>
```

## Register Service Worker

Add before closing `</body>` tag:

```html
<script>
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('{% static 'js/service-worker.js' %}');
}
</script>
```

## Image Recommendations

- **Open Graph**: 1200x630px (1.91:1 ratio)
- **PWA Icons**: 512x512px (square)
- **Format**: PNG or JPG
- **Size**: Under 1MB

✅ Your image has been copied to: static/img/default-share.png
