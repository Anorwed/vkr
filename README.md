# 🤖 PicoClaw Telegram Bot

<div align="center">

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Anorwed/vkr/blob/main/picoclawcolabqwen.ipynb)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![Ollama](https://img.shields.io/badge/🦙-Ollama-green)](https://ollama.com)
[![License](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)

**Личный AI-ассистент в Telegram на базе Qwen 2.5**

[🚀 Быстрый старт](#-быстрая-установка) • [📱 Android/Termux](#-версия-для-android)

</div>

---

## ✨ Возможности

- 🛠️ **Выполнение команд** — бот может запускать shell-команды, работать с файлами
- 💻 **Написание кода** — генерация и редактирование кода на Python, JS и др.
- 📁 **Работа с файлами** — создание, чтение, редактирование документов
- 🔒 **Безопасность** — изолированное окружение, ограничение рабочей папки
- 🌐 **Доступ из любой точки** — работает на Android, Colab или VPS

> **Модель:** Qwen 2.5 7B (поддерживает function calling, работает стабильно)

---

## 🚀 Быстрая установка

### ☁️ Версия для Google Colab (Рекомендуется)

> **Самый простой способ** — не требует установки, работает в облаке

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Anorwed/vkr/blob/main/picoclawcolabqwen.ipynb)

1. Для начала полностью прочитайте инструкцию
2. Получите токен бота у [@BotFather](https://t.me/BotFather) и скопируйте
3. Нажмите кнопку **"Open in Colab"** выше ↑
4. Войдите в Google-аккаунт
5. Убедитесь, что Google Colab выделил вам GPU T4
6. ![](Screenshot_20260323-165344_Firefox%20Nightly~2.png)
7. ![](Screenshot_20260323-165726_Firefox%20Nightly~2.png)
8. ![](3.png)
9. Запустите ячейку, дождитесь появления зеленой галочки
![](Screenshot_20260323-165344_Firefox%20Nightly~3.png)
10. Листайте вниз, вставьте токен, запустите и ждите 5-10 минут
![](5.png)
11. Готово! Бот отвечает в Telegram до тех пор, пока активна вкладка Google Colab

> ⚠️ **Важно**: Сессия Colab активна ~12 часов. Для постоянной работы используйте Android-версию.

---

### 📱 Версия для Android (Termux) 

> Можете пропустить, только для энтузиастов

Разверните личного AI-ассистента Gemini 2.5 flash на любом Android-устройстве с выводом в Telegram.

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
```

> 💡 Совет: Долгий тап в Termux = вставка из буфера обмена

🔄 Перезапуск бота

Если закрыли Termux или нужно перезапустить:

```bash
proot-distro login debian -- bash -c "cd /root/chemistry_bot && source venv/bin/activate && python3 main.py"
```

⏹️ Остановка бота

Нажмите `Ctrl + C` в окне Termux.

---

⚙️ Конфигурация

Смена модели AI

Отредактируйте `core/ai.py`:

```python
# Для Gemini (по умолчанию)
model = "gemini-2.5-flash"
model = "любая-гугл-ии-доступная-в-вашем-api"
```

Настройка Telegram

Измените токен в `.env` файле:

```bash
BOT_TOKEN=your_token_here
```

---

🎓 Обучение

Нужен совет, как правильно пользоваться нейросетями?

[![Курс КФУ](https://img.shields.io/badge/📚-Курс_КФУ-blue)](https://edu.kpfu.ru/course/section.php?id=76191)

[Перейти на курс КФУ →](https://edu.kpfu.ru/course/section.php?id=76191)

---

🛠️ Техническая поддержка

Проблема	Решение	
Бот не отвечает	Проверьте токен в @BotFather	
Ошибка 400	Проверьте VPN и интернет	
Colab отключается	Используйте Android-версию	

Issues: [Создать тикет](https://github.com/Anorwed/vkr/issues)

---

[⬆ Наверх](#-picoclaw-telegram-bot)

Made with ❤️ for educational purposes
