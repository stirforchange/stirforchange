#!/bin/bash
# Run after every git pull on the server
# Usage: bash server_deploy.sh
set -e
cd /var/www/stirforchange
source venv/bin/activate

echo "Running migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Fixing email settings..."
python3 << 'PYEOF'
import re
path = 'stirforchange/settings.py'
with open(path) as f:
    content = f.read()
for pat in [r'EMAIL_BACKEND.*\n', r'#.*EMAIL_BACKEND.*\n', r'EMAIL_HOST[^_].*\n',
            r'EMAIL_PORT.*\n', r'EMAIL_USE_TLS.*\n', r'EMAIL_USE_SSL.*\n',
            r'EMAIL_HOST_USER.*\n', r'EMAIL_HOST_PASSWORD.*\n',
            r'DEFAULT_FROM_EMAIL.*\n', r'STIRFORCHANGE_EMAIL.*\n']:
    content = re.sub(pat, '', content)
content = content.rstrip() + """

EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'mail.privateemail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_USE_SSL       = False
EMAIL_HOST_USER     = 'aarohi@stirforchange.org'
EMAIL_HOST_PASSWORD = 'Aarohi23!!'
DEFAULT_FROM_EMAIL  = 'StirForChange <aarohi@stirforchange.org>'
STIRFORCHANGE_EMAIL = 'aarohi@stirforchange.org'
"""
with open(path, 'w') as f:
    f.write(content)
print('Email settings configured!')
PYEOF

echo "Restarting server..."
systemctl restart stirforchange
echo "Done!"
