#!/bin/bash

cd 
mkdir -p sanbot
cd sanbot

wget -q https://raw.githubusercontent.com/Sandhj/ST/main/Reseller/create_vmess.py
wget -q https://raw.githubusercontent.com/Sandhj/ST/main/Reseller/create_vless.py
wget -q https://raw.githubusercontent.com/Sandhj/ST/main/Reseller/create_trojan.py

# Install Modul
python3 -m venv bot
source bot/bin/activate
pip install pyTelegramBotAPI
deactivate



cat <<EOL > /root/sanbot/run.sh
#!/bin/bash
source /root/sanbot/bot/bin/activate
python3 /root/sanbot/menu.py
EOL

# Buat file service systemd
cat <<EOF > /etc/systemd/system/sanbot.service
[Unit]
Description=San Bot Manager
After=network.target

[Service]
ExecStart=/usr/bin/bash /root/sanbot/run.sh
WorkingDirectory=/root/sanbot/
StandardOutput=inherit
StandardError=inherit
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd dan mulai service
systemctl daemon-reload
systemctl enable sanbot
systemctl start sanbot
echo "Tekan Enter Untuk Menuju Menu Utama(↩️)"
read -s
menu
