### Учебный проект Foodgram

### Описание

REST API для проекта Foodgram - «Продуктовый помощник». На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

http://51.250.100.232/ Продуктовый помощник

http://51.250.100.232/admin Админ-панель
```
СуперПользователь:
email:     admin@admin.com
password:  admin
login:     admin
```

### CI и CD: Включает в себя 4 шага

![Foodgram workflow](https://github.com/Annsjaw/foodgram-project-react/actions/workflows/main.yml/badge.svg)

- Tests: автоматический запуск тестов
- Build: обновление образов на Docker Hub
- Deploy: автоматический деплой на боевой сервер при пуше в главную ветку main
- Inform: отправление сообщения в Telegram

### Для реализации проекта используются:

- Python 3.10
- Django 4.1.4
- Django REST Framework 3.14.0
- gunicorn 20.1.0
- psycopg2-binary
- docker
- docker-compose
- Ubuntu 20.04 LTS на сервере

### Подготовка репозитория

В settings/secrets нужно подготовить ключи:

```
- DOCKER_USERNAME - Username для DockerHub
- DOCKER_PASSWORD - Пароль для DockerHub
- HOST - хост или IP для deploy
- USER - Username на сервере
- SSH_KEY - Приватный ключ
- PASSPHRASE - Если ваш ssh-ключ защищён фразой-паролем
- DB_ENGINE - django.db.backends.postgresql_psycopg2
- DB_NAME - Имя базы данных
- POSTGRES_USER - Логин для подключения к базе данных 
- POSTGRES_PASSWORD - Пароль для подключения к БД
- DB_HOST - Название сервиса
- DB_PORT - порт для подключения к БД
```
### Запуск проекта

Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/Annsjaw/foodgram-project-react
cd foodgram-project-react
```
1. Создать файл .env в infra/ и заполнить необходимыми данными:
```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=db_name # имя базы данных
POSTGRES_USER=db_user # логин для подключения к базе данных
POSTGRES_PASSWORD=db_password # пароль для подключения к БД (установите свой)
DB_HOST=db_host # название сервиса (контейнера)
DB_PORT=5432  # порт для подключения к БД
SECRET_KEY=secret_key
```
2. В файле docker-compose.yml установите подходящую вам конфигурацию для загрузки медиа файлов

- media загружается с локальной машины снаружи контейнера

```
backend:
  volumes:
    - <Путь до директории на локальной машине>:/app/media/
    
nginx:
  volumes:
    - <Путь до директории на локальной машине>:/app/media/
```
- media загружается внутри контейнера

```
backend:
  volumes:
    - media_value:/app/media/

nginx:
  volumes:
    - media_value:/var/html/media/
```

3. Там же, нужно создать контейнеры:
```
docker-compose up -d --build
Выполните по очереди команды:
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --no-input
# Если хотите заполнить базу тестовыми файлами воспользуйтесь командой ниже
docker-compose exec backend python manage.py loaddata dump.json
```
4. Создайте суперпользователя или войдите используя данные пользователя admin
(если вы заполняли базу данных тестовыми данными из dump.json):

```
docker-compose exec backend python manage.py createsuperuser
```
5. Запустить в браузере

```
http://localhost/
```