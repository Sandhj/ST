import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import threading
import time

from create_vmess import create_vmess_account
from create_vless import create_vless_account
from create_trojan import create_trojan_account

# Inisialisasi bot
bot = telebot.TeleBot('8255110757:AAFGiEMmjP8LWPbcArK2QDafxq12j7NKPkc')

# ID grup yang diizinkan
GROUP_CHAT_ID = -1003223194568

# Dictionary untuk menyimpan member baru yang perlu konfirmasi
pending_members = {}
# Set untuk menyimpan admin yang berhak melakukan konfirmasi
admins = set()  # Format: {user_id1, user_id2, ...}

# Waktu tunggu konfirmasi (dalam detik)
CONFIRMATION_TIMEOUT = 300  # 5 menit

# Fungsi untuk cek apakah user adalah member grup
def is_group_member(user_id):
    try:
        member_status = bot.get_chat_member(GROUP_CHAT_ID, user_id).status
        # Status yang diizinkan: 'member', 'administrator', 'creator'
        return member_status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Error checking group membership: {e}")
        return False

# Fungsi untuk cek apakah user adalah admin bot
def is_bot_admin(user_id):
    return user_id in admins

# Fungsi untuk menambahkan admin baru
def add_admin(user_id, username=None):
    admins.add(user_id)
    print(f"Admin added: {user_id} ({username})")

# Fungsi untuk menghapus admin
def remove_admin(user_id):
    if user_id in admins:
        admins.remove(user_id)
        print(f"Admin removed: {user_id}")

# Fungsi untuk mendapatkan daftar admin
def get_admin_list():
    admin_list = []
    for admin_id in admins:
        try:
            user = bot.get_chat(admin_id)
            admin_list.append(f"ID: {admin_id} | Username: @{user.username if user.username else 'N/A'}")
        except:
            admin_list.append(f"ID: {admin_id} | Username: N/A")
    return admin_list

# Fungsi untuk menangani member baru yang bergabung
@bot.message_handler(content_types=['new_chat_members'])
def handle_new_members(message):
    for new_member in message.new_chat_members:
        if not new_member.is_bot:  # Abaikan bot
            user_id = new_member.id
            username = f"@{new_member.username}" if new_member.username else f"User#{user_id}"
            
            # Simpan informasi member baru
            pending_members[user_id] = {
                'username': username,
                'first_name': new_member.first_name,
                'join_time': time.time(),
                'message_id': message.message_id
            }
            
            # Buat keyboard konfirmasi
            markup = InlineKeyboardMarkup()
            btn_confirm = InlineKeyboardButton("✅ Konfirmasi Member", callback_data=f"confirm_{user_id}")
            btn_kick = InlineKeyboardButton("❌ Tolak & Keluarkan", callback_data=f"reject_{user_id}")
            markup.add(btn_confirm, btn_kick)
            
            # Kirim notifikasi ke admin
            for admin_id in admins:
                try:
                    bot.send_message(
                        admin_id,
                        f"🆕 *MEMBER BARU MENUNGGU KONFIRMASI*\n\n"
                        f"👤 *Username:* {username}\n"
                        f"📛 *Nama:* {new_member.first_name}\n"
                        f"🆔 *User ID:* `{user_id}`\n\n"
                        f"⏰ *Waktu Konfirmasi:* {CONFIRMATION_TIMEOUT//60} menit",
                        parse_mode='Markdown',
                        reply_markup=markup
                    )
                except Exception as e:
                    print(f"Error sending notification to admin {admin_id}: {e}")
            
            # Mulai timer untuk auto kick
            start_auto_kick_timer(user_id)
            
            print(f"New member pending confirmation: {username} (ID: {user_id})")

