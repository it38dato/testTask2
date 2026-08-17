#!/bin/bash

# Функция для проверки наличия команды python3
check_python() {
    if command -v python3 &>/dev/null; then
        echo "Python 3 уже установлен. Версия:"
        python3 --version
        return 0
    else
        echo "Python 3 не найден. Приступаю к установке."
        return 1
    fi
}

# Функция для проверки наличия команды pip3
check_pip() {
    if command -v pip3 &>/dev/null; then
        echo "pip3 уже установлен. Версия:"
        pip3 --version
        return 0
    else
        echo "pip3 не найден. Приступаю к установке."
        return 1
    fi
}

# Функция установки для дистрибутивов на базе Debian/Ubuntu
install_debian() {
    echo "Определен Debian/Ubuntu. Установка Python 3 и pip..."
    sudo apt update -y
    # Установка python3 и python3-pip
    sudo apt install python3 python3-pip -y
    if [ $? -eq 0 ]; then
        echo "Python 3 и pip успешно установлены."
    else
        echo "Ошибка установки Python 3 и pip. Проверьте репозитории или разрешения."
    fi
}

# Функция установки для дистрибутивов на базе Fedora/CentOS/RHEL
install_rhel() {
    echo "Определен Fedora/CentOS/RHEL. Установка Python 3 и pip..."
    if command -v dnf &>/dev/null; then
        # На RHEL/Fedora pip3 обычно ставится вместе с python3 или как отдельный пакет python3-pip
        sudo dnf install python3 python3-pip -y
    elif command -v yum &>/dev/null; then
        sudo yum install python3 python3-pip -y
    else
        echo "Не найден менеджер пакетов dnf или yum. Установка невозможна."
        exit 1
    fi

    if [ $? -eq 0 ]; then
        echo "Python 3 и pip успешно установлены."
    else
        echo "Ошибка установки Python 3 и pip. Проверьте репозитории или разрешения."
    fi
}

# Функция установки для Arch Linux
install_arch() {
    echo "Определен Arch Linux. Установка Python 3 и pip..."
    sudo pacman -Syu --noconfirm
    # На Arch pip идет в комплекте с основным пакетом python
    sudo pacman -S python --noconfirm
    if [ $? -eq 0 ]; then
        echo "Python 3 и pip успешно установлены."
    else
        echo "Ошибка установки Python 3 и pip. Проверьте репозитории или разрешения."
    fi
}

# Основная логика скрипта
# Сначала проверяем и устанавливаем Python 3, если нужно
if ! check_python; then
    # Проверка файла /etc/os-release для определения дистрибутива
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        case "$ID" in
            ubuntu|debian|mint|popos)
                install_debian
                ;;
            fedora|centos|rhel|rocky)
                install_rhel
                ;;
            arch|manjaro)
                install_arch
                ;;
            *)
                echo "Неподдерживаемый дистрибутив ($ID). Установите Python 3 и pip вручную."
                exit 1
                ;;
        esac
    else
        echo "Не удалось определить дистрибутив Linux. Установите Python 3 и pip вручную."
        exit 1
    fi
fi

# После того, как мы убедились, что Python установлен,
# дополнительно проверяем наличие pip3
echo "" # Для разделения вывода
check_pip || echo "Не удалось установить pip3 автоматически. Пожалуйста, проверьте установку вручную."
