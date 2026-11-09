"""PJM-012 LAN-only Safari QA server tests: test-only fake key, no TLS trust or network deployment.

These tests use localhost as an ephemeral test fixture. The actual CLI disallows
localhost and requires an explicit private LAN address + valid trusted HTTPS.
"""
from __future__ import annotations

from http.server import ThreadingHTTPServer
import sys
from pathlib import Path
import threading
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from ios_safari_lan import handler_for,html_with_public_js_key,private_host

TEST_KEY="a"*32
TOKEN="fakeTemporaryTokenForTestsOnly"


def fetch(base,path,method="GET"):
    request=urllib.request.Request(base+path,method=method)
    try:
        with urllib.request.urlopen(request,timeout=5) as res:
            return res.status,res.read(),res.headers
    except urllib.error.HTTPError as exc:
        return exc.code,exc.read(),exc.headers


def main():
    for ip in ("192.168.0.2","10.2.3.4","172.18.20.9"):
        assert private_host(ip)==ip
    for ip in ("0.0.0.0","127.0.0.1","8.8.8.8","172.32.0.1","::1","not-an-ip"):
        try:
            private_host(ip)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Non-RFC1918 bind address was accepted: {ip}")

    html=html_with_public_js_key(TEST_KEY)
    assert b'window.PRZIMA_KAKAO_JS_KEY = "aaaaaaaa' in html
    assert html.index(b"PRZIMA_KAKAO_JS_KEY")<html.index(b'./pjm012-nearby.js')
    assert b"pjm012-nearby.js" in html and b"pjm013-navigation.js" in html

    server=ThreadingHTTPServer(("127.0.0.1",0),handler_for(TEST_KEY,TOKEN))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base=f"http://127.0.0.1:{server.server_port}"
    try:
        prefix=f"/t/{TOKEN}/"
        for path in ("/","/index.html","/robots.txt","/.git/config","/rootCA.pem",
                     "/.local-qa-key.pem","/t/otherToken/","/t/otherToken/pjm012-nearby.js",
                     prefix+".git/config",prefix+"../index.html"):
            status,body,_=fetch(base,path)
            assert status==404, f"Unauthorized path was served: {path}"
            assert TEST_KEY.encode() not in body

        status,body,headers=fetch(base,prefix)
        assert status==200
        assert TEST_KEY.encode() in body
        assert headers["Cache-Control"]=="no-store"
        assert headers["Referrer-Policy"]=="strict-origin-when-cross-origin"
        assert headers["Permissions-Policy"]=="geolocation=(self)"
        assert headers["X-Content-Type-Options"]=="nosniff"
        status,body,headers=fetch(base,prefix+"pjm012-nearby.js")
        assert status==200 and b"window.PJM012" in body
        assert TEST_KEY.encode() not in body
        assert headers.get_content_type()=="application/javascript"
        status,body,_=fetch(base,prefix+"pjm013-navigation.js")
        assert status==200 and b"PJM013" in body
        status,body,_=fetch(base,prefix+"pjm013-navigation.css")
        assert status==200 and b"pjm013" in body
        status,body,_=fetch(base,prefix+"pjm012-nearby.css")
        assert status==200 and b"nearby" in body
        status,body,headers=fetch(base,prefix,method="HEAD")
        assert status==200 and body==b""
        print("PASS LAN QA: RFC1918-only bind / random URL access token / no directory listing / no cache")
        print("PASS LAN QA: public JS key injection is RAM-only and static assets allowed")
        print("PASS LAN QA: no external domain, GitHub Pages, certificate file or real user GPS accessed")
    finally:
        server.shutdown()
        server.server_close()


if __name__=="__main__":main()
