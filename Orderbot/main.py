import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

# Konfigurasi
BOT_TOKEN = "7618239092:AAGeuIEoDpsEAQkCVPyo3mbBDc-rZ5o3QQQ"
ADMIN_CHAT_ID = 576495165
BLACKLIST_FILE = "blacklist.txt"

# Inisialisasi bot
bot = telebot.TeleBot(BOT_TOKEN)

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

# Handler untuk perintah /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    
    # Cek apakah user diblokir
    if is_blacklisted(chat_id):
        bot.send_message(chat_id, "‼️ Maaf kamu sudah tidak bisa mengakses bot ini karena telah melanggar ketentuan yang telah di tetapkan.")
        return
    
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
    
    welcome_text = """
🤖 *Welcome to VPN Bot*

*CHATID* : {chat_id}

*Harga VPN* : 7.000/30hari
*Limit* : 2 Device
*Support* : HP & STB

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
        bot.answer_callback_query(call.id, "VMESS selected!")
    elif call.data == "vless":
        bot.answer_callback_query(call.id, "VLESS selected!")
    elif call.data == "trojan":
        bot.answer_callback_query(call.id, "TROJAN selected!")

# Fungsi untuk menampilkan panel admin
def show_admin_panel(call):
    markup = InlineKeyboardMarkup(row_width=1)
    
    btn_blacklist = InlineKeyboardButton("🚫 Blacklist User", callback_data="blacklist_user")
    btn_unblacklist = InlineKeyboardButton("✅ Unblacklist User", callback_data="unblacklist_user")
    btn_view_blacklist = InlineKeyboardButton("📋 Lihat Daftar Blacklist", callback_data="view_blacklist")
    btn_send_message = InlineKeyboardButton("📨 Kirim Pesan ke User", callback_data="send_message")
    btn_back = InlineKeyboardButton("🔙 Kembali", callback_data="back_to_main")
    
    markup.add(btn_blacklist, btn_unblacklist, btn_view_blacklist, btn_send_message, btn_back)
    
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
            btn_user = InlineKeyboardButton(f"❌ {chat_id}", callback_data=f"unblacklist_{chat_id}")
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
        int(target_chat_id)
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
        int(target_chat_id)
        
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
    btn_send_message = InlineKeyboardButton("📨 Kirim Pesan ke User", callback_data="send_message")
    btn_back = InlineKeyboardButton("🔙 Kembali", callback_data="back_to_main")
    
    markup.add(btn_blacklist, btn_unblacklist, btn_view_blacklist, btn_send_message, btn_back)
    
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
