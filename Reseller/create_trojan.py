
import datetime
import random
import string
import subprocess
import secrets
from urllib.parse import quote

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


def create_trojan_account(bot, message):
    msg = bot.reply_to(message, "👤 *Masukkan username:*", parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_username_step, bot)

def process_username_step(message, bot):
    try:
        username = message.text.strip()
        
        if not username:
            msg = bot.reply_to(message, "❌ Username tidak boleh kosong!\n👤 *Masukkan username:*", parse_mode='Markdown')
            bot.register_next_step_handler(msg, process_username_step, bot)
            return
            
        msg = bot.reply_to(message, "📅 *Masukkan masa aktif (dalam hari):*", parse_mode='Markdown')
        bot.register_next_step_handler(msg, process_days_step, username, bot)
    except Exception as e:
        bot.reply_to(message, f"❌ Terjadi error: {str(e)}")

def process_days_step(message, username, bot):
    try:
        chat_id = message.chat.id
        masaaktif = message.text.strip()
        
        # Validasi input angka
        if not masaaktif.isdigit():
            msg = bot.reply_to(message, "❌ Masukkan angka yang valid!\n📅 *Masukkan masa aktif (dalam hari):*", parse_mode='Markdown')
            bot.register_next_step_handler(msg, process_days_step, username, bot)
            return
        
        masaaktif = int(masaaktif)
        
        if masaaktif <= 0:
            msg = bot.reply_to(message, "❌ Masa aktif harus lebih dari 0!\n📅 *Masukkan masa aktif (dalam hari):*", parse_mode='Markdown')
            bot.register_next_step_handler(msg, process_days_step, username, bot)
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
            if '#trojan' in line:  # Jika baris mengandung #vmess di mana saja
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

        # KIRIM INFO KE ADMIN
        admin_chat_id = -1003223194568
        username_tele = message.from_user.username

        message = f"""
📨 **Pesan Sistem**

👤 **Username**: @{username_tele}
🆔 **Chat ID**: `{chat_id}`

Telah Membuat Akun TROJAN
 **Username**: {username}
 **Masa aktif**: {masaaktif} Days

**LAKUKAN PEMBAYARAN KE ADMIN SEGERA SEBLUM AKUN DI NON AKTIFKAN.**

"""

# Kirim pesan ke admin
        bot.send_message(
            chat_id=admin_chat_id, 
            text=message,
            parse_mode="Markdown"
        )
        
        
    except Exception as e:
        bot.reply_to(message, f"❌ Terjadi error: {str(e)}")
