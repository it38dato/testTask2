#!/bin/bash

# Запрашиваем данные у пользователя
read -p "Enter GitHub repository URL: " repo_url
read -p "Enter commit message: " commit_msg

cd ..
ls
pwd

# Выполняем команды Git
git init
git add .
git commit -m "$commit_msg"
git branch -M main
git remote add origin "$repo_url"
git push -u origin main

# Аналог паузы
read -p "Press [Enter] key to continue..."
