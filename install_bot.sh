#!/bin/bash

HOSTING="https://raw.githubusercontent.com/Sandhj/ST/main"

mkdir -p /usr/local/etc/xray/config >> /dev/null 2>&1

# === [INPUT DOMAIN] ===
mkdir -p /usr/local/etc/xray/config /usr/local/etc/xray/dns >> /dev/null 2>&1
touch /usr/local/etc/xray/dns/domain

echo "Install Paket Yang Dibutuhkan"
sleep 2
apt update -y
apt install -y socat netfilter-persistent bsdmainutils vnstat lsof fail2ban jq curl sudo cron
apt install -y build-essential libpcre3 libpcre3-dev zlib1g zlib1g-dev openssl libssl-dev \
               gcc clang llvm g++ valgrind make cmake debian-keyring debian-archive-keyring \
               apt-transport-https systemd bind9-host gnupg2 ca-certificates lsb-release \
               ubuntu-keyring unzip python-is-python3 python3-pip

pip install psutil pandas tabulate rich py-cpuinfo distro requests pycountry geoip2 --break-system-packages

# === [BUAT DIREKTORI & HAPUS KONFIG LAMA] ===
echo "Membuat direktori yang diperlukan..."
mkdir -p /user /tmp /usr/local/etc/xray /var/log/xray
rm -f /usr/local/etc/xray/city /usr/local/etc/xray/org /usr/local/etc/xray/timezone /usr/local/etc/xray/region

# === [DETEKSI OS] ===
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VERSION=$VERSION_ID
    else
        echo "Tidak dapat mendeteksi OS. Skrip ini hanya mendukung distribusi berbasis Debian dan Red Hat."
        exit 1
    fi
}

detect_os

if [[ "$OS" != "Ubuntu" && "$OS" != "Debian" && "$OS" != "Debian GNU/Linux" && \
      "$OS" != "CentOS" && "$OS" != "Fedora" && "$OS" != "Red Hat Enterprise Linux" ]]; then
    echo "Distribusi $OS tidak didukung oleh skrip ini. Proses instalasi dibatalkan."
    exit 1
fi

echo "Mendeteksi OS: $OS $VERSION"

# === [INSTAL XRAY-CORE] ===
get_latest_xray_version() {
    LATEST_VERSION=$(curl -s https://api.github.com/repos/XTLS/Xray-core/releases/latest | jq -r '.tag_name')
    if [ -z "$LATEST_VERSION" ]; then
        echo "Tidak dapat menemukan versi terbaru Xray-core."
        exit 1
    fi
}

install_xray_core() {
    ARCH=$(uname -m)
    case $ARCH in
        x86_64) ARCH="64" ;;
        aarch64) ARCH="arm64-v8a" ;;
        *) echo "Arsitektur $ARCH tidak didukung."; exit 1 ;;
    esac

    DOWNLOAD_URL="https://github.com/XTLS/Xray-core/releases/download/$LATEST_VERSION/Xray-linux-$ARCH.zip"

    echo "Mengunduh dan memasang Xray-core..."
    curl -L -o xray.zip "$DOWNLOAD_URL"
    unzip -o xray.zip -d /usr/local/bin
    rm xray.zip
    chmod +x /usr/local/bin/xray

    cat > /etc/systemd/system/xray.service <<EOF
[Unit]
Description=Xray Service
Documentation=https://github.com/xtls
After=network.target nss-lookup.target

[Service]
User=nobody
Group=nogroup
CapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
NoNewPrivileges=true
ExecStart=/usr/local/bin/xray run -confdir /usr/local/etc/xray/config/
RestartSec=5
Restart=always
StandardOutput=file:/var/log/xray/access.log
StandardError=file:/var/log/xray/error.log
SyslogIdentifier=xray
LimitNOFILE=infinity
OOMScoreAdjust=100

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable xray
    systemctl start xray
}

echo "Memeriksa versi terbaru Xray-core..."
get_latest_xray_version
echo "Versi terbaru Xray-core: $LATEST_VERSION"

echo "Memasang dependensi yang diperlukan..."
if [[ "$OS" == "Ubuntu" || "$OS" == "Debian" ]]; then
    apt install -y curl unzip
elif [[ "$OS" == "CentOS" || "$OS" == "Fedora" || "$OS" == "Red Hat Enterprise Linux" ]]; then
    yum install -y curl unzip
fi

install_xray_core
echo "Pemasangan Xray-core versi $LATEST_VERSION selesai."

