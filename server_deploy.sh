#!/bin/bash
# Run this after every git pull on the server
# Usage: bash server_deploy.sh
set -e
cd /var/www/stirforchange
source venv/bin/activate

echo Running migrations...
python manage.py migrate

echo Collecting static files...
python manage.py collectstatic --noinput

echo Restarting server...
systemctl restart stirforchange

echo Done! Site is live at https://stirforchange.org
