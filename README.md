## Setup
```bash
py -m venv .venv
.venv\Scripts\Activate.ps1 # pro windows
source .venv/bin/activate # pro linux
pip install -r requirements.txt
py manage.py makemigrations
py manage.py migrate
```

## Načtení testovacích dat
```bash
py manage.py loaddata fixtures/databaze.json --exclude contenttypes --exclude auth.Permission --exclude admin --exclude sessions
python manage.py collectstatic --clear --noinput
```

## Spuštění serveru
```bash
py manage.py runserver
```

## Přihlašovací údaje

| Role       | Username      | Heslo |
|-----------|---------------|-------|
| Superuser | administrator | pass  |
| Teacher   | teacher       | pass  |
| Student   | student1      | pass  |
| Student   | student2      | pass  |
| Student   | student3      | pass  |