# === [AMBIL INFO LOKASI] ===
echo "Mengumpulkan informasi lokasi dari ipinfo.io..."
curl -s ipinfo.io/city?token=f209571547ff6b > /usr/local/etc/xray/city
curl -s ipinfo.io/org?token=f209571547ff6b | cut -d " " -f 2-10 > /usr/local/etc/xray/org
curl -s ipinfo.io/timezone?token=f209571547ff6b > /usr/local/etc/xray/timezone
curl -s ipinfo.io/region?token=f209571547ff6b > /usr/local/etc/xray/region

# === [INSTAL SPEEDTEST CLI] ===
echo "Mengunduh dan menginstal Speedtest CLI..."
curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash &>/dev/null
apt-get install -y speedtest &>/dev/null
echo "Speedtest CLI berhasil diinstal."

# === [SET ZONA WAKTU] ===
echo "Mengatur zona waktu ke Asia/Jakarta..."
timedatectl set-timezone Asia/Jakarta &>/dev/null
echo "Zona waktu berhasil diatur."

# === [INSTAL WIREPROXY] ===
echo "Instalasi WireProxy"
rm -rf /usr/local/bin/wireproxy
wget -O /usr/local/bin/wireproxy "${HOSTING}/wireproxy"
chmod +x /usr/local/bin/wireproxy

cat > /etc/wireproxy.conf << END
[Interface]
PrivateKey = 4Osd07VYMrPGDtrJfRaRZ+ynuscBVi4PjzOZmLUJDlE=
Address = 172.16.0.2/32, 2606:4700:110:8fdc:f256:b15d:9e5c:5d1/128
DNS = 1.1.1.1, 1.0.0.1, 2606:4700:4700::1111, 2606:4700:4700::1001
MTU = 1280

[Peer]
PublicKey = bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo=
AllowedIPs = 0.0.0.0/0
AllowedIPs = ::/0
Endpoint = engage.cloudflareclient.com:2408

[Socks5]
BindAddress = 127.0.0.1:40000
END

cat > /etc/systemd/system/wireproxy.service << END
[Unit]
Description=WireProxy for WARP
After=network.target

[Service]
ExecStart=/usr/local/bin/wireproxy -c /etc/wireproxy.conf
RestartSec=5
Restart=always

[Install]
WantedBy=multi-user.target
END

systemctl daemon-reload
systemctl enable wireproxy
systemctl start wireproxy
systemctl restart wireproxy
echo "Instalasi WireProxy selesai."

# === [INSTAL NGINX] ===
detect_os_for_nginx() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
    else
        echo "OS tidak didukung. Hanya mendukung Ubuntu dan Debian."
        exit 1
    fi
}

add_nginx_repo() {
    if [ "$OS" == "ubuntu" ]; then
        apt install -y curl gnupg2 ca-certificates lsb-release ubuntu-keyring
        echo "deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] http://nginx.org/packages/mainline/ubuntu $(lsb_release -cs) nginx" > /etc/apt/sources.list.d/nginx.list
        curl -fsSL https://nginx.org/keys/nginx_signing.key | gpg --dearmor > /usr/share/keyrings/nginx-archive-keyring.gpg
    elif [ "$OS" == "debian" ]; then
        apt install -y curl gnupg2 ca-certificates lsb-release debian-archive-keyring
        echo "deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] http://nginx.org/packages/mainline/debian $(lsb_release -cs) nginx" > /etc/apt/sources.list.d/nginx.list
        curl -fsSL https://nginx.org/keys/nginx_signing.key | gpg --dearmor > /usr/share/keyrings/nginx-archive-keyring.gpg
    else
        echo "OS tidak didukung. Hanya mendukung Ubuntu dan Debian."
        exit 1
    fi
}

install_nginx() {
    apt update
    apt install -y nginx
    systemctl start nginx
    systemctl enable nginx
}

detect_os_for_nginx
add_nginx_repo
install_nginx

