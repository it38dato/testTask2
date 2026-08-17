#!/bin/bash

cd ..
ls
pwd

git status

# Запрос сообщения коммита у пользователя
echo "Введите сообщение коммита:"
read commit_message

# Проверка, что сообщение не пустое
if [ -z "$commit_message" ]; then
    echo "Сообщение коммита не может быть пустым. Отмена операции."
    exit 1
fi

# Выполнение команд Git
git add .
git commit -m "$commit_message"
git push origin main
