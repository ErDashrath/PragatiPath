#!/usr/bin/env python3
"""
Debug the Set-Cookie header parsing
"""
import re

# This is the actual Set-Cookie header from Django
set_cookie_header = "csrftoken=hFVy1gmUbf8lX63LUQ3gOY9rHcDvxfbC; expires=Fri, 25 Sep 2026 10:38:20 GMT; Max-Age=31449600; Path=/; SameSite=Lax, sessionid=lws62sfkqip4nt556ma55jkzekbft50k; expires=Fri, 10 Oct 2025 10:38:20 GMT; HttpOnly; Max-Age=1209600; Path=/; SameSite=Lax"

print("Original Set-Cookie header:")
print(set_cookie_header)
print()

# Test the splitting logic from the proxy (converted to Python)
cookie_headers = re.split(r',\s*(?=[a-zA-Z]+=)', set_cookie_header)
print("Split result:")
for i, cookie in enumerate(cookie_headers):
    print(f"{i}: {cookie}")
    
print()
print("This should result in 2 separate cookies:")
print(f"Cookie 1: {cookie_headers[0] if len(cookie_headers) > 0 else 'None'}")
print(f"Cookie 2: {cookie_headers[1] if len(cookie_headers) > 1 else 'None'}")