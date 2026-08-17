# Информационный портал базовых станций (Nokia / Ericsson)
<p>
    <strong>Task:</strong><br>
    Необходимо установить и настроить веб-сервер «Информационный портал», в котором отображается информация о базовых станциях Nokia и Ericsson.<br>
    <strong>Decision:</strong><br>
    Веб-сервер изначально разрабатывается для тестовой среды Windows с использованием Django и автоматизации через BAT-скрипты. Для работы необходимо: Python 3.10, Django, Виртуальное окружение, База данных (SQLite3 / MySQL / PostgresSQL)<br>
    Примечания:<br>
    1. Проект предназначен для тестовой и боевой среды<br>
    2. Поддерживается Windows и Linux<br>
    3. Основной стек: Python / Django / MySQL
</p>
<p>
    <strong>Task:</strong><br>
    Установка и настройка (Windows / Linux)<br>
    <strong>Decision:</strong><br>
    1. Установка Python: Скачать и установить Python 3.10, убедиться, что он добавлен в PATH.<br>
    2. Проверка Python: Запустить checkPython.bat, для Линукс систем - checkPython.sh.<br>
    Скрипты проверяют наличие Python в системе.<br>
    3. Создание Django-проекта: Запустить checkDjango.bat, для Линукс систем - checkDjango.sh.<br>
    Что делает скрипт: Создаёт виртуальное окружение, Устанавливает зависимости из requirements.txt, Создаёт Django-проект в домашней директории, Запрашивает Имя виртуального окружения (SET VENV_NAME=...), Название проекта, Логин и пароль администратора и Показывает Команду активации виртуального окружения и Путь к исходным файлам проекта.<br>
    Файл requirements.txt должен находиться в той же папке, откуда запускается checkDjango.bat.<br>
    4. Запуск тестового сервера: Запустить Скрипт startDjango.bat, для Линукс систем - startDjango.sh.<br>
    Скрипт запрашивает Название проекта, IP-адрес. Если IP не указан, используется: http://127.0.0.1:8000<br>
    Если в settings.py изменён параметр:<br>
    ALLOWED_HOSTS = []<br>
    необходимо указать IP и порт, прописанные в ALLOWED\_HOSTS (например: 127.0.0.1:8000)<br>
    Остановка сервера - CTRL + C
</p>
<p>
    <strong>Task:</strong><br>
    Готовые проекты<br>
    <strong>Decision:</strong><br>
    В папке projects/ находятся готовые версии веб-сервера.<br>
    Перед запуском готового проекта необходимо:<br>
    - Изменить параметры в settings.py: ALLOWED\_HOSTS, INSTALLED\_APPS, TEMPLATES, DATABASES, customColorPalette, CKEDITOR\_5\_CONFIGS<br>
    - Скопировать и заменить файлы: webAdminTemplate/urls.py, webPages/\*.html, webApp/\*.py, config.json<br>
    - Запустить startDjango.bat, для Линукс систем - startDjango.sh.<br>
    - Ввести параметры из config.json
</p>
<p>
    <strong>Task:</strong><br>
    Работа с базами данных. По умолчанию используется SQLite3.<br>
    <strong>Decision:</strong><br>
    1. Посмотреть данные в SQLite3 можно командами:<br>
    sudo apt install sqlite3<br>
    sqlite3 db.sqlite3<br>
    .tables<br>
    .q<br>
    2. Для Импорта данных из Excel в SQLite3 есть скрипт ImportExcelSqlite.py<br>
    3. Создание БД MySQL (продакшн):<br>
    CREATE DATABASE your_database_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;<br>
    4. Настройка settings.py:<br>
    DATABASES = { 'default': { 'ENGINE': 'mysql.connector.django', 'NAME': 'your_database_name', 'USER': 'your_user', 'PASSWORD': 'your_password', 'HOST': 'localhost', 'PORT': '3306', 'OPTIONS': { 'init_command': "SET sql_mode='STRICT_TRANS_TABLES'", 'charset': 'utf8mb4', 'use_unicode': True, } } }<br>
    5. Миграция данных из SQLite в MySQL Экспорт данных: importDjangoSql1.bat<br>
    6. Миграция данных из SQLite в MySQL Импорт в MySQL: importDjangoSql2.bat<br>
    7. Создание БД PSQL (продакшн):<br>
    Скрипт checkPsql.sh проверяют наличие БД в системе.<br>
    Команды для настройки БД:<br>
    sudo -u postgres psql<br>
    \password postgres<br>
    CREATE DATABASE sqlite3;<br>
    CREATE USER myuser WITH PASSWORD 'testPassword';<br>
    GRANT ALL PRIVILEGES ON DATABASE sqlite3 TO myuser;<br>
    \q<br>
    Настройка /etc/postgresql/14/main/pg_hba.conf:<br>
    host &nbsp; &nbsp;all &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; all &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; 0.0.0.0/0 &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; md5<br>
    Настройка /etc/postgresql/16/main/postgresql.conf:<br>
    listen_addresses = '\*'<br>
    sudo systemctl restart postgresql<br>
    sudo ufw allow 5432/tcp<br>
    psql -U dato -d sqlite3 -h localhost
</p>
<p>
    <strong>Task:</strong><br>
    Миграция проекта (Linux)<br>
    <strong>Decision:</strong><br>
    1. Для переноса Django-проекта с Windows на Linux используется migrateDjango.sh.<br>
    2. executeFile.sh предоставляет права на исполнение файла.<br>
    3. Проверка сервиса:<br>
    sudo systemctl status bss_portal.service
</p>
<p>
    <strong>Task:</strong><br>
    Админ-панель Django<br>
    <strong>Decision:</strong><br>
    1. Создание суперпользователя:<br>
    python3 manage.py createsuperuser<br>
    Для Windows можно использовать<br>
    djangoAddUser.*
</p>
<p>
    <strong>Task:</strong><br>
    GitHub публикация проекта<br>
    <strong>Decision:</strong><br>
    для публикации проекта после внесения изменений можно использовать скрипт pushGithub.sh
</p>
<p>
    <strong>Task:</strong><br>
    Тестовые проекты<br>
    <strong>Decision:</strong><br>
    Папка testImportKeys:<br>
    1. testLibrary.py использует библиотеку importKeys.py<br>
    2. Данные подтягиваются из config.txt<br>
    3. Для веб-портала не используется, т.к. применяется config.json и другая логика.
</p>