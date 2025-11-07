import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import time
import json
from datetime import datetime, timedelta

from create_vmess import create_vmess_account
from create_vless import create_vless_account
from create_trojan import create_trojan_account

# Konfigurasi
BOT_TOKEN = "8532237499:AAF_OMYRoUiO1sGJKNy4qU8r2G4hmy5LsxA"
ADMIN_CHAT_ID = 576495165
BLACKLIST_FILE = "blacklist.txt"
USAGE_LIMIT_FILE = "usage_limit.json"

# Inisialisasi bot
bot = telebot.TeleBot(BOT_TOKEN)

# Fungsi untuk memuat data penggunaan user
def load_usage_data():
    if not os.path.exists(USAGE_LIMIT_FILE):
        return {}
    
    try:
        with open(USAGE_LIMIT_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception):
        return {}

# Fungsi untuk menyimpan data penggunaan user
def save_usage_data(usage_data):
    with open(USAGE_LIMIT_FILE, 'w') as f:
        json.dump(usage_data, f, indent=4)

# Fungsi untuk memeriksa dan update limit penggunaan /start
def check_start_limit(chat_id):
    # Admin tidak terkena limit
    if is_admin(chat_id):
        return True
    
    usage_data = load_usage_data()
    chat_id_str = str(chat_id)
    current_time = time.time()
    
    # Jika user belum ada dalam data, buat entry baru
    if chat_id_str not in usage_data:
        usage_data[chat_id_str] = {
            'count': 1,
            'first_use': current_time,
            'last_use': current_time
        }
        save_usage_data(usage_data)
        return True
    
    user_data = usage_data[chat_id_str]
    last_use_time = user_data['last_use']
    
    # Cek apakah sudah lewat 24 jam dari penggunaan pertama hari ini
    time_diff = current_time - user_data['first_use']
    
    if time_diff >= 24 * 60 * 60:  # 24 jam dalam detik
        # Reset counter jika sudah lewat 24 jam
        user_data['count'] = 1
        user_data['first_use'] = current_time
        user_data['last_use'] = current_time
        save_usage_data(usage_data)
        return True
    
    # Cek apakah masih dalam batas limit
    if user_data['count'] < 2:
        user_data['count'] += 1
        user_data['last_use'] = current_time
        save_usage_data(usage_data)
        return True
    else:
        # Hitung waktu tunggu sampai reset
        reset_time = user_data['first_use'] + (24 * 60 * 60)
        wait_time = reset_time - current_time
        return wait_time

# Fungsi untuk memuat daftar blacklist
def load_blacklist():
    if not os.path.exists(BLACKLIST_FILE):
        return set()
    
    with open(BLACKLIST_FILE, 'r') as f:
        blacklisted = set(line.strip() for line in f if line.strip())
    return blacklisted

# Fungsi untuk menyimpan blacklist
def save_blacklist(blacklisted):
    with open(BLACKLIST_FILE, 'w') as f:
        for chat_id in blacklisted:
            f.write(f"{chat_id}\n")

# Fungsi untuk menambahkan chat ID ke blacklist
def add_to_blacklist(chat_id):
    blacklisted = load_blacklist()
    blacklisted.add(str(chat_id))
    save_blacklist(blacklisted)
    
    # Kirim pesan notifikasi ke user yang diblacklist
    try:
        bot.send_message(
            chat_id, 
            "‼️ Maaf kamu sudah tidak bisa mengakses bot ini karena telah melanggar ketentuan yang telah di tetapkan."
        )
    except Exception as e:
        print(f"Gagal mengirim pesan blacklist ke {chat_id}: {e}")

# Fungsi untuk menghapus chat ID dari blacklist
def remove_from_blacklist(chat_id):
    blacklisted = load_blacklist()
    blacklisted.discard(str(chat_id))
    save_blacklist(blacklisted)
    
    # Reset usage limit ketika diunblacklist
    usage_data = load_usage_data()
    chat_id_str = str(chat_id)
    if chat_id_str in usage_data:
        del usage_data[chat_id_str]
        save_usage_data(usage_data)
    
    # Kirim pesan notifikasi ke user yang diunblacklist
    try:
        bot.send_message(
            chat_id, 
            "♻️ Kamu sudah bisa menggunakan kembali bot ini. tetap patuhi aturan yang berlaku"
        )
    except Exception as e:
        print(f"Gagal mengirim pesan unblacklist ke {chat_id}: {e}")

