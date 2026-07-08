#!/bin/bash
set -e
echo "=== StirForChange Full Deploy ==="

BASE=/var/www/stirforchange

# 1. Copy all Python files
cp /tmp/sfc_upload/core/models.py    $BASE/core/models.py
cp /tmp/sfc_upload/core/views.py     $BASE/core/views.py
cp /tmp/sfc_upload/core/forms.py     $BASE/core/forms.py
cp /tmp/sfc_upload/core/admin.py     $BASE/core/admin.py
cp /tmp/sfc_upload/core/emails.py    $BASE/core/emails.py
cp /tmp/sfc_upload/stirforchange/urls.py $BASE/stirforchange/urls.py

# 2. Reset migrations
rm -f $BASE/core/migrations/0002_*.py
rm -f $BASE/core/migrations/0003_*.py
rm -f $BASE/core/migrations/0004_*.py
rm -f $BASE/core/migrations/0005_*.py

# 3. Delete old database
rm -f $BASE/db.sqlite3

# 4. Activate venv and migrate
source $BASE/venv/bin/activate
cd $BASE

python manage.py makemigrations core
python manage.py migrate

# 5. Create superuser
echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
from core.models import StaffProfile
if not User.objects.filter(username='aarohi').exists():
    u = User.objects.create_superuser('aarohi', 'aarohi@stirforchange.org', 'Aarohi2025!')
    StaffProfile.objects.create(user=u, role='owner')
    print('Owner created: aarohi / Aarohi2025!')
else:
    u = User.objects.get(username='aarohi')
    sp, created = StaffProfile.objects.get_or_create(user=u, defaults={'role': 'owner'})
    print('Owner already exists')
"

# 6. Collectstatic
python manage.py collectstatic --noinput

# 7. Fix email settings
python3 << 'PYEOF'
import re
path = '/var/www/stirforchange/stirforchange/settings.py'
with open(path) as f:
    content = f.read()

# Remove all old email lines
for pat in [r'EMAIL_BACKEND.*\n', r'EMAIL_HOST.*\n', r'EMAIL_PORT.*\n',
            r'EMAIL_USE_TLS.*\n', r'EMAIL_USE_SSL.*\n', r'EMAIL_HOST_USER.*\n',
            r'EMAIL_HOST_PASSWORD.*\n', r'DEFAULT_FROM_EMAIL.*\n', r'STIRFORCHANGE_EMAIL.*\n']:
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
print('Email settings fixed!')
PYEOF

# 8. Lock files from git
git -C $BASE update-index --assume-unchanged stirforchange/settings.py
git -C $BASE update-index --assume-unchanged core/views.py
git -C $BASE update-index --assume-unchanged core/models.py
git -C $BASE update-index --assume-unchanged core/forms.py
git -C $BASE update-index --assume-unchanged core/admin.py
git -C $BASE update-index --assume-unchanged core/emails.py
git -C $BASE update-index --assume-unchanged stirforchange/urls.py

# 9. Restart
systemctl restart stirforchange

echo ""
echo "=== DONE ==="
echo "Login at: https://stirforchange.org/staff/login/"
echo "Username: aarohi"
echo "Password: Aarohi2025!"
echo ""
