import telebot
import uuid
import datetime
import random
import string
import base64
import subprocess
import json
import os
import re

# Token bot Telegram
TOKEN = "8310348454:AAHStB-GTHuAvx5G2XArai6EL8vELguf22A"
bot = telebot.TeleBot(TOKEN)

# Path ke file config yang benar
CONFIG_FILE_PATH = "/usr/local/etc/xray/config/04_inbounds.json"

# Fungsi untuk membaca file konfigurasi
def read_config_file(filename):
    try:
        with open(filename, 'r') as file:
            return file.read().strip()
    except:
        return "Tidak tersedia"

# Fungsi untuk mencari UUID berdasarkan username dari file JSON
def find_uuid_by_username(username):
    try:
        # Cek apakah file config ada
        if not os.path.exists(CONFIG_FILE_PATH):
            print(f"❌ File config tidak ditemukan: {CONFIG_FILE_PATH}")
            return None
            
        print(f"✅ Found config file at: {CONFIG_FILE_PATH}")
        
        # Baca file sebagai teks terlebih dahulu untuk analisis
        with open(CONFIG_FILE_PATH, 'r') as file:
            content = file.read()
        
        print(f"🔍 Searching for username: {username}")
        
        # Pattern untuk mencari username dan UUID
        # Format: "email": "username" kemudian "id": "uuid"
        pattern = r'"email":\s*"([^"]+)".*?"id":\s*"([^"]+)"'
        
        matches = re.findall(pattern, content, re.DOTALL)
        
        for email, uuid_val in matches:
            if email == username:
                print(f"✅ Found UUID: {uuid_val} for username: {username}")
                return uuid_val
        
        # Coba pattern alternatif jika format sedikit berbeda
        pattern2 = r'{"flow":\s*"[^"]*",\s*"id":\s*"([^"]+)",\s*"email":\s*"([^"]+)"'
        matches2 = re.findall(pattern2, content)
        
        for uuid_val, email in matches2:
            if email == username:
                print(f"✅ Found UUID (pattern2): {uuid_val} for username: {username}")
                return uuid_val
        
        print(f"❌ Username {username} not found in config file")
        return None
        
    except Exception as e:
        print(f"❌ Error reading config file: {str(e)}")
        return None

# Fungsi untuk mencari semua data user termasuk tanggal expired
def find_user_data(username):
    try:
        if not os.path.exists(CONFIG_FILE_PATH):
            return None, None, None
            
        with open(CONFIG_FILE_PATH, 'r') as file:
            content = file.read()
        
        # Pattern untuk mencari data lengkap
        pattern = r'##!\s*([^\s]+)\s*(\d{4}-\d{2}-\d{2}).*?"id":\s*"([^"]+)",\s*"email":\s*"([^"]+)"'
        
        matches = re.findall(pattern, content, re.DOTALL)
        
        for user_comment, exp_date, uuid_val, email in matches:
            if email == username:
                print(f"✅ Found user data: {email}, UUID: {uuid_val}, Expired: {exp_date}")
                return uuid_val, exp_date, user_comment
        
        return None, None, None
        
    except Exception as e:
        print(f"❌ Error finding user data: {str(e)}")
        return None, None, None

# Fungsi untuk membuat tautan Vmess
def create_vmess_link(ps, port, net, path, tls, uuid_val):
    config = {
        "v": "2",
        "ps": ps,
        "add": domain,
        "port": port,
        "id": uuid_val,
        "aid": "0",
        "net": net,
        "path": path,
        "type": "none",
        "host": domain,
        "tls": tls
    }
    
    # Convert dict to JSON string
    json_str = json.dumps(config, separators=(',', ':'))
    return "vmess://" + base64.b64encode(json_str.encode()).decode()

@bot.message_handler(commands=['cariakun'])
def search_vmess_account(message):
    msg = bot.reply_to(message, "👤 *Masukkan username yang ingin dicari:*", parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_search_step)