# Fungsi untuk memeriksa apakah user diblokir
def is_blacklisted(chat_id):
    return str(chat_id) in load_blacklist()

# Fungsi untuk memeriksa apakah user adalah admin
def is_admin(chat_id):
    return chat_id == ADMIN_CHAT_ID

# Fungsi untuk format waktu
def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours} jam {minutes} menit"

# Handler untuk perintah /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    
    # Cek apakah user diblokir
    if is_blacklisted(chat_id):
        bot.send_message(chat_id, "‼️ Maaf kamu sudah tidak bisa mengakses bot ini karena telah melanggar ketentuan yang telah di tetapkan.")
        return
    
    # Cek limit penggunaan /start (kecuali admin)
    if not is_admin(chat_id):
        limit_check = check_start_limit(chat_id)
        
        if limit_check is not True:
            # User melebihi limit, tampilkan pesan error
            wait_time = format_time(limit_check)
            bot.send_message(
                chat_id,
                f"❌ *Limit Tercapai*\n\n"
                f"Kamu sudah encapai batas akses menu bot sebanyak 2 kali hari ini.\n"
                f"Silakan tunggu {wait_time} lagi untuk menggunakan perintah ini kembali.\n\n"
                f"🚨 *Ingat:* Jangan spam pembuatan akun!",
                parse_mode='Markdown'
            )
            return
    
    # Dapatkan info penggunaan saat ini
    usage_data = load_usage_data()
    chat_id_str = str(chat_id)
    
    # Tampilkan info penggunaan yang berbeda untuk admin dan user biasa
    if is_admin(chat_id):
        usage_info = "♾️ *Unlimited* (Admin)"
        current_count = "∞"
    else:
        current_count = usage_data.get(chat_id_str, {}).get('count', 1) if chat_id_str in usage_data else 1
        usage_info = f"{current_count}/2"
    
    # Membuat inline keyboard
    markup = InlineKeyboardMarkup(row_width=2)
    
    # Membuat tombol inline dasar
    btn_vmess = InlineKeyboardButton("🔄 VMESS", callback_data="vmess")
    btn_vless = InlineKeyboardButton("⚡ VLESS", callback_data="vless")
    btn_trojan = InlineKeyboardButton("🔒 TROJAN", callback_data="trojan")
    
    # Menambahkan tombol dasar ke keyboard
    markup.add(btn_vmess, btn_vless, btn_trojan)
    
    # Jika user adalah admin, tambahkan tombol admin
    if is_admin(chat_id):
        btn_admin = InlineKeyboardButton("👑 ADMIN PANEL", callback_data="admin_panel")
        markup.add(btn_admin)
    
    welcome_text = f"""
🤖 *Welcome to VPN Bot*

*Harga VPN* : Rp233/hari
*Limit* : 2 Device
*Support* : HP & STB

📊 *Sisa akses menu bot:* {usage_info}

‼️Bot tidak menggunakan Payment Gateway jadi setelah akun berhasil dibuat 
silahkan lakukan pembayaran ke admin @sanmaxx . Jika tidak ada pembayaran kamu akan di
blokir dari akses bot dan akun yang dibuat akan di hapus.

Jika Berminat Join Reseller Bisa Hubungi Admin, Dengan Harga lebih murah
"""
    
    bot.send_message(
        chat_id, 
        welcome_text, 
        reply_markup=markup,
        parse_mode='Markdown'
    )

