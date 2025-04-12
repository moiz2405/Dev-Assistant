# open and close an app 
# takes app name as input 
import subprocess
import os

# Microsoft Store (UWP) Apps
uwp_apps = {
    "whatsapp": "5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App",
    "terminal": "Microsoft.WindowsTerminal_8wekyb3d8bbwe!App",
    "microsoft_edge": "Microsoft.MicrosoftEdge_8wekyb3d8bbwe!MicrosoftEdge",
    "calculator": "Microsoft.WindowsCalculator_8wekyb3d8bbwe!App",
    "calendar": "microsoft.windowscommunicationsapps_8wekyb3d8bbwe!microsoft.windowslive.calendar",
    "camera": "Microsoft.WindowsCamera_8wekyb3d8bbwe!App",
    "notepad_store": "Microsoft.WindowsNotepad_8wekyb3d8bbwe!App"
}

# Traditional Desktop (.exe) Apps
desktop_apps = {
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "vs_code": "C:\\Users\\<YourUsername>\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
    "steam": "C:\\Program Files (x86)\\Steam\\Steam.exe",
    "translucenttb": "C:\\Program Files\\TranslucentTB\\TranslucentTB.exe",
    "docker_desktop": "C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe",
    "powerpoint": "C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE",
    "file_explorer": "explorer.exe",
    "notepad_classic": "notepad.exe"
}

def open_app(app_name: str):
    """
    Opens a UWP or Desktop app by name.
    """
    app_name = app_name.lower()
    if app_name in uwp_apps:
        try:
            subprocess.Popen(["explorer.exe", f"shell:AppsFolder\\{uwp_apps[app_name]}"])
            print(f"[+] Opened UWP app: {app_name}")
        except Exception as e:
            print(f"[!] Failed to open {app_name}: {e}")
    elif app_name in desktop_apps:
        try:
            subprocess.Popen(desktop_apps[app_name])
            print(f"[+] Opened Desktop app: {app_name}")
        except Exception as e:
            print(f"[!] Failed to open {app_name}: {e}")
    else:
        print(f"[!] App '{app_name}' not found.")

def close_app(app_name: str):
    exe_name = app_name + ".exe"
    try:
        subprocess.call([
            "cmd.exe", "/c", "taskkill", "/f", "/im", exe_name
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[-] Closed app: {exe_name}")
    except Exception as e:
        print(f"[!] Failed to close {exe_name}: {e}")

