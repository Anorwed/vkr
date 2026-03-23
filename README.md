# 🤖 PicoClaw Telegram Bot

<div align="center">

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Anorwed/vkr/blob/main/picoclawcolabqwen.ipynb)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![Ollama](https://img.shields.io/badge/🦙-Ollama-green)](https://ollama.com)
[![License](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)

**Личный AI-ассистент в Telegram с выбором режимов работы**

[🚀 Быстрый старт](#-быстрая-установка) • [📱 Android/Termux](#-версия-для-android) • [☁️ Google Colab](#-версия-для-google-colab) • [⚙️ Настройка](#-конфигурация)

</div>

---

## ✨ Возможности

| Режим | Модель | Tools | Vision | Описание |
|-------|--------|-------|--------|----------|
| 🛠️ **Код & Команды** | Qwen 2.5 7B | ✅ | ❌ | Выполняет команды, пишет код, работает с файлами |
| 🖼️ **Vision & Медиа** | Gemma 3 12B | ❌ | ✅ | Анализирует фото, документы, PDF, описывает изображения |

- 🔒 **Безопасность**: Работа в изолированном окружении
- 🌐 **Доступ из любой точки**: Работает на Android, Colab или VPS
- 🎯 **Гибкость**: Легко менять модели и провайдеров

---

## 🚀 Быстрая установка

### ☁️ Версия для Google Colab (Рекомендуется)

> **Самый простой способ** — не требует установки, работает в облаке

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Anorwed/vkr/blob/main/picoclawcolabqwen.ipynb)

1. Нажмите кнопку **"Open in Colab"** выше ↑
2. Войдите в Google-аккаунт
3. Получите токен бота у [@BotFather](https://t.me/BotFather)
4. Запустите ячейку и выберите режим работы
5. Готово! Бот отвечает в Telegram

> ⚠️ **Важно**: Сессия Colab активна ~12 часов. Для постоянной работы используйте Android-версию.

---

### 📱 Версия для Android (Termux)

Разверните личного AI-ассистента на любом Android-устройстве с интерфейсом для Gemini 2.5 Flash (или другой модели).

#### Требования
- Android 7.0+
- 2 GB свободной памяти
- Стабильное интернет-соединение

#### 🔧 Подготовка

‼️ **Пользователям в РФ**: Рекомендуется включить VPN перед началом.

1. **Установите Termux** — [скачать APK](https://github.com/termux/termux-app/releases/download/v0.118.3/termux-app_v0.118.3+github-debug_universal.apk)
2. **Создайте бота в Telegram** — напишите [@BotFather](https://t.me/BotFather), получите токен
3. **Получите API-ключ Gemini** — [aistudio.google.com/api-keys](https://aistudio.google.com/api-keys)

#### 📥 Установка (одной командой)

Откройте Termux, вставьте команду и нажмите **Enter**:

```bash
pkg install wget -y && wget -O setupbot.sh https://raw.githubusercontent.com/Anorwed/vkr/main/setupbot.sh && chmod +x setupbot.sh && ./setupbot.sh
