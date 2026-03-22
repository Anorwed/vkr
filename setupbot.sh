#!/bin/bash

echo "=== Шаг 1: Выдача разрешения на доступ к хранилищу ==="
termux-setup-storage
# Ждем пару секунд, чтобы пользователь успел нажать "Разрешить" на экране
sleep 2 

echo "=== Шаг 2: Обновление пакетов Termux ==="
export DEBIAN_FRONTEND=noninteractive
# yes "" автоматически нажимает Enter (или Y) на все запросы, включая openssl.cnf
yes "" | pkg update -y
yes "" | pkg upgrade -y -o Dpkg::Options::="--force-confold"

echo "=== Шаг 3: Установка proot-distro ==="
pkg install proot-distro wget -y

echo "=== Шаг 4: Установка Debian ==="
proot-distro install debian

echo "=== Шаги 5-9: Переход в Debian и полная настройка бота ==="
# Передаем весь блок команд внутрь изолированной среды Debian
proot-distro login debian -- bash -c '
    export DEBIAN_FRONTEND=noninteractive
    
    echo "--- [Debian] Шаг 5: Обновление системы ---"
    apt-get update -y
    apt-get upgrade -y -o Dpkg::Options::="--force-confold"

    echo "--- [Debian] Шаг 6: Установка системных пакетов ---"
    # Добавляем wget и tar для скачивания и распаковки
    apt-get install -y python3 python3-venv python3-pip wget tar nano

    echo "--- [Debian] Шаг 7: Загрузка бота с GitHub и подготовка окружения ---"
    # Создаем рабочую папку, чтобы не мусорить в корне
    mkdir -p ~/chemistry_bot
    cd ~/chemistry_bot
    
    echo "Скачивание архива..."
    wget https://raw.githubusercontent.com/Anorwed/vkr/main/my_bot_backup.tar.gz -O my_bot.tar.gz
    
    echo "Распаковка архива..."
    tar -xzf my_bot.tar.gz
    rm my_bot.tar.gz # Удаляем архив после распаковки, чтобы не занимал место
    
    echo "Создание виртуального окружения (venv)..."
    python3 -m venv venv
    source venv/bin/activate
    
    echo "Установка Python-библиотек..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        # Резервный вариант, если requirements.txt вдруг не оказалось в архиве
        pip install aiogram google-genai python-docx python-dotenv
    fi

    echo "--- [Debian] Шаг 8: Настройка API ключей ---"
    echo "Пожалуйста, введите данные для запуска:"
    read -p "Введите BOT_TOKEN от Telegram: " bot_token
    read -p "Введите GEMINI_API_KEY: " gemini_key
    
    # Записываем ключи в скрытый файл .env
    echo "BOT_TOKEN=$bot_token" > .env
    echo "GEMINI_API_KEY=$gemini_key" >> .env
    echo "Файл .env успешно сформирован!"

    echo "--- [Debian] Шаг 9: Запуск бота ---"
    echo "Запускаю main.py..."
    python3 main.py
'
