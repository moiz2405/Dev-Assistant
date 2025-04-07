# open and close an app 
# takes app name as input 
import subprocess

# Replace the ID below with the one from your shortcut if it's different
whatsapp_id = "5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App"
# Microsoft Store (UWP) App IDs
uwp_apps = {
    "whatsapp": "5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App",
    "terminal": "Microsoft.WindowsTerminal_8wekyb3d8bbwe!App",
    "microsoft_edge": "Microsoft.MicrosoftEdge_8wekyb3d8bbwe!MicrosoftEdge",
    "calculator": "Microsoft.WindowsCalculator_8wekyb3d8bbwe!App",
    "calendar": "microsoft.windowscommunicationsapps_8wekyb3d8bbwe!microsoft.windowslive.calendar",
    "camera": "Microsoft.WindowsCamera_8wekyb3d8bbwe!App",
    "notepad_store": "Microsoft.WindowsNotepad_8wekyb3d8bbwe!App"
}

# Traditional Desktop (.exe) Paths
desktop_apps = {
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "vs_code": "C:\\Users\\<YourUsername>\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
    "steam": "C:\\Program Files (x86)\\Steam\\Steam.exe",
    "translucenttb": "C:\\Program Files\\TranslucentTB\\TranslucentTB.exe",
    "docker_desktop": "C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe",
    "powerpoint": "C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE",  # may vary
    "file_explorer": "explorer.exe",
    "notepad_classic": "notepad.exe"
}

try:
    subprocess.Popen(["explorer.exe", f"shell:AppsFolder\\{whatsapp_id}"])
    print("[+] WhatsApp launched successfully!")
except Exception as e:
    print(f"[!] Failed to launch WhatsApp: {e}")
