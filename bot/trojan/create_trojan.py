import telebot
import datetime
import random
import string
import subprocess
import secrets
from urllib.parse import quote

# Token bot Telegram
TOKEN = "8255110757:AAFGiEMmjP8LWPbcArK2QDafxq12j7NKPkc"
bot = telebot.TeleBot(TOKEN)

# Fungsi untuk membaca file konfigurasi
def read_config_file(filename):
    try:
        with open(filename, 'r') as file:
            return file.read().strip()
    except:
        return "Tidak tersedia"

# Fungsi untuk menghasilkan password acak
def generate_password():
    return secrets.token_hex(4)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = """
🛡️ *Trojan Account Generator Bot*

*Available Commands:*
`/buattrojan` - Buat akun Trojan baru
`/info` - Info bot

Bot ini akan membantu Anda membuat konfigurasi Trojan secara otomatis.
    """
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['info'])
def send_info(message):
    info_text = """
📊 *Bot Information*

*Features:*
• Generate Trojan accounts automatically
• Multiple protocol support (WS, gRPC, HTTP Upgrade, TCP)
• TLS & non-TLS configurations
• Auto-restart Xray service

*Supported Protocols:*
├── WebSocket (WS)
├── gRPC
├── HTTP Upgrade
└── TCP TLS

*Developer:* @YourUsername
    """
    bot.reply_to(message, info_text, parse_mode='Markdown')

@bot.message_handler(commands=['buattrojan'])
def create_trojan_account(message):
    msg = bot.reply_to(message, "👤 *Masukkan username:*", parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_username_step)

def process_username_step(message):
    try:
        username = message.text.strip()
        
        if not username:
            msg = bot.reply_to(message, "❌ Username tidak boleh kosong!\n👤 *Masukkan username:*", parse_mode='Markdown')
            bot.register_next_step_handler(msg, process_username_step)
            return
            
        msg = bot.reply_to(message, "📅 *Masukkan masa aktif (dalam hari):*", parse_mode='Markdown')
        bot.register_next_step_handler(msg, process_days_step, username)
    except Exception as e:
        bot.reply_to(message, f"❌ Terjadi error: {str(e)}")

