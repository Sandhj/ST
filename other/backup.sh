clear
mkdir -p /root/user/
echo -e "Sedang Menyiapkan Autobackup. . ."
sleep 2
read -p "Masukkan Token Bot Anda :" TOKEN
read -p "Masukkan ID Anda :" ID

TOKEN_TELE="$TOKEN"
ID_TELE="$ID"

cat << EOF > /root/user/backup.py
import os
import zipfile
import requests

# Konfigurasi
file_to_backup = "/usr/local/etc/xray/config/04_inbounds.json"
zip_file_name = "backup.zip"
telegram_bot_token = "$TOKEN_TELE"  # Ganti dengan token bot Anda
telegram_chat_id = "$ID_TELE"      # Ganti dengan ID chat penerima

def backup_file():
    try:
        # Pastikan file sumber ada
        if not os.path.exists(file_to_backup):
            print("File tidak ditemukan:", file_to_backup)
            return False
        
        # Buat file ZIP
        with zipfile.ZipFile(zip_file_name, "w") as zipf:
            zipf.write(file_to_backup, os.path.basename(file_to_backup))
        print(f"File berhasil di-zip: {zip_file_name}")
        return True
    except Exception as e:
        print("Terjadi kesalahan saat membuat ZIP:", str(e))
        return False

def send_to_telegram():
    try:
        # Kirim file ZIP ke bot Telegram
        url = f"https://api.telegram.org/bot{telegram_bot_token}/sendDocument"
        with open(zip_file_name, "rb") as file:
            response = requests.post(url, data={"chat_id": telegram_chat_id}, files={"document": file})
        
        if response.status_code == 200:
            print("File berhasil dikirim ke Telegram.")
        else:
            print("Gagal mengirim file ke Telegram:", response.text)
    except Exception as e:
        print("Terjadi kesalahan saat mengirim ke Telegram:", str(e))

if __name__ == "__main__":
    if backup_file():
        send_to_telegram()
EOF

#Memasang Schedule
SERVICE_NAME="backup"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
TIMER_FILE="/etc/systemd/system/${SERVICE_NAME}.timer"
SCRIPT_PATH="/root/user/backup.py"

# Pastikan script backup.py ada
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Script $SCRIPT_PATH tidak ditemukan!"
    exit 1
fi

# Buat service file
cat <<EOL > $SERVICE_FILE
[Unit]
Description=Backup Script Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 $SCRIPT_PATH
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOL

# Buat timer file
cat <<EOL > $TIMER_FILE
[Unit]
Description=Run Backup Script Every 3 Hours

[Timer]
OnCalendar=*-*-* 00,03,06,09,12,15,18,21:00:00
Unit=${SERVICE_NAME}.service

[Install]
WantedBy=timers.target
EOL

# Reload systemd
systemctl daemon-reload

# Enable dan start timer
systemctl enable ${SERVICE_NAME}.timer
systemctl start ${SERVICE_NAME}.timer

cd
wget -q https://raw.githubusercontent.com/Sandhj/ST/main/user.sh
chmod +x user.sh

echo -e "Sedang di Proses. . ."
sleep 2
echo -e "Sukses✓. . . ( Enter Untuk Kembali ke menu)"
read

rm backup.sh
menu
