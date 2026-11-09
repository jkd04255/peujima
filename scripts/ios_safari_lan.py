#!/usr/bin/env python3
"""PJM-012: HTTPS ONLY, private-LAN-only iPhone Safari test (NO deployment).

Requires a trusted, mkcert-issued HTTPS certificate for the PC's RFC1918 IPv4.
Reads the public, Kakao domain-restricted JavaScript key via hidden terminal prompt,
holds it only in RAM and never writes a dist/ site or logs requests.
Never use REST/Admin keys. Stop with Ctrl+C when finished.
"""
from __future__ import annotations

import argparse
import getpass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import ipaddress
import json
from pathlib import Path
import secrets
import ssl
import sys
from urllib.parse import urlsplit

from build_pages import ANCHOR, KEY_PATTERN, ROOT

RFC1918 = tuple(ipaddress.ip_network(net) for net in (
    "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"
))
FILES = {
    "pjm012-nearby.js": ("application/javascript; charset=utf-8", ROOT / "pjm012-nearby.js"),
    "pjm012-nearby.css": ("text/css; charset=utf-8", ROOT / "pjm012-nearby.css"),
    "pjm013-navigation.js": ("application/javascript; charset=utf-8", ROOT / "pjm013-navigation.js"),
    "pjm013-navigation.css": ("text/css; charset=utf-8", ROOT / "pjm013-navigation.css"),
}


def private_host(value: str) -> str:
    """Bind only to an explicit RFC1918 LAN IPv4, never all interfaces/public IP."""
    try:
        ip = ipaddress.ip_address(value)
    except ValueError as exc:
        raise ValueError("Use the PC's numeric private IPv4 address") from exc
    if not isinstance(ip, ipaddress.IPv4Address) or not any(ip in block for block in RFC1918):
        raise ValueError("Only RFC1918 private LAN IPv4 (10/172.16-31/192.168) is allowed")
    return str(ip)


def html_with_public_js_key(key: str) -> bytes:
    if not KEY_PATTERN.fullmatch(key):
        raise ValueError("Only a 20–64-character alphanumeric Kakao JavaScript key is accepted")
    original = (ROOT / "index.html").read_text(encoding="utf-8")
    if original.count(ANCHOR) != 1:
        raise ValueError("PJM-012 script anchor is missing or duplicated")
    # Public, origin-restricted JavaScript key visible to the test browser by design.
    inline = (
        '<script id="przima-kakao-public-config">'
        f"window.PRZIMA_KAKAO_JS_KEY = {json.dumps(key)};"
        "</script>"
    )
    return original.replace(ANCHOR, inline + ANCHOR).encode("utf-8")


def handler_for(key: str, access_token: str) -> type[BaseHTTPRequestHandler]:
    html = html_with_public_js_key(key)
    if not access_token or "/" in access_token or "?" in access_token:
        raise ValueError("Invalid temporary access token")
    prefix = "/t/" + access_token + "/"
    assets = {name: (ctype, path.read_bytes()) for name, (ctype, path) in FILES.items()}

    class LocalOnlyHandler(BaseHTTPRequestHandler):
        server_version = "PRZIMA-LAN-QA"
        sys_version = ""

        def log_message(self, format, *args) -> None:
            # Deliberately do not log IPs, location inputs, key material or access token.
            pass

        def do_GET(self) -> None:
            self._serve(send_body=True)

        def do_HEAD(self) -> None:
            self._serve(send_body=False)

        def _serve(self, send_body: bool) -> None:
            path = urlsplit(self.path).path
            if path in (prefix, prefix + "index.html"):
                content_type = "text/html; charset=utf-8"
                body = html
            elif path.startswith(prefix) and path[len(prefix):] in assets:
                content_type, body = assets[path[len(prefix):]]
            else:
                # No directory listings or access to .git, SSL certificates or key files.
                self.send_error(404, "Not found")
                return

            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            # Kakao needs the origin for JS SDK domain validation; never send path token.
            self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
            self.send_header("Permissions-Policy", "geolocation=(self)")
            self.end_headers()
            if send_body:
                self.wfile.write(body)

    return LocalOnlyHandler


def main() -> None:
    parser = argparse.ArgumentParser(description="PJM-012 local-LAN HTTPS Safari test; no public deployment")
    parser.add_argument("--host", required=True, help="PC private LAN IP (e.g. 192.168.0.23)")
    parser.add_argument("--port", type=int, default=8443)
    parser.add_argument("--cert", type=Path, required=True, help="mkcert-issued certificate for --host")
    parser.add_argument("--key", type=Path, required=True, help="PRIVATE TLS leaf key; never upload")
    args = parser.parse_args()

    try:
        host = private_host(args.host)
        if not 1024 <= args.port <= 65535:
            raise ValueError("Port must be between 1024 and 65535")
        if not args.cert.is_file() or not args.key.is_file():
            raise ValueError("The local TLS certificate and its private key files are required")
        key = getpass.getpass("Kakao JavaScript 키만 입력 (화면에 표시하지 않음): ").strip()
        # No storage of the JS key, no logs, no dist/ build.
        token = secrets.token_urlsafe(24)
        handler = handler_for(key, token)
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.load_cert_chain(certfile=str(args.cert), keyfile=str(args.key))
        server = ThreadingHTTPServer((host, args.port), handler)
        server.socket = ctx.wrap_socket(server.socket, server_side=True)
    except (ValueError, OSError, ssl.SSLError) as exc:
        # Error strings only involve paths/certificate issues, never the JS key.
        print(f"Failed to start local HTTPS test: {exc}", file=sys.stderr)
        raise SystemExit(2) from None

    url = f"https://{host}:{args.port}/t/{token}/"
    print("PJM-012 local HTTPS ready; SAME WI-FI ONLY (not publicly hosted)")
    print("iPhone Safari: " + url)
    print("Kakao JavaScript SDK domain allowlist: " + f"https://{host}:{args.port}")
    print("Never share this one-time URL. Stop with Ctrl+C after testing.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print("LAN QA server stopped; the access URL no longer works.")


if __name__ == "__main__":
    main()