# Fungsi untuk auto kick member yang tidak dikonfirmasi
def start_auto_kick_timer(user_id):
    def auto_kick():
        time.sleep(CONFIRMATION_TIMEOUT)
        if user_id in pending_members:
            # Kick member dari grup
            try:
                bot.ban_chat_member(GROUP_CHAT_ID, user_id)
                bot.unban_chat_member(GROUP_CHAT_ID, user_id)
                
                # Hapus dari pending members
                member_info = pending_members.pop(user_id)
                
                # Beritahu admin
                for admin_id in admins:
                    try:
                        bot.send_message(
                            admin_id,
                            f"⏰ *MEMBER DIKELUARKAN OTOMATIS*\n\n"
                            f"👤 *Username:* {member_info['username']}\n"
                            f"📛 *Nama:* {member_info['first_name']}\n"
                            f"🆔 *User ID:* `{user_id}`\n\n"
                            f"❌ *Alasan:* Timeout konfirmasi",
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        print(f"Error notifying admin about auto-kick: {e}")
                
                print(f"Member auto-kicked: {member_info['username']} (ID: {user_id})")
                
            except Exception as e:
                print(f"Error auto-kicking member {user_id}: {e}")
    
    thread = threading.Thread(target=auto_kick)
    thread.daemon = True
    thread.start()

# Handler untuk konfirmasi admin
@bot.callback_query_handler(func=lambda call: call.data.startswith(('confirm_', 'reject_')))
def handle_confirmation(call):
    if not is_bot_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Hanya admin yang dapat melakukan konfirmasi!", show_alert=True)
        return
    
    action, user_id_str = call.data.split('_')
    user_id = int(user_id_str)
    
    if user_id not in pending_members:
        bot.answer_callback_query(call.id, "❌ Member sudah diproses atau timeout!", show_alert=True)
        return
    
    member_info = pending_members[user_id]
    
    if action == 'confirm':
        # Konfirmasi member
        del pending_members[user_id]
        
        # Edit pesan asli
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"✅ *MEMBER DIKONFIRMASI*\n\n"
                 f"👤 *Username:* {member_info['username']}\n"
                 f"📛 *Nama:* {member_info['first_name']}\n"
                 f"🆔 *User ID:* `{user_id}`\n\n"
                 f"Oleh: @{call.from_user.username if call.from_user.username else 'N/A'}",
            parse_mode='Markdown'
        )
        
        # Kirim welcome message ke member
        try:
            bot.send_message(
                user_id,
                f"🎉 *SELAMAT DATANG!*\n\n"
                f"Halo {member_info['first_name']}!\n\n"
                f"Keanggotaan Anda telah dikonfirmasi oleh admin. "
                f"Sekarang Anda dapat menggunakan bot ini dengan mengirim perintah /start",
                parse_mode='Markdown'
            )
        except:
            pass  # User mungkin belum memulai chat dengan bot
        
        print(f"Member confirmed: {member_info['username']} (ID: {user_id})")
        
    elif action == 'reject':
        # Tolak dan kick member
        try:
            bot.ban_chat_member(GROUP_CHAT_ID, user_id)
            bot.unban_chat_member(GROUP_CHAT_ID, user_id)
        except Exception as e:
            print(f"Error kicking member: {e}")
        
        del pending_members[user_id]
        
        # Edit pesan asli
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"❌ *MEMBER DITOLAK*\n\n"
                 f"👤 *Username:* {member_info['username']}\n"
                 f"📛 *Nama:* {member_info['first_name']}\n"
                 f"🆔 *User ID:* `{user_id}`\n\n"
                 f"Oleh: @{call.from_user.username if call.from_user.username else 'N/A'}",
            parse_mode='Markdown'
        )
        
        print(f"Member rejected: {member_info['username']} (ID: {user_id})")
    
    bot.answer_callback_query(call.id)

# Handler command untuk admin management
@bot.message_handler(commands=['admin'])
def admin_management(message):
    if not is_bot_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Anda bukan admin!")
        return
    
    markup = InlineKeyboardMarkup(row_width=2)
    btn_add = InlineKeyboardButton("➕ Tambah Admin", callback_data="admin_add")
    btn_remove = InlineKeyboardButton("➖ Hapus Admin", callback_data="admin_remove")
    btn_list = InlineKeyboardButton("📋 List Admin", callback_data="admin_list")
    btn_pending = InlineKeyboardButton("⏳ Pending Members", callback_data="admin_pending")
    
    markup.add(btn_add, btn_remove, btn_list, btn_pending)
    
    bot.send_message(
        message.chat.id,
        "👨‍💼 *ADMIN MANAGEMENT*\n\nPilih opsi yang diinginkan:",
        parse_mode='Markdown',
        reply_markup=markup
    )