def process_days_step(message, username):
    try:
        chat_id = message.chat.id
        masaaktif = message.text.strip()
        
        # Validasi input angka
        if not masaaktif.isdigit():
            msg = bot.reply_to(message, "❌ Masukkan angka yang valid!\n📅 *Masukkan masa aktif (dalam hari):*", parse_mode='Markdown')
            bot.register_next_step_handler(msg, process_days_step, username)
            return
        
        masaaktif = int(masaaktif)
        
        if masaaktif <= 0:
            msg = bot.reply_to(message, "❌ Masa aktif harus lebih dari 0!\n📅 *Masukkan masa aktif (dalam hari):*", parse_mode='Markdown')
            bot.register_next_step_handler(msg, process_days_step, username)
            return
        
        # Tampilkan pesan processing
        processing_msg = bot.send_message(chat_id, "⏳ *Sedang membuat akun Trojan...*", parse_mode='Markdown')
        
        # Baca konfigurasi
        domain = read_config_file("/usr/local/etc/xray/dns/domain")
        password = generate_password()
        
        # Membuat 4 huruf besar acak
        random_letters = ''.join(random.choices(string.ascii_uppercase, k=4))
        
        # Menambahkan huruf acak ke username
        user = f"{username}-{random_letters}"
        
        # Hitung tanggal expired
        exp = (datetime.datetime.now() + datetime.timedelta(days=masaaktif)).strftime("%Y-%m-%d")
        created = datetime.datetime.now().strftime("%Y-%m-%d")

        # Masukkan user ke config
        new_entry = f'}},{{"password": "{password}","email": "{user}"'
        comment_line = f"#&! {user} {exp}" 
        config_file = "/usr/local/etc/xray/config/04_inbounds.json"
        temp_content = f"{comment_line}\n{new_entry}\n"

        with open(config_file, 'r') as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            new_lines.append(line)
            if '#vmess' in line:  # Jika baris mengandung #vmess di mana saja
                new_lines.append(temp_content)

        with open(config_file, 'w') as f:
            f.writelines(new_lines)
      
        ISP = read_config_file("/usr/local/etc/xray/org")
        CITY = read_config_file("/usr/local/etc/xray/city")
        REG = read_config_file("/usr/local/etc/xray/region")
        
        # Membuat Tautan Trojan Sederhana
        trojanlink1 = f"trojan://{password}@{domain}:443?type=ws&security=tls&path=%2Ftrojan-ws#{user}-ws-tls"
        trojanlink2 = f"trojan://{password}@{domain}:80?type=ws&security=none&path=%2Ftrojan-ws#{user}-ws-ntls"
        trojanlink3 = f"trojan://{password}@{domain}:443?type=http&security=tls&path=%2Ftrojan-hup#{user}-http-tls"
        trojanlink4 = f"trojan://{password}@{domain}:80?type=http&security=none&path=%2Ftrojan-hup#{user}-http-ntls"
        trojanlink5 = f"trojan://{password}@{domain}:443?type=grpc&security=tls&serviceName=trojan-grpc#{user}-grpc"
        trojanlink6 = f"trojan://{password}@{domain}:443?security=tls&type=tcp#{user}-tcp-tls"
        
        # Restart Xray Service
        try:
            subprocess.run(["systemctl", "restart", "xray"], check=True)
            restart_status = "✅ Berhasil"
        except subprocess.CalledProcessError:
            restart_status = "❌ Gagal"
        
        # Format pesan modern
        text = f"""
🛡️ *TROJAN ACCOUNT INFORMATION*

┌────────────────────────────
│ 🌐 *DOMAIN*: `{domain}`
│ 👤 *USERNAME*: `{user}`
│ 🔑 *PASSWORD*: `{password}`
│ 📍 *ISP*: {ISP}
│ 🌍 *REGION*: {REG}
│ 🏙️ *CITY*: {CITY}
├────────────────────────────
│ 📅 *CREATED*: {created}
│ ⏳ *EXPIRED*: {exp}
│ 🔄 *RESTART STATUS*: {restart_status}
└────────────────────────────

🔧 *CONFIGURATION LINKS:*

*🌐 WebSocket TLS (443)*
`{trojanlink1}`

*⚡ WebSocket non-TLS (80)*
`{trojanlink2}`

*🔄 HTTP Upgrade TLS (443)*
`{trojanlink3}`

*🚀 HTTP Upgrade non-TLS (80)*
`{trojanlink4}`

*🎯 gRPC TLS (443)*
`{trojanlink5}`

*🔒 TCP TLS (443)*
`{trojanlink6}`

⚠️ *Note:* 
- Simpan config dengan aman
- Jangan bagikan kepada orang lain
- Config akan expired pada {exp}
"""

        # Hapus pesan processing dan kirim hasil
        bot.delete_message(chat_id, processing_msg.message_id)
        
        # Kirim pesan utama
        bot.send_message(chat_id, text, parse_mode='Markdown')
        
        
    except Exception as e:
        bot.reply_to(message, f"❌ Terjadi error: {str(e)}")

# Handler untuk pesan selain command
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    help_text = """
❓ *Perintah tidak dikenali*

Gunakan salah satu perintah berikut:
`/start` - Memulai bot
`/buattrojan` - Buat akun Trojan baru
`/info` - Informasi bot

Ketik /start untuk memulai.
    """
    bot.reply_to(message, help_text, parse_mode='Markdown')

if __name__ == "__main__":
    print("🛡️ Bot Trojan Account Generator sedang berjalan...")
    print("📍 Token:", TOKEN)
    print("⏰", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    bot.polling()
