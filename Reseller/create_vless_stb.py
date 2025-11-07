import uuid
import datetime
import random
import string
import subprocess


# Fungsi untuk membaca file konfigurasi
def read_config_file(filename):
    try:
        with open(filename, 'r') as file:
            return file.read().strip()
    except:
        return "Tidak tersedia"

# Fungsi untuk menghasilkan UUID
def generate_uuid():
    return str(uuid.uuid4())


def create_vless_stb_account(bot, message):
    msg = bot.reply_to(message, "👤 *Masukkan username:*\n\n⚠️ *Rules:*\n- Hanya huruf dan angka\n- Maksimal 12 karakter\n- Ketik /cancel untuk membatalkan", parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_username_step, bot)

def process_username_step(message, bot):
    try:
        username = message.text.strip()
        
        # Check for cancel command
        if username.lower() == '/cancel':
            bot.reply_to(message, "❌ *Pembuatan akun Vless dibatalkan*", parse_mode='Markdown')
            return
            
        if not username:
            msg = bot.reply_to(message, "❌ Username tidak boleh kosong!\n👤 *Masukkan username:*\n\n⚠️ *Rules:*\n- Hanya huruf dan angka\n- Maksimal 12 karakter\n- Ketik /cancel untuk membatalkan", parse_mode='Markdown')
            bot.register_next_step_handler(msg, process_username_step, bot)
            return
        
        # Validasi username: hanya huruf dan angka, maksimal 12 karakter
        if len(username) > 12:
            msg = bot.reply_to(message, f"❌ Username terlalu panjang! Maksimal 12 karakter.\n\n👤 *Masukkan username:*\n\n⚠️ *Rules:*\n- Hanya huruf dan angka\n- Maksimal 12 karakter\n- Ketik /cancel untuk membatalkan", parse_mode='Markdown')
            bot.register_next_step_handler(msg, process_username_step, bot)
            return
            
        if not username.isalnum():
            msg = bot.reply_to(message, "❌ Username hanya boleh mengandung huruf dan angka!\n\n👤 *Masukkan username:*\n\n⚠️ *Rules:*\n- Hanya huruf dan angka\n- Maksimal 12 karakter\n- Ketik /cancel untuk membatalkan", parse_mode='Markdown')
            bot.register_next_step_handler(msg, process_username_step, bot)
            return
            
        msg = bot.reply_to(message, "📅 *Masukkan masa aktif (dalam hari):*\n\nKetik /cancel untuk membatalkan", parse_mode='Markdown')
        bot.register_next_step_handler(msg, process_days_step, username, bot)
    except Exception as e:
        bot.reply_to(message, f"❌ Terjadi error: {str(e)}")

def process_days_step(message, username, bot):
    try:
        chat_id = message.chat.id
        masaaktif = message.text.strip()
        
        # Check for cancel command
        if masaaktif.lower() == '/cancel':
            bot.reply_to(message, "❌ *Pembuatan akun Vless dibatalkan*", parse_mode='Markdown')
            return
        
        # Validasi input angka
        if not masaaktif.isdigit():
            msg = bot.reply_to(message, "❌ Masukkan angka yang valid!\n📅 *Masukkan masa aktif (dalam hari):*\n\nKetik /cancel untuk membatalkan", parse_mode='Markdown')
            bot.register_next_step_handler(msg, process_days_step, username, bot)
            return
        
        masaaktif = int(masaaktif)
        
        if masaaktif <= 0:
            msg = bot.reply_to(message, "❌ Masa aktif harus lebih dari 0!\n📅 *Masukkan masa aktif (dalam hari):*\n\nKetik /cancel untuk membatalkan", parse_mode='Markdown')
            bot.register_next_step_handler(msg, process_days_step, username, bot)
            return
        
        # Tampilkan pesan processing
        processing_msg = bot.send_message(chat_id, "⏳ *Sedang membuat akun Vless...*", parse_mode='Markdown')
        
        # Baca konfigurasi
        domain = read_config_file("/usr/local/etc/xray/dns/domain")
        uuid_val = generate_uuid()
        
        # Membuat 4 huruf besar acak
        random_letters = ''.join(random.choices(string.ascii_uppercase, k=4))
        
        # Menambahkan huruf acak ke username
        user = f"{username}-{random_letters}"
        
        # Hitung tanggal expired
        exp = (datetime.datetime.now() + datetime.timedelta(days=masaaktif)).strftime("%Y-%m-%d")
        created = datetime.datetime.now().strftime("%Y-%m-%d")

        # Masukkan user ke config
        new_entry = f'}},{{"id": "{uuid_val}","email": "{user}"'
        comment_line = f"##! {user} {exp}" 
        config_file = "/usr/local/etc/xray/config/04_inbounds.json"
        temp_content = f"{comment_line}\n{new_entry}\n"

        with open(config_file, 'r') as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            new_lines.append(line)
            if '#vless' in line:  # Jika baris mengandung #vless di mana saja
                new_lines.append(temp_content)

        with open(config_file, 'w') as f:
            f.writelines(new_lines)
        
        ISP = read_config_file("/usr/local/etc/xray/org")
        CITY = read_config_file("/usr/local/etc/xray/city")
        REG = read_config_file("/usr/local/etc/xray/region")
        
        # Membuat Tautan Vless Sederhana
        vlesslink1 = f"vless://{uuid_val}@{domain}:443?type=ws&security=tls&path=%2Fvless-ws#{user}-ws-tls"
        vlesslink2 = f"vless://{uuid_val}@{domain}:80?type=ws&security=none&path=%2Fvless-ws#{user}-ws-ntls"
        vlesslink3 = f"vless://{uuid_val}@{domain}:443?type=http&security=tls&path=%2Fvless-hup#{user}-http-tls"
        vlesslink4 = f"vless://{uuid_val}@{domain}:80?type=http&security=none&path=%2Fvless-hup#{user}-http-ntls"
        vlesslink5 = f"vless://{uuid_val}@{domain}:443?type=grpc&security=tls&serviceName=vless-grpc#{user}-grpc"
        #vlesslink6 = f"vless://{uuid_val}@{domain}:443?security=tls&flow=xtls-rprx-vision#{user}-xtls"
        
        # Restart Xray Service
        try:
            subprocess.run(["systemctl", "restart", "xray"], check=True)
            restart_status = "✅ Berhasil"
        except subprocess.CalledProcessError:
            restart_status = "❌ Gagal"
        
        # Format pesan modern
        text = f"""
🌐 *VLESS ACCOUNT INFORMATION*

┌────────────────────────────
│ 🌐 *DOMAIN*: `{domain}`
│ 👤 *USERNAME*: `{user}`
│ 📍 *ISP*: {ISP}
│ 🌍 *REGION*: {REG}
│ 🏙️ *CITY*: {CITY}
├────────────────────────────
│ 📅 *CREATED*: {created}
│ ⏳ *EXPIRED*: {exp}
│ 🆔 *UUID*: `{uuid_val}`
│ 🔄 *RESTART STATUS*: {restart_status}
└────────────────────────────

🔧 *CONFIGURATION LINKS:*

*🌐 WebSocket TLS (443)*
`{vlesslink1}`

*⚡ WebSocket non-TLS (80)*
`{vlesslink2}`

*🔄 HTTP Upgrade TLS (443)*
`{vlesslink3}`

*🚀 HTTP Upgrade non-TLS (80)*
`{vlesslink4}`

*🎯 gRPC TLS (443)*
`{vlesslink5}`

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

Telah Membuat Akun VLESS STB
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
