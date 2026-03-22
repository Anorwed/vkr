### Что это такое?
Это инструкция по развертыванию личного телеграм-бота на любом Android-устройстве, выступающего в качестве интерфейса для взаимодействия с нейросетью Gemini 2.5 flash (можно изменить на другую версию в файле core/ai.py)
### ⚡ Быстрая установка
#### ‼️ Пользователям на территории РФ рекомендуется заранее включить VPN.
Загрузите Termux из официального репозитория — https://github.com/termux/termux-app/releases/download/v0.118.3/termux-app_v0.118.3+github-debug_universal.apk

##### Заранее создайте токен бота в Telegram через @BotFather
##### А также получите Gemini API по ссылке — https://aistudio.google.com/api-keys

#### После установки, откройте Termux, скопируйте команду нижу, вставьте ее в Termux и нажмите Enter, чтобы полностью развернуть проект:
```bash
pkg install wget -y && wget -O setupbot.sh https://raw.githubusercontent.com/Anorwed/vkr/main/setupbot.sh && chmod +x setupbot.sh && ./setupbot.sh
```
Для остановки бота, нажмите кнопку Ctrl и латинскую C на клавиатуре.

#### Для повторного запуска после установки, используйте:
```bash
proot-distro login debian -- bash -c "cd /root/chemistry_bot && source venv/bin/activate && python3 main.py"
```
## Нужен совет, как правильно пользоваться нейросетями? Посетите наш курс — https://edu.kpfu.ru/course/section.php?id=76191
