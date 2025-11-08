import telebot
import re

# Path file konfigurasi Xray
FILE = "/usr/local/etc/xray/config/04_inbounds.json"

def get_user_list():
    """Mendapatkan daftar user dari file konfigurasi"""
    try:
        with open(FILE, 'r') as f:
            content = f.read()
        
        users = re.findall(r'###\s+(\S+)', content)
        return sorted(list(set(users)))
    except Exception as e:
        return None

def delete_user(username):
    """Menghapus user dari file konfigurasi"""
    try:
        with open(FILE, 'r') as f:
            lines = f.readlines()
        
        new_lines = []
        i = 0
        while i < len(lines):
            if f"### {username}" in lines[i]:
                i += 2
                continue
            new_lines.append(lines[i])
            i += 1
        
        with open(FILE, 'w') as f:
            f.writelines(new_lines)
        
        return True, "Sukses"
    except Exception as e:
        return False, str(e)

def delete_all_users():
    """Menghapus semua user dari file konfigurasi"""
    try:
        users = get_user_list()
        if not users:
            return False, "Tidak ada user yang ditemukan"
        
        for user in users:
            success, message = delete_user(user)
            if not success:
                return False, f"Gagal menghapus user {user}: {message}"
        
        return True, f"Semua {len(users)} user telah dihapus"
    except Exception as e:
        return False, str(e)


def delete_user_vmess(bot, message):
    """Handler untuk menghapus user - langsung tampilkan list"""
    users = get_user_list()
    
    if not users:
        bot.reply_to(message, "❌ Tidak ada user yang ditemukan.")
        return
    
    # Tampilkan daftar user dengan tombol inline
    user_list_text = "🗑️ *HAPUS USER VMESS*\n"
    user_list_text += "——————————————————\n"
    
    for i, user in enumerate(users, 1):
        user_list_text += f"{i}. `{user}`\n"
    
    user_list_text += "——————————————————\n"
    user_list_text += f"Total: *{len(users)}* user\n\n"
    user_list_text += "📝 *Balas dengan nomor user yang ingin dihapus*\n"
    user_list_text += "💀 Atau ketik *all* untuk hapus semua"
    
    msg = bot.reply_to(message, user_list_text, parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_user_selection, users, bot)

def process_user_selection(message, users, bot):
    """Memproses pilihan user dari pengguna"""
    try:
        user_input = message.text.strip()
        
        if user_input.lower() == 'all':
            # Konfirmasi hapus semua
            confirm_text = f"⚠️ *KONFIRMASI HAPUS SEMUA*\n\nTotal user: *{len(users)}*\n\nKetik `HAPUS SEMUA` untuk konfirmasi:"
            msg = bot.reply_to(message, confirm_text, parse_mode='Markdown')
            bot.register_next_step_handler(msg, process_delete_all_confirmation, bot)
            return
        
        if user_input.isdigit():
            user_number = int(user_input)
            if 1 <= user_number <= len(users):
                selected_user = users[user_number - 1]
                
                # Konfirmasi penghapusan user tertentu
                confirm_text = f"⚠️ *KONFIRMASI PENGHAPUSAN*\n\nUser: `{selected_user}`\n\nKetik `ya` untuk hapus user ini:"
                msg = bot.reply_to(message, confirm_text, parse_mode='Markdown')
                bot.register_next_step_handler(msg, process_single_delete_confirmation, selected_user, bot)
            else:
                bot.reply_to(message, f"❌ Nomor tidak valid. Pilih 1-{len(users)}")
        else:
            bot.reply_to(message, "❌ Input harus angka atau 'all'")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

def process_single_delete_confirmation(message, username, bot):
    """Memproses konfirmasi penghapusan user tunggal"""
    if message.text.lower() in ['ya', 'y', 'yes']:
        success, result_message = delete_user(username)
        if success:
            bot.reply_to(message, f"✅ *Sukses menghapus user* `{username}`", parse_mode='Markdown')
        else:
            bot.reply_to(message, f"❌ *Gagal menghapus user:* {result_message}", parse_mode='Markdown')
    else:
        bot.reply_to(message, "❌ Penghapusan dibatalkan.")

def process_delete_all_confirmation(message, bot):
    """Memproses konfirmasi penghapusan semua user"""
    if message.text.upper() == 'HAPUS SEMUA':
        success, result_message = delete_all_users()
        if success:
            bot.reply_to(message, f"✅ *{result_message}*", parse_mode='Markdown')
        else:
            bot.reply_to(message, f"❌ *Gagal menghapus semua user:* {result_message}", parse_mode='Markdown')
    else:
        bot.reply_to(message, "❌ Penghapusan semua user dibatalkan.")