def process_search_step(message):
    try:
        chat_id = message.chat.id
        username = message.text.strip()
        
        if not username:
            msg = bot.reply_to(message, "❌ Username tidak boleh kosong!\n👤 *Masukkan username yang ingin dicari:*", parse_mode='Markdown')
            bot.register_next_step_handler(msg, process_search_step)
            return
            
        # Tampilkan pesan processing
        processing_msg = bot.send_message(chat_id, f"🔍 *Mencari akun untuk username: {username}...*", parse_mode='Markdown')
        
        # Cari data user (UUID, expired date, dan comment)
        uuid_val, exp_date, user_comment = find_user_data(username)
        
        if not uuid_val:
            # Jika tidak ditemukan dengan pattern lengkap, coba pattern sederhana
            uuid_val = find_uuid_by_username(username)
            if not uuid_val:
                bot.delete_message(chat_id, processing_msg.message_id)
                bot.send_message(chat_id, f"❌ *Akun dengan username `{username}` tidak ditemukan!*\n\nPastikan:\n• Username sudah benar\n• Akun sudah pernah dibuat sebelumnya\n• File config ada di `{CONFIG_FILE_PATH}`", parse_mode='Markdown')
                return
        
        # Baca konfigurasi domain
        global domain
        domain = read_config_file("/usr/local/etc/xray/dns/domain")
        
        # Baca informasi tambahan
        ISP = read_config_file("/usr/local/etc/xray/org")
        CITY = read_config_file("/usr/local/etc/xray/city")
        REG = read_config_file("/usr/local/etc/xray/region")
        
        # Jika tidak ada tanggal expired, gunakan tanggal hari ini + 30 hari sebagai default
        if not exp_date:
            exp_date = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        
        # Membuat Tautan Vmess dengan UUID yang ditemukan
        vmesslink1 = create_vmess_link("vmess-ws-tls", "443", "ws", "/vmess-ws", "tls", uuid_val)
        vmesslink2 = create_vmess_link("vmess-ws-ntls", "80", "ws", "/vmess-ws", "none", uuid_val)
        vmesslink3 = create_vmess_link("vmess-hup-tls", "443", "httpupgrade", "/vmess-hup", "tls", uuid_val)
        vmesslink4 = create_vmess_link("vmess-hup-ntls", "80", "httpupgrade", "/vmess-hup", "none", uuid_val)
        vmesslink5 = create_vmess_link("vmess-grpc", "443", "grpc", "vmess-grpc", "tls", uuid_val)
        
        # Format pesan modern
        text = f"""
🔍 *VMESS ACCOUNT FOUND*

┌────────────────────────────
│ 🏷️ *DOMAIN*: `{domain}`
│ 👤 *USERNAME*: `{username}`
│ 📍 *ISP*: {ISP}
│ 🌍 *REGION*: {REG}
│ 🏙️ *CITY*: {CITY}
├────────────────────────────
│ 🆔 *UUID*: `{uuid_val}`
│ 📅 *EXPIRED*: {exp_date}
│ 🔍 *STATUS*: ✅ Ditemukan
└────────────────────────────

🔗 *CONFIGURATION LINKS:*

*WebSocket TLS* 🌐
`{vmesslink1}`

*WebSocket non-TLS* ⚡
`{vmesslink2}`

*HTTP Upgrade TLS* 🔄
`{vmesslink3}`

*HTTP Upgrade non-TLS* 🚀
`{vmesslink4}`

*gRPC TLS* 🎯
`{vmesslink5}`

📖 *Cara penggunaan:*
Salin salah satu config di atas dan import ke client V2Ray/Vmess

⚠️ *Note:* 
- Simpan config dengan aman
- Jangan bagikan kepada orang lain
- Config ini sudah pernah dibuat sebelumnya
- Expired: {exp_date}
"""

        # Hapus pesan processing dan kirim hasil
        bot.delete_message(chat_id, processing_msg.message_id)
        bot.send_message(chat_id, text, parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(message, f"❌ Terjadi error: {str(e)}")

if __name__ == "__main__":
    bot.polling()
