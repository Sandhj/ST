import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Inisialisasi bot
bot = telebot.TeleBot('8255110757:AAFGiEMmjP8LWPbcArK2QDafxq12j7NKPkc')

# Daftar ID telegram yang diizinkan (ganti dengan ID reseller Anda)
authorized_ids = [576495165, 987654321, 555666777]  # Contoh ID, ganti dengan yang asli

# Handler command start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Cek authorized access
    if message.from_user.id not in authorized_ids:
        bot.send_message(message.chat.id, "❌ *Akses Ditolak*\n\nAnda tidak memiliki akses ke bot ini.", parse_mode='Markdown')
        return
    
    markup = InlineKeyboardMarkup(row_width=2)
    
    btn_vmess = InlineKeyboardButton("🔄 VMESS", callback_data="vmess")
    btn_vless = InlineKeyboardButton("⚡ VLESS", callback_data="vless")
    btn_trojan = InlineKeyboardButton("🔒 TROJAN", callback_data="trojan")
    
    markup.add(btn_vmess, btn_vless, btn_trojan)
    
    welcome_text = """
✨ *SANSTORE BOT* ✨
*Your Trusted VPN Reseller Partner*

🤝 *RESELLER AREA*
📈 Tingkatkan bisnis Anda dengan layanan premium kami
💰 Harga khusus reseller

Pilih protocol yang Anda butuhkan:
"""
    
    bot.send_message(message.chat.id, welcome_text, 
                    parse_mode='Markdown', 
                    reply_markup=markup)

# Handler callback
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if data == 'menu_ssh':
        menu_ssh(call.message)
    elif data == 'menu_vmess':
        menu_vmess(call.message)

# Jalankan bot
print("Bot SANSTORE berjalan...")
print(f"Authorized users: {authorized_ids}")
bot.polling()