# Handler untuk callback query
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    
    # Cek apakah user diblokir
    if is_blacklisted(chat_id):
        bot.answer_callback_query(call.id, "❌ Anda telah diblokir!")
        return
    
    # Handle tombol admin panel
    if call.data == "admin_panel":
        if is_admin(chat_id):
            show_admin_panel(call)
        else:
            bot.answer_callback_query(call.id, "❌ Akses ditolak!")
        return
    
    # Handle tombol blacklist
    elif call.data == "blacklist_user":
        if is_admin(chat_id):
            bot.answer_callback_query(call.id)
            msg = bot.send_message(chat_id, "📝 Masukkan Chat ID yang ingin diblacklist:")
            bot.register_next_step_handler(msg, process_blacklist)
        else:
            bot.answer_callback_query(call.id, "❌ Akses ditolak!")
        return
    
    # Handle tombol unblacklist
    elif call.data == "unblacklist_user":
        if is_admin(chat_id):
            show_unblacklist_menu(call)
        else:
            bot.answer_callback_query(call.id, "❌ Akses ditolak!")
        return
    
    # Handle tombol lihat blacklist
    elif call.data == "view_blacklist":
        if is_admin(chat_id):
            show_blacklist(call)
        else:
            bot.answer_callback_query(call.id, "❌ Akses ditolak!")
        return
    
    # Handle tombol lihat usage limit
    elif call.data == "view_usage_limit":
        if is_admin(chat_id):
            show_usage_limit(call)
        else:
            bot.answer_callback_query(call.id, "❌ Akses ditolak!")
        return
    
    # Handle tombol reset usage limit
    elif call.data.startswith("reset_usage_"):
        if is_admin(chat_id):
            target_chat_id = call.data.split("_")[2]
            reset_usage_limit(target_chat_id)
            bot.answer_callback_query(call.id, f"✅ Usage limit untuk {target_chat_id} telah direset!")
            show_usage_limit(call)
        else:
            bot.answer_callback_query(call.id, "❌ Akses ditolak!")
        return
    
    # Handle tombol kirim pesan ke user
    elif call.data == "send_message":
        if is_admin(chat_id):
            bot.answer_callback_query(call.id)
            msg = bot.send_message(chat_id, "📝 Masukkan Chat ID tujuan dan pesan (format: <chat_id>|<pesan>):")
            bot.register_next_step_handler(msg, process_send_message)
        else:
            bot.answer_callback_query(call.id, "❌ Akses ditolak!")
        return
    
    # Handle tombol unblacklist spesifik
    elif call.data.startswith("unblacklist_"):
        if is_admin(chat_id):
            target_chat_id = call.data.split("_")[1]
            remove_from_blacklist(target_chat_id)
            bot.answer_callback_query(call.id, f"✅ Chat ID {target_chat_id} telah diunblacklist!")
            show_unblacklist_menu(call)
        else:
            bot.answer_callback_query(call.id, "❌ Akses ditolak!")
        return
    
    # Handle tombol kembali ke admin panel
    elif call.data == "back_to_admin":
        if is_admin(chat_id):
            show_admin_panel(call)
        else:
            bot.answer_callback_query(call.id, "❌ Akses ditolak!")
        return
    
    # Handle tombol kembali ke menu utama
    elif call.data == "back_to_main":
        send_welcome(call.message)
        return
    
    # Handle tombol konfigurasi VPN biasa
    elif call.data == "vmess":
        bot.edit_message_reply_markup(
               chat_id=call.message.chat.id,
               message_id=call.message.message_id,
               reply_markup=None
        )
        create_vmess_account(bot, call.message)
    elif call.data == "vless":
        bot.edit_message_reply_markup(
               chat_id=call.message.chat.id,
               message_id=call.message.message_id,
               reply_markup=None
        )
        create_vless_account(bot, call.message)
    elif call.data == "trojan":
        bot.edit_message_reply_markup(
               chat_id=call.message.chat.id,
               message_id=call.message.message_id,
               reply_markup=None
        )
        create_trojan_account(bot, call.message)

