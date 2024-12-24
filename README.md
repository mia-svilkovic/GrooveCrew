# Instalacija

## Kloniraj repo s GitHub-a

```bash
git clone https://github.com/mia-svilkovic/GrooveCrew.git
```

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

```
DJANGO_ENV=development

# Security
DJANGO_SECRET_KEY="django-insecure-1knbe=omqi2a0@w@u0h+yl2s8t*z_2tpl=r1g6xkh0c!yqc%y7"
DJANGO_DEBUG=True

# Allowed hosts
DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1"

# Database
DATABASE_URL="postgresql://<VAŠ POSTGRES USERNAME>:<LOZINKA VAŠEG USERA>@localhost:5432/<NAZIV BAZE>"

# CORS and CSRF
CORS_ALLOWED_ORIGINS="http://localhost:5173"
CSRF_TRUSTED_ORIGINS="http://localhost:5173,https://accounts.google.com"

# Google OAuth
GOOGLE_CLIENT_ID="<VAŠ GOOGLE CLIENT ID>"
GOOGLE_CLIENT_SECRET="<VAŠ GOOGLE CLIENT SECRET>"
```


## Stvori i primijeni migracije

```bash
python manage.py makemigrations
python manage.py makemigrations api
python manage.py migrate
```


## Pokreni development server za Django

```bash
python manage.py runserver  # pokreni Django development server
```



## Dodaj .env za lokalni frontend development

U direktoriju izvorni_kod/frontend mora postojati datoteka naziva ".env", a u njoj:

```
VITE_API_URL=http://localhost:8000
```

## Instaliraj Node.js dependencies za React frontend

```bash
npm install
```

## Pokreni development server za React

```bash
npm run dev
```
