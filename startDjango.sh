#!/bin/bash

# Чтение ввода пользователя
read -p "Enter the project name: " PROJECT_NAME
read -p "Enter ip address with port (example: 1.2.3.4:8000): " WITH_IP

VENV_NAME="envWebDjango"
VENV_PATH="$HOME/$VENV_NAME"
MANAGE_PY="manage.py"

# Переход в директорию проекта
# В Linux пути чувствительны к регистру (Case-sensitive)
if [ -d "$HOME/$PROJECT_NAME" ]; then
    cd "$HOME/$PROJECT_NAME" || exit
else
    echo "Error: Directory $HOME/$PROJECT_NAME does not exist."
    exit 1
fi

# --- 1. Проверка наличия файла manage.py ---
if [ ! -f "$MANAGE_PY" ]; then
    echo "Error: The $MANAGE_PY file was not found in $(pwd)."
    echo "Make sure that you run the script from the root of your Django project."
    exit 1
fi

# --- 2. Проверка наличия виртуального окружения ---
# В Linux скрипт активации находится в папке bin/activate
if [ ! -f "$VENV_PATH/bin/activate" ]; then
    echo "Error: The virtual environment '$VENV_NAME' was not found at '$VENV_PATH'."
    echo "Please run setup_venv.sh first."
    exit 1
fi

# --- 3. Активация виртуального окружения ---
echo "Activating the virtual environment $VENV_NAME..."
source "$VENV_PATH/bin/activate"

if [ $? -ne 0 ]; then
    echo "Error when activating the environment."
    exit 1
fi

echo "The environment is activated."

# --- 4. Запуск сервера Django ---
echo "Launching the Django server on $WITH_IP..."
# Используем python3, так как в Linux это стандарт
python3 manage.py runserver $WITH_IP

# После остановки сервера (Ctrl+C) можно деактивировать окружение
deactivate
