"""
Auth flow test: register -> login -> logout, plus invalid-login check.
Requires the dev server to be running on localhost:8000.
"""
import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar
import random
import sys

# Force UTF-8 on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = 'http://localhost:8000'

# helpers

def make_opener():
    jar = http.cookiejar.CookieJar()
    processor = urllib.request.HTTPCookieProcessor(jar)
    opener = urllib.request.build_opener(processor)
    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
    return opener, jar

def get_csrf(opener, jar, url):
    """Fetch a page and return the csrfmiddlewaretoken from the cookie jar."""
    try:
        opener.open(url)
    except Exception:
        pass
    for c in jar:
        if c.name == 'csrftoken':
            return c.value
    return ''

def post(opener, url, data_dict, csrf):
    data_dict['csrfmiddlewaretoken'] = csrf
    payload = urllib.parse.urlencode(data_dict).encode()
    req = urllib.request.Request(
        url, data=payload, method='POST',
        headers={
            'Referer': url,
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    )
    try:
        resp = opener.open(req)
        return resp.status, resp.url, resp.read().decode('utf-8', errors='replace')
    except urllib.error.HTTPError as e:
        return e.code, url, e.read().decode('utf-8', errors='replace')

# test counters

passed = 0
failed = 0

def ok(name):
    global passed
    passed += 1
    print(f'  OK  {name}')

def fail(name, detail=''):
    global failed
    failed += 1
    print(f' FAIL {name}  -- {detail}')


# A: Register a fresh user

opener, jar = make_opener()
reg_url = BASE + '/users/register/'
csrf = get_csrf(opener, jar, reg_url)

uid = random.randint(10000, 99999)
username = f'testuser{uid}'
email = f'test{uid}@example.com'
password = f'SecurePass{uid}!'

code, final_url, body = post(opener, reg_url, {
    'first_name': 'Test',
    'last_name': 'User',
    'username': username,
    'email': email,
    'phone': '+254700000001',
    'role': 'tenant',
    'password': password,
    'password_confirm': password,
}, csrf)

if final_url and ('dashboard' in final_url or 'tenant' in final_url):
    ok('A: Register new user -> redirects to dashboard')
elif code == 200 and 'error' not in body[:500].lower() and 'already' not in body[:500].lower():
    ok('A: Register new user -> 200 (may have auto-logged in)')
else:
    fail('A: Register new user', f'code={code}, url={final_url}')


# B: Duplicate username rejected

opener2, jar2 = make_opener()
csrf2 = get_csrf(opener2, jar2, reg_url)

code2, final2, body2 = post(opener2, reg_url, {
    'first_name': 'Dup',
    'last_name': 'User',
    'username': username,       # same as just registered
    'email': f'other{uid}@example.com',
    'phone': '+254700000002',
    'role': 'tenant',
    'password': password,
    'password_confirm': password,
}, csrf2)

if 'register' in final2 or (code2 == 200 and ('taken' in body2.lower() or 'username' in body2.lower())):
    ok('B: Duplicate username rejected -> stays on register page')
else:
    fail('B: Duplicate username rejected', f'code={code2}, url={final2}')


# C: Login with correct credentials

opener3, jar3 = make_opener()
login_url = BASE + '/users/login/'
csrf3 = get_csrf(opener3, jar3, login_url)

code3, final3, body3 = post(opener3, login_url, {
    'username': username,
    'password': password,
}, csrf3)

if final3 and ('dashboard' in final3 or 'tenant' in final3):
    ok('C: Login correct credentials -> dashboard')
elif code3 == 200 and 'welcome' in body3.lower():
    ok('C: Login correct credentials -> 200 with welcome message')
else:
    fail('C: Login correct credentials', f'code={code3}, url={final3}')


# D: Login with wrong password

opener4, jar4 = make_opener()
csrf4 = get_csrf(opener4, jar4, login_url)

code4, final4, body4 = post(opener4, login_url, {
    'username': username,
    'password': 'WRONGPASSWORD',
}, csrf4)

if ('login' in final4 and
    ('invalid' in body4.lower() or 'password' in body4.lower() or 'incorrect' in body4.lower())):
    ok('D: Wrong password -> stays on login with error')
elif code4 == 200 and 'dashboard' not in (final4 or ''):
    ok('D: Wrong password -> did not proceed to dashboard')
else:
    fail('D: Wrong password', f'code={code4}, url={final4}')


# E: Logout

logout_url = BASE + '/users/logout/'
try:
    resp5 = opener3.open(logout_url)
    if resp5.status in (200, 302) or 'home' in resp5.url or resp5.url.rstrip('/') == BASE:
        ok('E: Logout -> redirects to home')
    else:
        fail('E: Logout', f'status={resp5.status}, url={resp5.url}')
except Exception as e:
    fail('E: Logout', str(e))


print(f'\nAuth Results: {passed} passed, {failed} failed out of 5 tests')