# Handler untuk kick member manual oleh admin
@bot.message_handler(commands=['kick'])
def kick_member(message):
    if not is_bot_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Anda bukan admin!")
        return
    
    if len(message.text.split()) < 2:
        bot.send_message(
            message.chat.id,
            "❌ *Format salah!*\n\nGunakan: `/kick <user_id atau username>`\nContoh: `/kick 123456789` atau `/kick @username`",
            parse_mode='Markdown'
        )
        return
    
    target = message.text.split()[1]
    
    try:
        # Coba parse sebagai user_id
        if target.startswith('@'):
            # Jika username, perlu mendapatkan user_id terlebih dahulu
            bot.send_message(message.chat.id, "⚠️ Fitur kick by username sedang dalam pengembangan. Gunakan User ID.")
            return
        else:
            user_id = int(target)
        
        # Kick member dari grup
        bot.ban_chat_member(GROUP_CHAT_ID, user_id)
        bot.unban_chat_member(GROUP_CHAT_ID, user_id)
        
        # Hapus dari pending members jika ada
        if user_id in pending_members:
            del pending_members[user_id]
        
        bot.send_message(
            message.chat.id,
            f"✅ *Member berhasil dikeluarkan!*\n\nUser ID: `{user_id}`",
            parse_mode='Markdown'
        )
        
    except ValueError:
        bot.send_message(message.chat.id, "❌ User ID harus berupa angka!")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")