# Fungsi untuk menampilkan panel admin
def show_admin_panel(call):
    markup = InlineKeyboardMarkup(row_width=1)
    
    btn_blacklist = InlineKeyboardButton("🚫 Blacklist User", callback_data="blacklist_user")
    btn_unblacklist = InlineKeyboardButton("✅ Unblacklist User", callback_data="unblacklist_user")
    btn_view_blacklist = InlineKeyboardButton("📋 Lihat Daftar Blacklist", callback_data="view_blacklist")
    btn_view_usage = InlineKeyboardButton("📊 Lihat Usage Limit", callback_data="view_usage_limit")
    btn_send_message = InlineKeyboardButton("📨 Kirim Pesan ke User", callback_data="send_message")
    btn_back = InlineKeyboardButton("🔙 Kembali", callback_data="back_to_main")
    
    markup.add(btn_blacklist, btn_unblacklist, btn_view_blacklist, btn_view_usage, btn_send_message, btn_back)
    
    bot.edit_message_text(
        "👑 **Admin Panel**\n\nPilih opsi yang diinginkan:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

# Fungsi untuk menampilkan daftar blacklist
def show_blacklist(call):
    blacklisted = load_blacklist()
    
    if not blacklisted:
        text = "📋 **Daftar Blacklist**\n\nTidak ada chat ID yang diblacklist."
    else:
        text = "📋 **Daftar Blacklist**\n\n"
        for chat_id in blacklisted:
            text += f"• `{chat_id}`\n"
    
    markup = InlineKeyboardMarkup(row_width=1)
    btn_back = InlineKeyboardButton("🔙 Kembali ke Admin Panel", callback_data="back_to_admin")
    markup.add(btn_back)
    
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

# Fungsi untuk menampilkan usage limit
def show_usage_limit(call):
    usage_data = load_usage_data()
    
    if not usage_data:
        text = "📊 **Data Usage Limit**\n\nTidak ada data penggunaan."
    else:
        text = "📊 **Data Usage Limit**\n\n"
        for chat_id, data in usage_data.items():
            count = data.get('count', 0)
            last_use = datetime.fromtimestamp(data.get('last_use', 0)).strftime('%Y-%m-%d %H:%M:%S')
            # Tandai jika ini adalah admin
            admin_status = " 👑" if int(chat_id) == ADMIN_CHAT_ID else ""
            text += f"• `{chat_id}`: {count}/2 (Terakhir: {last_use}){admin_status}\n"
    
    markup = InlineKeyboardMarkup(row_width=1)
    
    # Tambahkan tombol reset untuk setiap user (kecuali admin)
    for chat_id in usage_data.keys():
        if int(chat_id) != ADMIN_CHAT_ID:  # Jangan tampilkan tombol reset untuk admin
            btn_reset = InlineKeyboardButton(f"🔄 Reset {chat_id}", callback_data=f"reset_usage_{chat_id}")
            markup.add(btn_reset)
    
    btn_back = InlineKeyboardButton("🔙 Kembali ke Admin Panel", callback_data="back_to_admin")
    markup.add(btn_back)
    
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

# Fungsi untuk reset usage limit
def reset_usage_limit(chat_id):
    # Jangan reset usage limit untuk admin
    if int(chat_id) == ADMIN_CHAT_ID:
        return
    
    usage_data = load_usage_data()
    chat_id_str = str(chat_id)
    
    if chat_id_str in usage_data:
        del usage_data[chat_id_str]
        save_usage_data(usage_data)

# Fungsi untuk menampilkan menu unblacklist
def show_unblacklist_menu(call):
    blacklisted = load_blacklist()
    
    if not blacklisted:
        text = "✅ **Unblacklist User**\n\nTidak ada chat ID yang diblacklist."
        markup = InlineKeyboardMarkup(row_width=1)
        btn_back = InlineKeyboardButton("🔙 Kembali ke Admin Panel", callback_data="back_to_admin")
        markup.add(btn_back)
    else:
        text = "✅ **Unblacklist User**\n\nPilih user yang ingin diunblacklist:"
        markup = InlineKeyboardMarkup(row_width=1)
        for chat_id in blacklisted:
            # Tandai jika ini adalah admin (seharusnya tidak mungkin admin diblacklist, tapi untuk keamanan)
            admin_status = " 👑" if int(chat_id) == ADMIN_CHAT_ID else ""
            btn_user = InlineKeyboardButton(f"❌ {chat_id}{admin_status}", callback_data=f"unblacklist_{chat_id}")
            markup.add(btn_user)
        btn_back = InlineKeyboardButton("🔙 Kembali ke Admin Panel", callback_data="back_to_admin")
        markup.add(btn_back)
    
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

# Proses blacklist user
def process_blacklist(message):
    chat_id = message.chat.id
    target_chat_id = message.text.strip()
    
    try:
        # Validasi chat ID
        target_id = int(target_chat_id)
        
        # Cegah admin memblacklist diri sendiri
        if target_id == ADMIN_CHAT_ID:
            bot.send_message(chat_id, "❌ Tidak bisa memblacklist admin!")
            show_admin_panel_from_message(message)
            return
        
        add_to_blacklist(target_chat_id)
        bot.send_message(chat_id, f"✅ Chat ID `{target_chat_id}` telah berhasil diblacklist!", parse_mode='Markdown')
        show_admin_panel_from_message(message)
    except ValueError:
        bot.send_message(chat_id, "❌ Format Chat ID tidak valid! Harus berupa angka.")
        show_admin_panel_from_message(message)

# Proses kirim pesan ke user tertentu
def process_send_message(message):
    chat_id = message.chat.id
    data = message.text.strip()
    
    try:
        if '|' not in data:
            bot.send_message(chat_id, "❌ Format salah! Gunakan: <chat_id>|<pesan>")
            show_admin_panel_from_message(message)
            return
        
        target_chat_id, user_message = data.split('|', 1)
        target_chat_id = target_chat_id.strip()
        user_message = user_message.strip()
        
        # Validasi chat ID
        target_id = int(target_chat_id)
        
        # Cek apakah target diblacklist
        if is_blacklisted(target_chat_id):
            bot.send_message(chat_id, f"❌ Chat ID `{target_chat_id}` sedang diblacklist!", parse_mode='Markdown')
            show_admin_panel_from_message(message)
            return
        
        # Kirim pesan ke user
        try:
            bot.send_message(target_chat_id, f"📨 **Pesan dari Admin:**\n\n{user_message}", parse_mode='Markdown')
            bot.send_message(chat_id, f"✅ Pesan berhasil dikirim ke `{target_chat_id}`!", parse_mode='Markdown')
        except Exception as e:
            bot.send_message(chat_id, f"❌ Gagal mengirim pesan ke `{target_chat_id}`: {str(e)}", parse_mode='Markdown')
        
        show_admin_panel_from_message(message)
        
    except ValueError:
        bot.send_message(chat_id, "❌ Format Chat ID tidak valid! Harus berupa angka.")
        show_admin_panel_from_message(message)

# Fungsi bantu untuk menampilkan admin panel dari message handler
def show_admin_panel_from_message(message):
    markup = InlineKeyboardMarkup(row_width=1)
    
    btn_blacklist = InlineKeyboardButton("🚫 Blacklist User", callback_data="blacklist_user")
    btn_unblacklist = InlineKeyboardButton("✅ Unblacklist User", callback_data="unblacklist_user")
    btn_view_blacklist = InlineKeyboardButton("📋 Lihat Daftar Blacklist", callback_data="view_blacklist")
    btn_view_usage = InlineKeyboardButton("📊 Lihat Usage Limit", callback_data="view_usage_limit")
    btn_send_message = InlineKeyboardButton("📨 Kirim Pesan ke User", callback_data="send_message")
    btn_back = InlineKeyboardButton("🔙 Kembali", callback_data="back_to_main")
    
    markup.add(btn_blacklist, btn_unblacklist, btn_view_blacklist, btn_view_usage, btn_send_message, btn_back)
    
    bot.send_message(
        message.chat.id,
        "👑 **Admin Panel**\n\nPilih opsi yang diinginkan:",
        reply_markup=markup,
        parse_mode='Markdown'
    )

# Handler untuk callback kembali ke menu utama
@bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
def back_to_main(call):
    send_welcome(call.message)

# Jalankan bot
if __name__ == "__main__":
    print("Bot is running...")
    print(f"Admin Chat ID: {ADMIN_CHAT_ID}")
    bot.polling(none_stop=True)
