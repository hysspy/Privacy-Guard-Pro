🛡️ Privacy Guard Pro v1.0
Developed by hysspy

Privacy Guard Pro is a high-security system lockdown utility for Windows designed to prevent physical intruders from accessing your workstation. Unlike standard Windows locks, this tool utilizes Low-Level Input Hooking to prevent system bypass and Smart Sensors to adapt to your activity.
✨ Key Features

    📺 Multi-Monitor Blackout: Automatically spans all connected displays. Uses the Windows Virtual Screen API to ensure no "leaks" on secondary monitors.

    🔊 Smart Audio Sensing: Integrated with pycaw. The auto-lock timer will pause if it detects active audio (perfect for movies or meetings).

    📸 Intruder Capture: Automatically triggers the webcam on failed password attempts, saving evidence locally.

    🚨 Blink-Alert UI: Features a high-visibility flashing red status when unauthorized access is detected.

    ⌨️ Kernel-Level Feel: Blocks Win+D, Alt+Tab, Win+R, and Ctrl+Esc. Continuously terminates Task Manager while locked.

    tray stealth: Minimizes to the System Tray to keep your taskbar clean while staying vigilant in the background.

🚀 Installation & Build
1. Environment Setup

Clone the repository and install the dependencies:
Bash

git clone https://github.com/hysspy/Privacy-Guard-Pro.git
cd Privacy-Guard-Pro
pip install -r requirements.txt

2. Compilation (Production EXE)

To create the standalone executable, use the following PyInstaller command (ensure you are in an Admin terminal):
Bash

pyinstaller --noconsole --onefile --uac-admin --clean --icon="guard.ico" --name="PrivacyGuardPro" main.py

🛠️ Technical Architecture

    Language: Python 3.14+

    Graphics: Custom "Cyber-Slate" Tkinter Theme.

    Coordinates: Calculated via ctypes.windll.user32.GetSystemMetrics.

    Input Blocking: Global suppression via pynput.keyboard.Listener.

    Storage: Automatically cycles and purges intruder photos after 50 captures to save disk space.

📖 Usage Instructions

    Launch: Open PrivacyGuardPro.exe as Administrator.

    Configure: Set your custom password and your desired idle timeout (1-60 mins).

    Engage: Press the Engage button or use the Global Hotkey: Ctrl + Alt + L.

    Unlock: Type your password and press Enter. If you fail, the app will begin capturing photos and blinking red.

⚠️ Disclaimer

Use at your own risk. This software interacts with low-level system processes. The author (hysspy) is not responsible for any forgotten passwords or system instability. There is no "backdoor"—if you lose your password, a hard reboot is required.
📄 License & Copyright

Copyright © 2026 hysspy Licensed under the MIT License. See LICENSE for more details.