# Handler callback untuk admin management
@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))
def handle_admin_callback(call):
    if not is_bot_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Anda bukan admin!", show_alert=True)
        return
    
    action = call.data.split('_')[1]
    
    if action == 'add':
        msg = bot.send_message(
            call.message.chat.id,
            "📝 *TAMBAH ADMIN*\n\nKirim User ID atau username admin baru:\n\nContoh: `123456789` atau `@username`",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(msg, process_add_admin)
        
    elif action == 'remove':
        if not admins:
            bot.send_message(call.message.chat.id, "❌ Tidak ada admin yang terdaftar!")
            return
        
        admin_text = "📋 *DAFTAR ADMIN*\n\n"
        for i, admin_id in enumerate(admins, 1):
            try:
                user = bot.get_chat(admin_id)
                admin_text += f"{i}. ID: `{admin_id}` | Username: @{user.username if user.username else 'N/A'}\n"
            except:
                admin_text += f"{i}. ID: `{admin_id}` | Username: N/A\n"
        
        admin_text += "\nKirim User ID yang ingin dihapus:"
        
        msg = bot.send_message(call.message.chat.id, admin_text, parse_mode='Markdown')
        bot.register_next_step_handler(msg, process_remove_admin)
        
    elif action == 'list':
        if not admins:
            bot.send_message(call.message.chat.id, "❌ Tidak ada admin yang terdaftar!")
            return
        
        admin_text = "👨‍💼 *DAFTAR ADMIN BOT*\n\n"
        for i, admin_id in enumerate(admins, 1):
            try:
                user = bot.get_chat(admin_id)
                admin_text += f"{i}. ID: `{admin_id}`\n   Username: @{user.username if user.username else 'N/A'}\n   Nama: {user.first_name}\n\n"
            except:
                admin_text += f"{i}. ID: `{admin_id}` | Username: N/A\n\n"
        
        bot.send_message(call.message.chat.id, admin_text, parse_mode='Markdown')
        
    elif action == 'pending':
        if not pending_members:
            bot.send_message(call.message.chat.id, "✅ Tidak ada member yang menunggu konfirmasi!")
            return
        
        pending_text = "⏳ *MEMBER MENUNGGU KONFIRMASI*\n\n"
        for i, (user_id, info) in enumerate(pending_members.items(), 1):
            time_left = CONFIRMATION_TIMEOUT - (time.time() - info['join_time'])
            minutes_left = max(0, int(time_left // 60))
            
            pending_text += f"{i}. {info['username']}\n   📛 Nama: {info['first_name']}\n   🆔 ID: `{user_id}`\n   ⏰ Sisa waktu: {minutes_left} menit\n\n"
        
        bot.send_message(call.message.chat.id, pending_text, parse_mode='Markdown')
    
    bot.answer_callback_query(call.id)

# Proses tambah admin
def process_add_admin(message):
    try:
        target = message.text.strip()
        user_id = None
        
        if target.startswith('@'):
            # Untuk username, perlu implementasi khusus
            bot.send_message(message.chat.id, "⚠️ Fitur tambah admin by username sedang dalam pengembangan. Gunakan User ID.")
            return
        else:
            user_id = int(target)
        
        # Verifikasi bahwa user exists
        user = bot.get_chat(user_id)
        
        add_admin(user_id, user.username)
        
        bot.send_message(
            message.chat.id,
            f"✅ *Admin berhasil ditambahkan!*\n\n"
            f"🆔 User ID: `{user_id}`\n"
            f"👤 Username: @{user.username if user.username else 'N/A'}\n"
            f"📛 Nama: {user.first_name}",
            parse_mode='Markdown'
        )
        
    except ValueError:
        bot.send_message(message.chat.id, "❌ User ID harus berupa angka!")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")

# Proses hapus admin
def process_remove_admin(message):
    try:
        user_id = int(message.text.strip())
        
        if user_id not in admins:
            bot.send_message(message.chat.id, "❌ User ID tidak ditemukan dalam daftar admin!")
            return
        
        remove_admin(user_id)
        bot.send_message(
            message.chat.id,
            f"✅ *Admin berhasil dihapus!*\n\nUser ID: `{user_id}`",
            parse_mode='Markdown'
        )
        
    except ValueError:
        bot.send_message(message.chat.id, "❌ User ID harus berupa angka!")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")

# Handler command start (tetap sama)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Cek apakah user adalah member grup
    if not is_group_member(message.from_user.id):
        bot.send_message(
            message.chat.id, 
            "❌ *Akses Ditolak*\n\nAnda harus menjadi member grup resmi untuk menggunakan bot ini.", 
            parse_mode='Markdown'
        )
        return
    
    markup = InlineKeyboardMarkup(row_width=2)
    
    btn_vmess = InlineKeyboardButton("🔄 VMESS", callback_data="vmess")
    btn_vless = InlineKeyboardButton("⚡ VLESS", callback_data="vless")
    btn_trojan = InlineKeyboardButton("🔒 TROJAN", callback_data="trojan")
    
    markup.add(btn_vmess, btn_vless, btn_trojan)
    
    welcome_text = """
✨ *SANSTORE BOT* ✨
*Your Trusted VPN Reseller Partner*

🤝 *MEMBER AREA*
📈 Akses khusus untuk member VIP/RESELLER
💰 Harga khusus untuk member VIP/RESELLER

Pilih protocol yang Anda butuhkan:
"""
    
    bot.send_message(message.chat.id, welcome_text, 
                    parse_mode='Markdown', 
                    reply_markup=markup)

# Handler callback - tambahkan pengecekan member grup juga
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    # Cek membership untuk setiap callback
    if not is_group_member(call.from_user.id):
        bot.answer_callback_query(
            call.id, 
            "❌ Akses ditolak. Anda harus menjadi member grup!", 
            show_alert=True
        )
        return
    
    if call.data == 'vmess':
        create_vmess_account(bot, call.message)
    elif call.data == 'vless':
        create_vless_account(bot, call.message)
    elif call.data == 'trojan':
        create_trojan_account(bot, call.message)

# Fungsi untuk inisialisasi admin pertama (opsional)
def initialize_first_admin():
    add_admin(576495165)

# Jalankan bot
if __name__ == "__main__":
    initialize_first_admin()
    print("Bot SANSTORE berjalan...")
    print(f"Authorized group: {GROUP_CHAT_ID}")
    print("Fitur konfirmasi member baru: AKTIF")
    print("Fitur admin management: AKTIF")
    bot.polling()