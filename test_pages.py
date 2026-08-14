"""Quick smoke test to verify all pages return 200."""
import urllib.request

urls = [
    ('/', 'Homepage'),
    ('/about/', 'About'),
    ('/contact/', 'Contact'),
    ('/faq/', 'FAQ'),
    ('/blog/', 'Blog List'),
    ('/properties/', 'Property List'),
    ('/users/login/', 'Login'),
    ('/users/register/', 'Register'),
    ('/terms/', 'Terms'),
    ('/privacy/', 'Privacy'),
    ('/cookies/', 'Cookies'),
]

base = 'http://localhost:8000'
passed = 0
failed = 0

for path, name in urls:
    try:
        resp = urllib.request.urlopen(base + path)
        status = resp.status
        if status == 200:
            passed += 1
            print(f'  OK  {name:20s} {path}')
        else:
            failed += 1
            print(f' FAIL {name:20s} {path} -> {status}')
    except Exception as e:
        failed += 1
        print(f' ERR  {name:20s} {path} -> {e}')

print(f'\nResults: {passed} passed, {failed} failed out of {len(urls)} pages')
