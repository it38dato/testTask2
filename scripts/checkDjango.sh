#!/bin/bash

# Проверка наличия python3
if ! command -v python3 &> /dev/null; then
    echo "Ошибка: Python 3 не найден. Установите его перед запуском скрипта."
    exit 1
fi

read -p "Введите название проекта: " PROJECT_NAME

VENV_NAME="envWebDjango"
VENV_PATH="$HOME/$VENV_NAME"
REQS_FILE="requirements.txt"
APP_NAME="webApp"

echo "Домашняя директория: $HOME"
echo "Путь к виртуальному окружению: $VENV_PATH"
echo "Файл зависимостей: $REQS_FILE"

# Создание виртуального окружения
if [ ! -d "$VENV_PATH" ]; then
    echo "Создание виртуального окружения '$VENV_NAME'..."
    python3 -m venv "$VENV_PATH"
    if [ $? -ne 0 ]; then
        echo "Ошибка при создании виртуального окружения."
        exit 1
    fi
    echo "Виртуальное окружение успешно создано."
else
    echo "Виртуальное окружение '$VENV_NAME' уже существует. Пропуск создания."
fi

# Активация окружения
echo "Активация окружения и установка библиотек из $REQS_FILE..."
source "$VENV_PATH/bin/activate"

# Установка зависимостей (прокси удален или замените на свой)
# Если прокси нужен, добавьте: --proxy http://YOURPROXY:8080
pip install --upgrade pip
if [ -f "$REQS_FILE" ]; then
    pip install -r "$REQS_FILE"
else
    echo "Файл $REQS_FILE не найден! Установка только Django..."
    pip install django
fi

if [ $? -ne 0 ]; then
    echo "Ошибка при установке библиотек."
    exit 1
fi

echo "Библиотеки установлены:"
pip list

# Работа с Django
cd "$HOME" || exit

echo "Создание Django проекта '$PROJECT_NAME'..."
django-admin startproject "$PROJECT_NAME"
if [ $? -ne 0 ]; then
    echo "Ошибка при создании Django проекта."
    exit 1
fi

echo "Проект создан в: $HOME/$PROJECT_NAME"

# Настройка приложения и БД
cd "$PROJECT_NAME" || exit
python manage.py startapp "$APP_NAME"
python manage.py migrate

echo "Создание суперпользователя..."
python manage.py createsuperuser

echo "Всё готово!"
echo "Для активации окружения вручную используйте: source $VENV_PATH/bin/activate"
