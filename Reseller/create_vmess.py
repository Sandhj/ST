import uuid
import datetime
import random
import string
import base64
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

# Fungsi untuk membuat tautan Vmess
def create_vmess_link(ps, port, net, path, tls):
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
    import json
    json_str = json.dumps(config, separators=(',', ':'))
    return "vmess://" + base64.b64encode(json_str.encode()).decode()


def create_vmess_account(bot, message):
    msg = bot.reply_to(message, "👤 *Masukkan username:*\n\n⚠️ *Rules:*\n- Hanya huruf dan angka\n- Maksimal 12 karakter\n- Ketik /cancel untuk membatalkan", parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_username_step, bot)

def process_username_step(message, bot):
    try:
        username = message.text.strip()
        
        # Check for cancel command
        if username.lower() == '/cancel':
            bot.reply_to(message, "❌ *Pembuatan akun Vmess dibatalkan*", parse_mode='Markdown')
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
            bot.reply_to(message, "❌ *Pembuatan akun Vmess dibatalkan*", parse_mode='Markdown')
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
        processing_msg = bot.send_message(chat_id, "⏳ *Sedang membuat akun Vmess...*", parse_mode='Markdown')
        
        # Baca konfigurasi
        global domain, uuid_val
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
        comment_line = f"### {user} {exp}" 
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
                
        # Membuat Tautan Vmess
        vmesslink1 = create_vmess_link("vmess-ws-tls", "443", "ws", "/vmess-ws", "tls")
        vmesslink2 = create_vmess_link("vmess-ws-ntls", "80", "ws", "/vmess-ws", "none")
        vmesslink3 = create_vmess_link("vmess-hup-tls", "443", "httpupgrade", "/vmess-hup", "tls")
        vmesslink4 = create_vmess_link("vmess-hup-ntls", "80", "httpupgrade", "/vmess-hup", "none")
        vmesslink5 = create_vmess_link("vmess-grpc", "443", "grpc", "vmess-grpc", "tls")
        
        # Restart Xray Service
        try:
            subprocess.run(["systemctl", "restart", "xray"], check=True)
            restart_status = "✅ Berhasil"
        except subprocess.CalledProcessError:
            restart_status = "❌ Gagal"
        
        # Format pesan modern
        text = f"""
🌐 *VMESS ACCOUNT INFORMATION*

┌────────────────────────────
│ 🏷️ *DOMAIN*: `{domain}`
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
- Config akan expired pada {exp}
"""

        # Hapus pesan processing dan kirim hasil
        bot.delete_message(chat_id, processing_msg.message_id)
        bot.send_message(chat_id, text, parse_mode='Markdown')

        # KIRIM INFO KE ADMIN
        admin_chat_id = -1003223194568
        username_tele = message.from_user.username

        message = f"""
📨 **Pesan Sistem**

👤 **Username**: @{username_tele}
🆔 **Chat ID**: `{chat_id}`

Telah Membuat Akun VMESS
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
