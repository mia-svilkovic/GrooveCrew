# Savjeti za korištenje Gita

Držite se stvari napisanih u prezentaciji "Uvodne lab. vježbe", od 30. do 68. slidea.

# Inicijalno postavljanje projekta

Ovo su upute koje je potrebno pratiti prilikom inicijalnog postavljanja projekta u lokalni Git repo.

## 1. Kloniraj repo s GitHub-a

```bash
git clone https://github.com/mia-svilkovic/GrooveCrew.git
cd GrooveCrew
git checkout develop
cd izvorni_kod
```

## 2. Stvori Python virtualno okruženje

```bash
python -m venv env  # Postavi virtualno okruženje na Windowsu
# ili
python3 -m venv env  # Kreiraj virtualno okruženje na Linux/Mac
```

## 3. Aktivirajte virtualno okruženje:

```bash
env\Scripts\activate  # Aktiviraj virtualno okruženje na Windows
# ili
source env/bin/activate  # Aktiviraj virtualno okruženje na Linux/Mac
```

## 4. Instaliraj Python dependencies

```bash
pip install -r backend/requirements.txt
```

## 5. Postavi Node.js dependencies za React front-end

```bash
cd frontend
npm install  # Instaliraj Node.js dependencies
cd ..
```

## 6. Pokreni razvojni server za Django

```bash
cd backend
python manage.py migrate  # Pokreni migracije
python manage.py runserver  # Pokreni Django development server
```

## 7. Pokreni development server za React

```bash
cd frontend
npm run dev  # Pokreni React Vite development server
```

# Općenite upute za rad na ovom projektu

## 1. Početak coding sessiona

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
