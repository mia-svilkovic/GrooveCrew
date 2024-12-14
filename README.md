# Savjeti za korištenje Gita

Držite se stvari napisanih u prezentaciji "Uvodne lab. vježbe", od 30. do 68. slidea.

# Inicijalno postavljanje projekta

Ovo su upute koje je potrebno pratiti prilikom inicijalnog postavljanja projekta u lokalni Git repo.

## 1. Kloniraj repo s GitHub-a

```bash
git clone https://github.com/mia-svilkovic/GrooveCrew.git
cd GrooveCrew
```

## 2. Stvori Python virtual environment

```bash
cd izvorni_kod/backend
# Postavi virtual environment
python -m venv env  # Windowsu
# ili
python3 -m venv env  # Linux/Mac
```

## 3. Aktivirajte virutal environment:

```bash
env\Scripts\activate  # Windows
# ili
source env/bin/activate  # Linux/Mac
```

## 4. Instaliraj Python dependencies

```bash
pip install -r requirements.txt
```

## 5. Pokreni development server za Django

```bash
python manage.py migrate  # pokreni migracije
python manage.py runserver  # pokreni Django development server
```
## 6. Dodaj .env za lokalni frontend development

```bash
# pozicioniranje u frontend folder
cd ../frontend

stvoriti datoteku .env
u njoj se treba nalazati:
VITE_API_URL=http://localhost:8000/
```

## 7. Instaliraj Node.js dependencies za React front-end

```bash
npm install
```

## 8. Pokreni development server za React

```bash
npm run dev
```

# Općenite upute za rad na ovom projektu

## 1. Početak coding sessiona

Uvjerite se da ste na develop branchu.  
Napravite pull promjena koje su drugi napravili. Eventualne konflikte riješiti prema uputama u prezentaciji.  
Napraviti korake 3. - 7. koji ste napravili i prilikom inicijalnog postavljanja projekta.

## 2. Tijekom coding sessiona

Redovno radite commit promjena prema uputama u prezentaciji.

## 3. Kraj coding sessiona

### Posebna napomena za backend

Ako ste dodali nove dependencies, tada obavezno pokrenuti naredbu:

```bash
cd backend
pip freeze > requirements.txt
```

### I za frontend i za backend

Napravite push napravljenih commitova. Eventualne konflikte riješiti prema uputama u prezentaciji.
