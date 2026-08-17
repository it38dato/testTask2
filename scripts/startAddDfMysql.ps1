# Определяем путь к папке скрипта и к корню проекта (на уровень выше)
$scriptDir = $PSScriptRoot
$projectDir = Split-Path -Path $scriptDir -Parent

$envProject = "envWebDjango"
$userProfile = $env:USERPROFILE

# 1. Лог сохраняем в папку скриптов
Start-Transcript -Path "$scriptDir\outShellScript.log"

# 2. Активация виртуального окружения
cd "$userProfile\$envProject\Scripts\"
. .\Activate.ps1

# 3. Переход в директорию со скриптом Python
cd $scriptDir

# 4. Запуск Python скрипта
python addDfMysql.py

# 5. Деактивация окружения
deactivate

# 6. Остановка транскрипта
Stop-Transcript