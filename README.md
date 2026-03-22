### ⚡ Быстрая установка (одной командой)

Запустите эту команду в терминале Termux, чтобы полностью развернуть проект:

```bash
pkg install wget -y && wget -O setupbot.sh https://raw.githubusercontent.com/Anorwed/vkr/main/setupbot.sh && chmod +x setupbot.sh && ./setupbot.sh
```
Для остановки бота, нажмите кнопку Ctrl и латинскую O на клавиатуре.
Для повторного запуска после установки, используйте:
```bash
proot-distro login debian -- bash -c "cd ~/chemistry_bot && source venv/bin/activate && python3 main.py
```
