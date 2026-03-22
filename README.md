### ⚡ Быстрая установка

Загрузите Termux из официального репозитория — https://github.com/termux/termux-app/releases/download/v0.118.3/termux-app_v0.118.3+github-debug_universal.apk

Заранее создайте токен бота в Telegram через @BotFather
А также получите Gemini API по ссылке — https://aistudio.google.com/api-keys

#### После установки, откройте Termux, скопируйте команду нижу, вставьте ее в Termux и нажмите Enter, чтобы полностью развернуть проект:
```bash
pkg install wget -y && wget -O setupbot.sh https://raw.githubusercontent.com/Anorwed/vkr/main/setupbot.sh && chmod +x setupbot.sh && ./setupbot.sh
```
Для остановки бота, нажмите кнопку Ctrl и латинскую O на клавиатуре.

#### Для повторного запуска после установки, используйте:
```bash
proot-distro login debian -- bash -c "cd ~/chemistry_bot && source venv/bin/activate && python3 main.py
```