# Hapus konfigurasi default Nginx
rm -rf /etc/nginx/conf.d/default.conf /etc/nginx/sites-enabled/default /etc/nginx/sites-available/default /var/www/html/*
systemctl restart nginx

mkdir -p /var/www/html/xray
echo "Pemasangan dan konfigurasi Nginx telah selesai."

# === [SERTIFIKAT SSL DENGAN ACME.SH] ===
systemctl stop nginx
systemctl stop xray

install_acme_sh2() {
    domain=$(cat /usr/local/etc/xray/dns/domain)
    rm -rf ~/.acme.sh/*_ecc
    curl https://get.acme.sh | sh
    source ~/.bashrc
    ~/.acme.sh/acme.sh --register-account -m "$(echo $RANDOM | md5sum | head -c 6; echo;)@gmail.com" --server letsencrypt
    ~/.acme.sh/acme.sh --issue -d "$domain" --standalone --listen-v6 --server letsencrypt --keylength ec-256 \
        --fullchain-file /usr/local/etc/xray/fullchain.cer --key-file /usr/local/etc/xray/private.key \
        --reloadcmd "systemctl restart nginx" --force
    chmod 745 /usr/local/etc/xray/private.key
    echo "Sertifikat SSL berhasil dipasang!"
}

install_acme_sh2

# === [KONFIGURASI XRAY & NGINX] ===
echo "[ INFO ] Setup Nginx & Xray Config"

uuid=$(cat /proc/sys/kernel/random/uuid)
pwtr=$(openssl rand -hex 4)
pwss=$(echo $RANDOM | md5sum | head -c 6; echo;)
userpsk=$(openssl rand -base64 32)
serverpsk=$(openssl rand -base64 32)

escaped_uuid=$(printf '%s\n' "$uuid" | sed 's/[\/&]/\\&/g')
escaped_pwtr=$(printf '%s\n' "$pwtr" | sed 's/[\/&]/\\&/g')
escaped_pwss=$(printf '%s\n' "$pwss" | sed 's/[\/&]/\\&/g')
escaped_userpsk=$(printf '%s\n' "$userpsk" | sed 's/[\/&]/\\&/g')
escaped_serverpsk=$(printf '%s\n' "$serverpsk" | sed 's/[\/&]/\\&/g')

# Unduh konfigurasi Xray
wget -q -O /usr/local/etc/xray/config/00_log.json "${HOSTING}/config/00_log.json"
wget -q -O /usr/local/etc/xray/config/01_api.json "${HOSTING}/config/01_api.json"
wget -q -O /usr/local/etc/xray/config/02_dns.json "${HOSTING}/config/02_dns.json"
wget -q -O /usr/local/etc/xray/config/03_policy.json "${HOSTING}/config/03_policy.json"
wget -q -O /usr/local/etc/xray/config/04_inbounds.json "${HOSTING}/config/04_inbounds.json"
wget -q -O /usr/local/etc/xray/config/05_outbonds.json "${HOSTING}/config/05_outbonds.json"
wget -q -O /usr/local/etc/xray/config/06_routing.json "${HOSTING}/config/06_routing.json"
wget -q -O /usr/local/etc/xray/config/07_stats.json "${HOSTING}/config/07_stats.json"

sed -i \
    -e "s/UUID/$escaped_uuid/g" \
    -e "s/PWTR/$escaped_pwtr/g" \
    -e "s/PWSS/$escaped_pwss/g" \
    -e "s/USERPSK/$escaped_userpsk/g" \
    -e "s/SERVERPSK/$escaped_serverpsk/g" \
    /usr/local/etc/xray/config/04_inbounds.json

# Buat file log
touch /var/log/xray/access.log /var/log/xray/error.log
chown nobody:nogroup /var/log/xray/access.log /var/log/xray/error.log
chmod 664 /var/log/xray/access.log /var/log/xray/error.log

# Konfigurasi Nginx
wget -q -O /var/www/html/index.html "${HOSTING}/index.html"
wget -q -O /etc/nginx/nginx.conf "${HOSTING}/nginx.conf"
domain=$(cat /usr/local/etc/xray/dns/domain)
sed -i "s/server_name web.com;/server_name $domain;/g" /etc/nginx/nginx.conf
sed -i "s/server_name \*.web.com;/server_name \*.$domain;/g" /etc/nginx/nginx.conf

systemctl restart nginx
systemctl restart xray
echo "[ INFO ] Setup Done"

# === [BLOKIR TRAFFIC TORRENT] ===
iptables -A INPUT -p udp --dport 6881:6889 -j DROP
iptables -A INPUT -p tcp --dport 6881:6889 -j DROP
iptables -A INPUT -p tcp --dport 6881:6889 -m string --algo bm --string "BitTorrent" -j DROP
iptables -A INPUT -p udp --dport 6881:6889 -m string --algo bm --string "BitTorrent" -j DROP

# === [INSTAL MENU] ===
# Daftar file menu
cd
mkdir -p /root/san
cd /root/san
wget -q ${HOSTING}/menu/menu
wget -q ${HOSTING}/menu/settingmenu
wget -q ${HOSTING}/menu/sodosokmenu
wget -q ${HOSTING}/menu/trojanmenu
wget -q ${HOSTING}/menu/vlessmenu
wget -q ${HOSTING}/menu/vmessmenu
wget -q ${HOSTING}/menu/update

wget -q ${HOSTING}/other/about
wget -q ${HOSTING}/other/cek-xray
wget -q ${HOSTING}/other/certxray
wget -q ${HOSTING}/other/clear-log
wget -q ${HOSTING}/other/dns
wget -q ${HOSTING}/other/log-xray
wget -q ${HOSTING}/other/route-xray
wget -q ${HOSTING}/other/update-xray
wget -q ${HOSTING}/other/xp2

wget -q ${HOSTING}/xray/ss/create_ss
wget -q ${HOSTING}/xray/ss/delete_ss
wget -q ${HOSTING}/xray/ss/renew_ss
wget -q ${HOSTING}/xray/ss/list_ss

wget -q ${HOSTING}/xray/trojan/create_trojan
wget -q ${HOSTING}/xray/trojan/delete_trojan
wget -q ${HOSTING}/xray/trojan/renew_trojan
wget -q ${HOSTING}/xray/trojan/list_trojan
wget -q ${HOSTING}/xray/trojan/trojan_custom

wget -q ${HOSTING}/xray/vless/create_vless
wget -q ${HOSTING}/xray/vless/delete_vless
wget -q ${HOSTING}/xray/vless/renew_vless
wget -q ${HOSTING}/xray/vless/list_vless
wget -q ${HOSTING}/xray/vless/vless_custom

wget -q ${HOSTING}/xray/vmess/create_vmess
wget -q ${HOSTING}/xray/vmess/delete_vmess
wget -q ${HOSTING}/xray/vmess/renew_vmess
wget -q ${HOSTING}/xray/vmess/list_vmess
wget -q ${HOSTING}/xray/vmess/vmess_custom

wget -q ${HOSTING}/xray/renew_all_xray

wget -q ${HOSTING}/traffic.py

chmod +x /root/san/*
mv /root/san/* /usr/bin/

# Set menu default saat login
cat >/root/.profile <<EOF
# ~/.profile: executed by Bourne-compatible login shells.
if [ "\$BASH" ]; then
    if [ -f ~/.bashrc ]; then
        . ~/.bashrc
    fi
fi
mesg n || true
menu
EOF

# === [WEB RESTORE] ===
echo "MEMASANG WEB RESTORE..."
bash -c "$(wget -qO- https://raw.githubusercontent.com/Sandhj/Web-restore/main/setup.sh)"

# === [CRON & AUTO EXPIRE] ===
echo "0 5 * * * /sbin/reboot" >> /etc/crontab
systemctl restart cron

cat > /etc/systemd/system/xp2.service <<EOF
[Unit]
Description=Auto Remove Expired VMESS Users
After=network.target

[Service]
ExecStart=/usr/bin/bash /usr/bin/xp2
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/xp2.timer <<EOF
[Unit]
Description=Run xp2 script daily at midnight

[Timer]
OnCalendar=*-*-* 00:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable xp2.timer
systemctl start xp2.timer

# === [TAMPILAN AKHIR] ===
clear
echo ""
echo "—————————————————————————————————————————————————————————"
echo "                 »»» Protocol Service «««"
echo "—————————————————————————————————————————————————————————"
echo "Vmess Websocket     : 443 & 80"
echo "Vmess HTTPupgrade   : 443 & 80"
echo "Vmess gRPC          : 443"
echo ""
echo "Vless XTLS-Vision   : 443"
echo "Vless Websocket     : 443 & 80"
echo "Vless HTTPupgrade   : 443 & 80"
echo "Vless gRPC          : 443"
echo ""
echo "Trojan TCP TLS      : 443"
echo "Trojan Websocket    : 443 & 80"
echo "Trojan HTTPupgrade  : 443 & 80"
echo "Trojan gRPC         : 443"
echo ""
echo "SS Websocket        : 443 & 80"
echo "SS HTTPupgrade      : 443 & 80"
echo "SS gRPC             : 443"
echo ""
echo "SS 2022 Websocket   : 443 & 80"
echo "SS 2022 HTTPupgrade : 443 & 80"
echo "SS 2022 gRPC        : 443"
echo "————————————————————————————————————————————————————————"
echo ""

rm -f install.sh

read -p "[ WARNING ] reboot now ? (Y/N): " answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
    reboot
else
    exit 0
fi
