## Setup
```bash
pip install -r requirements.txt
py manage.py makemigrations
py manage.py migrate
```

## Načtení testovacích dat
```bash
py manage.py loaddata fixtures/testdata.json
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