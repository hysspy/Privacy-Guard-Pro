import tkinter as tk
import cv2
import logging
import subprocess
import threading
import os
import sys
import ctypes
from datetime import datetime
from PIL import Image, ImageDraw, ImageGrab
from pycaw.pycaw import AudioUtilities
from pynput import keyboard as pynput_kb
import pystray 

# --- BRANDING & CONFIG ---
AUTHOR = "hysspy"
GITHUB = "https://github.com/hysspy"
COPYRIGHT = "© 2026 hysspy"

C_BG = "#1E1E2E"       
C_HEADER = "#181825"   
C_ACCENT = "#3DB5FF"   
C_DANGER = "#FF5D5D"   
C_TEXT = "#D9E0EE"     
C_INPUT = "#313244"    

DEFAULT_PASSWORD = "1234"
MAX_PHOTOS = 50

class PrivacyGuardPro:
    def __init__(self, master):
        self.master = master
        self.master.title(f"Privacy Guard Pro | {AUTHOR}")
        self.master.geometry("400x350") # Reduced height for ultra-compact look
        self.master.resizable(False, False)
        self.master.configure(bg=C_BG)
        
        self.current_password = DEFAULT_PASSWORD
        self.is_locked = False
        self.kb_listener = None
        self.failed_attempts = 0
        self.blink_state = False

        # --- UI SETUP ---
        header = tk.Label(master, text="🛡️ SECURITY CONSOLE", font=("Segoe UI", 12, "bold"), 
                          bg=C_HEADER, fg=C_ACCENT, pady=15)
        header.pack(fill="x", side="top")
        
        # Upper Settings Container (Removed bottom padding)
        settings = tk.Frame(master, bg=C_BG)
        settings.pack(fill="x", padx=30, pady=(10, 0))
        
        tk.Label(settings, text="LOCK PASSWORD", bg=C_BG, fg=C_TEXT, 
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        
        self.pass_entry = tk.Entry(settings, show="*", width=20, font=("Consolas", 12), 
                                   bg=C_INPUT, fg="white", insertbackground="white", 
                                   relief="flat", bd=8)
        self.pass_entry.insert(0, self.current_password)
        self.pass_entry.pack(fill="x", pady=(2, 5))

        self.idle_slider = tk.Scale(settings, from_=1, to=60, orient="horizontal", 
                                   label="AUTO-LOCK (MINUTES)", bg=C_BG, fg=C_TEXT,
                                   troughcolor=C_INPUT, activebackground=C_ACCENT,
                                   font=("Segoe UI", 8, "bold"), highlightthickness=0, bd=0)
        self.idle_slider.set(5)
        self.idle_slider.pack(fill="x", pady=0) # Removed vertical padding

        # --- BOTTOM STACK (NO SPACE) ---
        footer_frame = tk.Frame(master, bg=C_BG)
        footer_frame.pack(fill="x", side="bottom")

        self.status_text = tk.StringVar(value="Status: Ready")
        self.status_label = tk.Label(footer_frame, textvariable=self.status_text, bg=C_BG, 
                                     fg="#6E6C7E", font=("Segoe UI", 12, "italic"))
        self.status_label.pack(pady=0) # Absolute zero gap

        self.copy_label = tk.Label(footer_frame, text=f"{COPYRIGHT} | github.com/{AUTHOR}", 
                                   bg=C_BG, fg="#444", font=("Segoe UI", 10))
        self.copy_label.pack(pady=0) # Absolute zero gap

        self.start_btn = tk.Button(footer_frame, text="ENGAGE PROTECTION", command=self.engage_lock, 
                                   bg=C_ACCENT, fg=C_BG, font=("Segoe UI", 13, "bold"), 
                                   relief="flat", cursor="hand2", pady=12)
        self.start_btn.pack(fill="x", pady=(5, 0))

        # Background Handlers
        self.master.protocol('WM_DELETE_WINDOW', self.hide_window)
        threading.Thread(target=self.create_tray, daemon=True).start()
        threading.Thread(target=self.hotkey_monitor, daemon=True).start()
        self.check_idle_loop()

    # --- TRAY & WINDOW MGMT ---
    def create_tray(self):
        width, height = 64, 64
        image = Image.new('RGB', (width, height), C_HEADER)
        dc = ImageDraw.Draw(image)
        dc.ellipse((10, 10, 54, 54), fill=C_ACCENT)
        
        menu = pystray.Menu(
            pystray.MenuItem('Show Console', self.show_window),
            pystray.MenuItem('Lock Instantly', lambda: self.master.after(0, self.engage_lock)),
            pystray.MenuItem('Exit', self.exit_app)
        )
        self.tray = pystray.Icon("PrivacyGuard", image, f"Privacy Guard Pro - {AUTHOR}", menu)
        self.tray.run()

    def hide_window(self): self.master.withdraw()
    def show_window(self): self.master.deiconify()
    def exit_app(self): 
        self.tray.stop()
        self.master.quit()
        sys.exit(0) # Forcefully kill process to avoid PermissionError in next build

    # --- SECURITY CORE ---
    def hotkey_monitor(self):
        with pynput_kb.GlobalHotKeys({'<ctrl>+<alt>+l': lambda: self.master.after(0, self.engage_lock)}) as h:
            h.join()

    def block_logic(self, key):
        if self.is_locked:
            forbidden = [pynput_kb.Key.cmd, pynput_kb.Key.cmd_l, pynput_kb.Key.cmd_r, 
                         pynput_kb.Key.tab, pynput_kb.Key.esc, pynput_kb.Key.alt_l, 
                         pynput_kb.Key.alt_r, pynput_kb.Key.ctrl_l, pynput_kb.Key.ctrl_r]
            return False if key in forbidden else True
        return True

    def manage_photo_storage(self):
        photos = [f for f in os.listdir('.') if f.startswith('intruder_') and f.endswith('.jpg')]
        if len(photos) >= MAX_PHOTOS:
            photos.sort(key=os.path.getctime)
            for i in range((len(photos) - MAX_PHOTOS) + 1):
                try: os.remove(photos[i])
                except: pass

    def capture_intruder(self):
        self.manage_photo_storage()
        cam = cv2.VideoCapture(0)
        if cam.isOpened():
            ret, frame = cam.read()
            if ret:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                cv2.imwrite(f"intruder_{ts}.jpg", frame)
        cam.release()

    def get_idle_time(self):
        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
        lii = LASTINPUTINFO()
        lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
        ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
        return (ctypes.windll.kernel32.GetTickCount() - lii.dwTime) / 1000.0

    def is_audio_playing(self):
        try:
            sessions = AudioUtilities.GetAllSessions()
            for s in sessions:
                if s.Process and s.State == 1: return True
            return False
        except: return False

    def check_idle_loop(self):
        if not self.is_locked:
            idle_sec = self.get_idle_time()
            if idle_sec >= (self.idle_slider.get() * 60) and not self.is_audio_playing():
                self.engage_lock()
            else:
                self.status_text.set(f"Status: Monitoring (Idle: {int(idle_sec)}s)")
        self.master.after(5000, self.check_idle_loop)

    def engage_lock(self):
        if self.is_locked: return
        self.current_password = self.pass_entry.get()
        self.is_locked = True
        self.failed_attempts = 0
        self.master.withdraw()
        
        self.kb_listener = pynput_kb.Listener(on_press=self.block_logic, suppress=True)
        self.kb_listener.start()

        v_width = ctypes.windll.user32.GetSystemMetrics(78)  
        v_height = ctypes.windll.user32.GetSystemMetrics(79) 
        v_left = ctypes.windll.user32.GetSystemMetrics(76)   
        v_top = ctypes.windll.user32.GetSystemMetrics(77)    

        self.lock_root = tk.Toplevel(self.master)
        self.lock_root.geometry(f"{v_width}x{v_height}+{v_left}+{v_top}")
        self.lock_root.attributes("-topmost", True, "-alpha", 0.0) 
        self.lock_root.overrideredirect(True)
        self.lock_root.configure(bg="black") 
        self.lock_root.config(cursor="none")
        
        self.create_login_box()
        self.fade_in(0.0)
        self.security_loop()

    def fade_in(self, alpha):
        if alpha < 0.85: 
            alpha += 0.05
            self.lock_root.attributes("-alpha", alpha)
            self.master.after(20, lambda: self.fade_in(alpha))

    def create_login_box(self):
        self.login_box = tk.Toplevel(self.lock_root)
        self.login_box.attributes("-topmost", True)
        self.login_box.overrideredirect(True)
        bw, bh = 360, 260
        sw, sh = self.master.winfo_screenwidth(), self.master.winfo_screenheight()
        cx, cy = (sw // 2) - (bw // 2), (sh // 2) - (bh // 2)
        
        self.login_box.geometry(f"{bw}x{bh}+{cx}+{cy}")
        self.login_box.configure(bg=C_HEADER, highlightbackground=C_ACCENT, highlightthickness=2)
        
        tk.Label(self.login_box, text="SYSTEM SECURED", fg=C_ACCENT, bg=C_HEADER, font=("Segoe UI", 12, "bold")).pack(pady=(25, 5))
        self.attempt_label = tk.Label(self.login_box, text="Monitoring Unauthorized Access", fg="#6E6C7E", bg=C_HEADER, font=("Segoe UI", 9))
        self.attempt_label.pack()
        
        self.lock_entry = tk.Entry(self.login_box, show="*", font=("Consolas", 24), justify='center', bg=C_INPUT, fg="white", bd=0, insertbackground="white")
        self.lock_entry.pack(pady=15, padx=40)
        self.lock_entry.bind("<Return>", self.check_access)
        self.lock_entry.focus_force()
        
        tk.Button(self.login_box, text="UNLOCK SYSTEM", command=self.check_access, bg=C_ACCENT, fg=C_BG, width=20, relief="flat", font=("Segoe UI", 10, "bold")).pack(pady=10)

    def security_loop(self):
        if self.is_locked:
            subprocess.run("taskkill /F /IM taskmgr.exe /T", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
            self.lock_root.lift()
            self.login_box.lift()
            if self.login_box.focus_get() != self.lock_entry: self.lock_entry.focus_force()
            self.master.after(200, self.security_loop)

    def blink_alert(self):
        if self.is_locked and self.failed_attempts > 0:
            self.blink_state = not self.blink_state
            self.attempt_label.config(fg=C_DANGER if self.blink_state else "#6E6C7E")
            self.master.after(500, self.blink_alert)

    def check_access(self, event=None):
        if self.lock_entry.get() == self.current_password:
            self.is_locked = False
            if self.kb_listener: self.kb_listener.stop()
            self.lock_root.destroy()
            self.show_window()
        else:
            self.failed_attempts += 1
            self.attempt_label.config(text=f"{self.failed_attempts} Unauthorized Attempts Detected")
            if self.failed_attempts == 1: self.blink_alert()
            self.capture_intruder()
            self.lock_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = PrivacyGuardPro(root)
    root.mainloop()