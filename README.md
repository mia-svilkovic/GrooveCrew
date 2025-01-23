# VinylSwap

Aplikacija je dostupna na sljedećoj poveznici: https://vinyl-swap.onrender.com/

# Opis projekta

Ovaj projekt rezultat je timskog rada razvijenog u sklopu projektnog zadatka kolegija [Programsko inženjerstvo](https://www.fer.unizg.hr/predmet/proinz) na Fakultetu elektrotehnike i računarstva Sveučilišta u Zagrebu.

## Motivacija projekta

Skupljanje gramofonskih ploča posljednjih je godina doživjelo veliki preporod, postavši omiljeni hobi za glazbene entuzijaste. U doba u kojem dominira digitalni streaming, vinil nudi opipljivu i nostalgičnu vezu s glazbom koju mnogi ljudi smatraju nezamjenjivom. Zbog ograničenog broja izdanja, prestanka izdavanja ili velike potražnje, teško je uvijek pronaći željene ploče.

## Cilj projekta

Cilj je stvoriti funkcionalnu platformu koja olakšava razmjenu gramofonskih ploča između glazbenih entuzijasta. Na jednom mjestu korisnik objavljuje ploče koje nudi za zamjenu, pregledava i pronalazi željene ploče i realizira zamjenu.

# Instalacija i tehnologija

## Kloniraj repo s GitHub-a

```bash
git clone https://github.com/mia-svilkovic/GrooveCrew.git
```
## Kreiraj bazu

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

_NAPOMENA: Obje Google OAuth postavke možete pustiti kao prazan string osim ako baš ne testirate tu vrstu autorizacije._

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

# Članovi tima

- Marko Kliček
- Antonio Macan
- Filip Marković
- Karlo Peršić
- Antonio Ružić
- Mia Svilković
- Tonka Šegvić

# 📝 Kodeks ponašanja [![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)

Kao studenti upoznati smo s minimumom prihvatljivog ponašanja definiranim u [KODEKS PONAŠANJA STUDENATA FAKULTETA ELEKTROTEHNIKE I RAČUNARSTVA SVEUČILIŠTA U ZAGREBU](https://www.fer.hr/_download/repository/Kodeks_ponasanja_studenata_FER-a_procisceni_tekst_2016%5B1%5D.pdf), te dodatnim naputcima za timski rad na predmetu [Programsko inženjerstvo](https://wwww.fer.hr).
Poštujemo [etički kodeks IEEE-a](https://www.ieee.org/about/corporate/governance/p7-8.html) koji ima važnu obrazovnu funkciju sa svrhom postavljanja najviših standarda integriteta, odgovornog ponašanja i etičkog ponašanja u profesionalnim aktivnosti. Time profesionalna zajednica programskih inženjera definira opća načela koja definiranju moralni karakter, donošenje važnih poslovnih odluka i uspostavljanje jasnih moralnih očekivanja za sve pripadnike zajenice.

Kodeks ponašanja skup je provedivih pravila koja služe za jasnu komunikaciju očekivanja i zahtjeva za rad zajednice/tima. Njime se jasno definiraju obaveze, prava, neprihvatljiva ponašanja te odgovarajuće posljedice (za razliku od etičkog kodeksa). U ovom repozitoriju dan je jedan od široko prihvačenih kodeks ponašanja za rad u zajednici otvorenog koda.

# 📝 Licenca

Važeča (1)
[![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

Ovaj repozitorij sadrži otvoreni obrazovni sadržaji (eng. Open Educational Resources) i licenciran je prema pravilima Creative Commons licencije koja omogućava da preuzmete djelo, podijelite ga s drugima uz
uvjet da navođenja autora, ne upotrebljavate ga u komercijalne svrhe te dijelite pod istim uvjetima [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License HR][cc-by-nc-sa].

> ### Napomena:
>
> Svi paketi distribuiraju se pod vlastitim licencama.
> Svi upotrijebleni materijali (slike, modeli, animacije, ...) distribuiraju se pod vlastitim licencama.

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: https://creativecommons.org/licenses/by-nc/4.0/deed.hr
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg

Orginal [![cc0-1.0][cc0-1.0-shield]][cc0-1.0]

> COPYING: All the content within this repository is dedicated to the public domain under the CC0 1.0 Universal (CC0 1.0) Public Domain Dedication.
>
> [![CC0-1.0][cc0-1.0-image]][cc0-1.0]

[cc0-1.0]: https://creativecommons.org/licenses/by/1.0/deed.en
[cc0-1.0-image]: https://licensebuttons.net/l/by/1.0/88x31.png
[cc0-1.0-shield]: https://img.shields.io/badge/License-CC0--1.0-lightgrey.svg

### Reference na licenciranje repozitorija
