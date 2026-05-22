# StirForChange — Django Website

A minimalist, responsive nonprofit website for StirForChange, built with Django + vanilla CSS.

## Quick Start

```bash
# 1. Clone / unzip the project
cd stirforchange

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install django pillow

# 4. Run migrations
python manage.py migrate

# 5. Create admin user (to manage content)
python manage.py createsuperuser

# 6. Run the development server
python manage.py runserver
```

Visit: http://127.0.0.1:8000

## Pages

| URL | Page |
|-----|------|
| `/` | Home |
| `/about/` | Aarohi's biography |
| `/podcast/` | Podcast & interview episodes |
| `/volunteer/` | Volunteer signup form |
| `/business/` | Local business partner signup |
| `/donate/` | Donation page |
| `/admin/` | Django admin (manage content) |

## How to Add Podcast Episodes

1. Go to `/admin/`
2. Click **Podcast Episodes** → **Add Episode**
3. Paste a YouTube watch URL — it auto-converts to embed
4. Check **Is Featured** to highlight an episode on the home page

## Customization Checklist

- [ ] `about.html` — Add Aarohi's photo at `static/images/aarohi.jpg` and update the `<img>` tag
- [ ] `donate.html` — Replace PayPal and Venmo links with real ones; add your EIN
- [ ] `base.html` footer — Update Instagram link and email address
- [ ] `settings.py` — Change `SECRET_KEY` before deploying; set `DEBUG = False` in production
- [ ] Stats on home page — Update meal/volunteer/partner numbers in `home.html`

## Deployment (Render / Railway)

1. Add `gunicorn` and `whitenoise` to requirements: `pip install gunicorn whitenoise`
2. Set `ALLOWED_HOSTS` and `SECRET_KEY` as environment variables
3. Point your start command to `gunicorn stirforchange.wsgi`

## Tech Stack

- **Backend:** Django 5.x, SQLite (swap to PostgreSQL for production)
- **Frontend:** Vanilla CSS with CSS variables, Google Fonts (Playfair Display + DM Sans)
- **Forms:** Django ModelForms with CSRF protection
- **Admin:** Django admin for managing signups and podcast episodes
