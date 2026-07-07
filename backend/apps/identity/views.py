from django.conf import settings
from django.http import HttpResponse, HttpResponsePermanentRedirect


def index(request):
        canonical_host = getattr(settings, 'CANONICAL_HOST', 'identity.silentkey.me')
        host = request.get_host().split(':', 1)[0].lower()

        if host not in {'localhost', '127.0.0.1', '::1', canonical_host}:
                return HttpResponsePermanentRedirect(f'https://{canonical_host}/')

        body = f"""<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Silent Key | Identity</title>
        <style>
            :root {{ color-scheme: dark; }}
            body {{ font-family: system-ui, sans-serif; margin: 0; min-height: 100vh; display: grid; place-items: center; background: linear-gradient(135deg, #0f172a, #111827 50%, #1f2937); color: #e5e7eb; }}
            main {{ max-width: 42rem; padding: 3rem; background: rgba(15, 23, 42, 0.88); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 1.25rem; box-shadow: 0 24px 80px rgba(0, 0, 0, 0.35); }}
            h1 {{ margin-top: 0; font-size: 2.4rem; }}
            p {{ line-height: 1.6; color: #cbd5e1; }}
            code {{ background: rgba(148, 163, 184, 0.15); padding: 0.15rem 0.35rem; border-radius: 0.35rem; }}
            .tag {{ display: inline-block; padding: 0.35rem 0.75rem; border-radius: 999px; background: rgba(14, 165, 233, 0.18); color: #7dd3fc; font-size: 0.85rem; letter-spacing: 0.04em; text-transform: uppercase; }}
        </style>
    </head>
    <body>
        <main>
            <span class="tag">Identity root</span>
            <h1>Silent Key</h1>
            <p>The canonical application host is <code>{canonical_host}</code>. This landing page is served from the root URL so the identity portal can be reached directly from the domain and from local development.</p>
            <p>Use this entry point for QR pairing, challenge-response authentication, and future thin-client surfaces.</p>
        </main>
    </body>
</html>"""
        return HttpResponse(body, content_type='text/html; charset=utf-8')