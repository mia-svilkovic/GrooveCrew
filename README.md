# Instalacija

## Kloniraj repo s GitHub-a

```bash
git clone https://github.com/mia-svilkovic/GrooveCrew.git
```
## Kreiraj bazu

Potrebno je kreirati PostgreSQL.
Postaviti PostGIS ekstenziju prema uputama koje se mogu naći u dokumentaciji:
https://postgis.net/documentation


## Stvori Python virtual environment

Pozicionirati se u `izvorni_kod/backend` te pokrenuti sljedeće na naredbe:

```bash
python -m venv env  # Windows
# ili
python3 -m venv env  # Linux/Mac
```

## Aktivirajte virutal environment:

```bash
env\Scripts\activate  # Windows
# ili
source env/bin/activate  # Linux/Mac
```

## Instaliraj Python dependencies

```bash
pip install -r requirements.txt
```

## Dodaj .env.dev za Django backend

U direktoriju izvorni_kod/backend mora postojati datoteka naziva ".env.dev", a u njoj mora biti sadržaj prema sljedećem predlošku.

*NAPOMENA: Obje Google OAuth postavke možete pustiti kao prazan string osim ako baš ne testirate tu vrstu autorizacije.*

```
DJANGO_ENV=development

# Security
DJANGO_SECRET_KEY=<VAŠ DJANGO SECRET KEY>
DJANGO_DEBUG=True

# Allowed hosts
DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1"

# Database
DATABASE_URL="postgis://<VAŠ POSTGRES USERNAME>:<LOZINKA VAŠEG USERA>@localhost:5432/<NAZIV BAZE>"

# CORS and CSRF
CORS_ALLOWED_ORIGINS="http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174,https://accounts.google.com"
CSRF_TRUSTED_ORIGINS="http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174,https://accounts.google.com"

# Google OAuth
GOOGLE_CLIENT_ID="<VAŠ GOOGLE CLIENT ID>"
GOOGLE_CLIENT_SECRET="<VAŠ GOOGLE CLIENT SECRET>"

# Email settings
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL="Record Exchange <noreply@example.com>"
SITE_URL=http://localhost:8000
```


## Stvori i primijeni migracije

```bash
python manage.py makemigrations
python manage.py makemigrations api
python manage.py migrate
```

## Punjenje baze s dummy podatcima
```bash
python manage.py populate_db
```

## Pokreni development server za Django

```bash
python manage.py runserver
```



## Dodaj .env za lokalni frontend development

U direktoriju izvorni_kod/frontend mora postojati datoteka naziva ".env", a u njoj:

```
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID="<VAŠ GOOGLE CLIENT SECRET>"
```

## Instaliraj Node.js dependencies za React frontend

```bash
npm install
```

## Pokreni development server za React

```bash
npm run dev
```
