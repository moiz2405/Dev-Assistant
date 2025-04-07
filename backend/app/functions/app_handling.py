# open and close an app 
# takes app name as input 
import subprocess

# Replace the ID below with the one from your shortcut if it's different
whatsapp_id = "5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App"

try:
    subprocess.Popen(["explorer.exe", f"shell:AppsFolder\\{whatsapp_id}"])
    print("[+] WhatsApp launched successfully!")
except Exception as e:
    print(f"[!] Failed to launch WhatsApp: {e}")
