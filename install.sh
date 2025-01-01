#!/bin/bash
clear
# Warna untuk output (sesuaikan dengan kebutuhan)
NC='\e[0m'       # No Color
RB='\e[31;1m'    # Red Bold
GB='\e[32;1m'    # Green Bold
YB='\e[33;1m'    # Yellow Bold
BB='\e[34;1m'    # Blue Bold
MB='\e[35;1m'    # Magenta Bold
CB='\e[36;1m'    # Cyan Bold
WB='\e[37;1m'    # White Bold

# Fungsi untuk mencetak pesan dengan warna
print_msg() {
    COLOR=$1
    MSG=$2
    echo -e "${COLOR}${MSG}${NC}"
}

# Memastikan pengguna adalah root
if [ "$EUID" -ne 0 ]; then
  print_error "Harap jalankan skrip ini sebagai root."
  exit 1
fi

HOSTING="https://raw.githubusercontent.com/Sandhj/ST/main"
#======================================== START SCRIPT =============================================
# Fungsi untuk memvalidasi domain
validate_domain() {
    local domain=$1
    if [[ $domain =~ ^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
        return 0
    else
        return 1
    fi
}

#SETUP DOMAIN
clear
echo -e "${BB}————————————————————————————————————————————————————————"
echo -e "${YB}                      SETUP DOMAIN"
echo -e "${BB}————————————————————————————————————————————————————————"
    while true; do
        read -rp $'\e[33;1mInput domain kamu: \e[0m' -e dns

        if [ -z "$dns" ]; then
            echo -e "${RB}Tidak ada input untuk domain!${NC}"
        elif ! validate_domain "$dns"; then
            echo -e "${RB}Format tidak valid!${NC}"
        else
            echo "$dns" > /usr/local/etc/xray/dns/domain
            echo "DNS=$dns" > /var/lib/dnsvps.conf
            echo -e "Domain ${GB}${dns}${NC} berhasil disimpan"
            break
        fi
    done

# Update package list
print_msg $YB "PERBAHARUI PAKET. . ."
apt update -y
sleep 1

# Install paket pertama
print_msg $YB "MEMASANG PAKET YANG DI BUTUHKAN. . ."
apt install socat netfilter-persistent bsdmainutils -y
apt install vnstat lsof fail2ban -y
apt install jq curl sudo cron -y
apt install build-essential libpcre3 libpcre3-dev zlib1g zlib1g-dev openssl libssl-dev gcc clang llvm g++ valgrind make cmake debian-keyring debian-archive-keyring apt-transport-https systemd bind9-host gnupg2 ca-certificates lsb-release ubuntu-keyring debian-archive-keyring -y
apt install unzip python-is-python3 python3-pip -y
pip install psutil pandas tabulate rich py-cpuinfo distro requests pycountry geoip2 --break-system-packages
sleep 1

# Menghapus file konfigurasi lama jika ada
print_msg $YB "MENGHAPUS DIREKTORI LAMA. . ."
sudo rm -f /usr/local/etc/xray/city /usr/local/etc/xray/org /usr/local/etc/xray/timezone /usr/local/etc/xray/region

# Membuat direktori yang diperlukan
print_msg $YB "MEMBUAT DIREKTORI BARU. . ."
sudo mkdir -p /user /tmp /usr/local/etc/xray /var/log/xray

# Fungsi untuk memeriksa versi terbaru Xray-core
LATEST_VERSION=$(curl -s https://api.github.com/repos/XTLS/Xray-core/releases/latest | jq -r '.tag_name')
if [ -z "$LATEST_VERSION" ]; then
   print_msg $RB "Tidak dapat menemukan versi terbaru Xray-core."
   exit 1
fi


# Fungsi untuk memasang Xray-core
    ARCH=$(uname -m)
    case $ARCH in
        x86_64)
            ARCH="64"
            ;;
        aarch64)
            ARCH="arm64-v8a"
            ;;
        *)
            print_msg $RB "Arsitektur $ARCH tidak didukung."
            exit 1
            ;;
    esac

    DOWNLOAD_URL="https://github.com/XTLS/Xray-core/releases/download/$LATEST_VERSION/Xray-linux-$ARCH.zip"

    # Unduh dan ekstrak Xray-core
    print_msg $YB "MEMASANG XRAY CORE. . ."
    curl -L -o xray.zip $DOWNLOAD_URL

    sudo unzip -o xray.zip -d /usr/local/bin
    rm xray.zip

    sudo chmod +x /usr/local/bin/xray

    # Membuat layanan systemd
    sudo bash -c 'cat <<EOF > /etc/systemd/system/xray.service
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
EOF'

sudo systemctl daemon-reload
sudo systemctl enable xray
sudo systemctl start xray

    
sudo apt update
sudo apt install -y curl unzip

# Mengumpulkan informasi dari ipinfo.io
curl -s ipinfo.io/city?token=f209571547ff6b | sudo tee /usr/local/etc/xray/city
curl -s ipinfo.io/org?token=f209571547ff6b | cut -d " " -f 2-10 | sudo tee /usr/local/etc/xray/org
curl -s ipinfo.io/timezone?token=f209571547ff6b | sudo tee /usr/local/etc/xray/timezone
curl -s ipinfo.io/region?token=f209571547ff6b | sudo tee /usr/local/etc/xray/region
clear

# Mengunduh dan menginstal Speedtest CLI
curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | sudo bash &>/dev/null
sudo apt-get install -y speedtest &>/dev/null

# Mengatur zona waktu ke Asia/Jakarta
sudo timedatectl set-timezone Asia/Jakarta &>/dev/null

#Install Wireproxy
print_msg $YB "INSTALL WIREPROXY. . ."
rm -rf /usr/local/bin/wireproxy >> /dev/null 2>&1
wget -q -O /usr/local/bin/wireproxy ${HOSTING}/wireproxy
chmod +x /usr/local/bin/wireproxy

#Buat config wireproxy
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

#Membuat Service untuk Wireproxy
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
sudo systemctl enable wireproxy
sudo systemctl start wireproxy
sudo systemctl daemon-reload
sudo systemctl restart wireproxy
clear

# Fungsi untuk mendeteksi OS dan distribusi
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VERSION=$VERSION_ID
    else
        print_msg $RB "Tidak dapat mendeteksi OS. Skrip ini hanya mendukung distribusi berbasis Debian dan Red Hat."
        exit 1
    fi


# Fungsi untuk menambahkan repositori Nginx
  if [ "$OS" == "ubuntu" ]; then
    sudo apt install curl gnupg2 ca-certificates lsb-release ubuntu-keyring -y
    echo "deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] http://nginx.org/packages/mainline/ubuntu `lsb_release -cs` nginx" | sudo tee /etc/apt/sources.list.d/nginx.list
    curl -fsSL https://nginx.org/keys/nginx_signing.key | gpg --dearmor | sudo tee /usr/share/keyrings/nginx-archive-keyring.gpg >/dev/null
  elif [ "$OS" == "debian" ]; then
    sudo apt install curl gnupg2 ca-certificates lsb-release debian-archive-keyring -y
    echo "deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] http://nginx.org/packages/mainline/debian `lsb_release -cs` nginx" | sudo tee /etc/apt/sources.list.d/nginx.list
    curl -fsSL https://nginx.org/keys/nginx_signing.key | gpg --dearmor | sudo tee /usr/share/keyrings/nginx-archive-keyring.gpg >/dev/null
  else
    print_error "OS tidak didukung. Hanya mendukung Ubuntu dan Debian."
    exit 1
  fi

# Fungsi untuk menginstal Nginx
  sudo apt update
  sudo apt install nginx -y
  sudo systemctl start nginx
  sudo systemctl enable nginx

# Menghapus konfigurasi default Nginx dan konten default web
rm -rf /etc/nginx/conf.d/default.conf >> /dev/null 2>&1
rm -rf /etc/nginx/sites-enabled/default >> /dev/null 2>&1
rm -rf /etc/nginx/sites-available/default >> /dev/null 2>&1
rm -rf /var/www/html/* >> /dev/null 2>&1
sudo systemctl restart nginx

# Pesan selesai
systemctl restart nginx
systemctl stop nginx
systemctl stop xray
mkdir -p /usr/local/etc/xray/config >> /dev/null 2>&1
mkdir -p /usr/local/etc/xray/dns >> /dev/null 2>&1
touch /usr/local/etc/xray/dns/domain

#================================== BAGIAN PENGATURAN DOMAIN ===========================
install_acme_sh2() {
    domain=$(cat /usr/local/etc/xray/dns/domain)
    rm -rf ~/.acme.sh/*_ecc >> /dev/null 2>&1
    curl https://get.acme.sh | sh
    source ~/.bashrc
    ~/.acme.sh/acme.sh --register-account -m $(echo $RANDOM | md5sum | head -c 6; echo;)@gmail.com --server letsencrypt
    ~/.acme.sh/acme.sh --issue -d $domain --standalone --listen-v6 --server letsencrypt --keylength ec-256 --fullchain-file /usr/local/etc/xray/fullchain.cer --key-file /usr/local/etc/xray/private.key --reloadcmd "systemctl restart nginx" --force
    chmod 745 /usr/local/etc/xray/private.key
    echo -e "${YB}Sertifikat SSL berhasil dipasang!${NC}"
}

install_acme_sh2

#========================================= END SCRIPT DOMAIN ===============================
# Menghasilkan UUID
uuid=$(cat /proc/sys/kernel/random/uuid)

# Menghasilkan password random
pwtr=$(openssl rand -hex 4)
pwss=$(echo $RANDOM | md5sum | head -c 6; echo;)

# Menghasilkan PSK (Pre-Shared Key) untuk pengguna dan server
userpsk=$(openssl rand -base64 32)
serverpsk=$(openssl rand -base64 32)
echo "$serverpsk" > /usr/local/etc/xray/serverpsk

# Konfigurasi Xray-core
print_msg $YB "KONFIGURASI FILE JSON XRAY. . ."
wget -q -O /usr/local/etc/xray/config/00_log.json "${HOSTING}/config/00_log.json"
wget -q -O /usr/local/etc/xray/config/01_api.json "${HOSTING}/config/01_api.json"
wget -q -O /usr/local/etc/xray/config/02_dns.json "${HOSTING}/config/02_dns.json"
wget -q -O /usr/local/etc/xray/config/03_policy.json "${HOSTING}/config/03_policy.json"
wget -q -O /usr/local/etc/xray/config/04_inbounds.json "${HOSTING}/config/04_inbounds.json"
wget -q -O /usr/local/etc/xray/config/05_outbonds.json "${HOSTING}/config/05_outbonds.json"
wget -q -O /usr/local/etc/xray/config/06_routing.json "${HOSTING}/config/06_routing.json"
wget -q -O /usr/local/etc/xray/config/07_stats.json "${HOSTING}/config/07_stats.json"
sleep 1.5

# Membuat file log Xray yang diperlukan
sudo touch /var/log/xray/access.log /var/log/xray/error.log
sudo chown nobody:nogroup /var/log/xray/access.log /var/log/xray/error.log
sudo chmod 664 /var/log/xray/access.log /var/log/xray/error.log
sleep 1.5

# Konfigurasi Nginx
wget -q -O /var/www/html/index.html ${HOSTING}/index.html
wget -q -O /etc/nginx/nginx.conf ${HOSTING}/nginx.conf

domain=$(cat /usr/local/etc/xray/dns/domain)
sed -i "s/server_name web.com;/server_name $domain;/g" /etc/nginx/nginx.conf
sed -i "s/server_name \*.web.com;/server_name \*.$domain;/" /etc/nginx/nginx.conf

print_msg $GB "SETUP SCRIPT UTAMA SELESAI. . ."
sleep 3

systemctl restart nginx
systemctl restart xray
clear

# Blokir lalu lintas torrent (BitTorrent)
sudo iptables -A INPUT -p udp --dport 6881:6889 -j DROP
sudo iptables -A INPUT -p tcp --dport 6881:6889 -j DROP
# Blokir lalu lintas torrent dengan modul string
sudo iptables -A INPUT -p tcp --dport 6881:6889 -m string --algo bm --string "BitTorrent" -j DROP
sudo iptables -A INPUT -p udp --dport 6881:6889 -m string --algo bm --string "BitTorrent" -j DROP


cd
mkdir -p /root/san
cd /root/san
wget -q ${HOSTING}/menu/menu.sh
wget -q ${HOSTING}/menu/settingmenu.sh
wget -q ${HOSTING}/menu/sodosokmenu.sh
wget -q ${HOSTING}/menu/trojanmenu.sh
wget -q ${HOSTING}/menu/vlessmenu.sh
wget -q ${HOSTING}/menu/vmessmenu.sh

wget -q ${HOSTING}/other/about.sh
wget -q ${HOSTING}/other/cek-xray.sh
wget -q ${HOSTING}/other/certxray.sh
wget -q ${HOSTING}/other/clear-log.sh
wget -q ${HOSTING}/other/dns.sh
wget -q ${HOSTING}/other/log-xray.sh
wget -q ${HOSTING}/other/route-xray.sh
wget -q ${HOSTING}/other/update-xray.sh
wget -q ${HOSTING}/other/xp.sh

wget -q ${HOSTING}/xray/ss/create_ss.sh
wget -q ${HOSTING}/xray/ss/delete_ss.sh
wget -q ${HOSTING}/xray/ss/renew_ss.sh

wget -q ${HOSTING}/xray/trojan/create_trojan.sh
wget -q ${HOSTING}/xray/trojan/delete_trojan.sh
wget -q ${HOSTING}/xray/trojan/renew_trojan.sh

wget -q ${HOSTING}/xray/vless/create_vless.sh
wget -q ${HOSTING}/xray/vless/delete_vless.sh
wget -q ${HOSTING}/xray/vless/renew_vless.sh

wget -q ${HOSTING}/xray/vmess/create_vmess.sh
wget -q ${HOSTING}/xray/vmess/delete_vmess.sh
wget -q ${HOSTING}/xray/vmess/renew_vmess.sh

wget -q ${HOSTING}/traffic.py

#Berikan Izin Eksekusi dan memindahkan ke /usr/bin
cd
chmod +x /root/san/*
mv /root/san/* /usr/bin/
rm -r /root/san

cd
echo "0 0 * * * root xp" >> /etc/crontab
echo "*/3 * * * * root clear-log" >> /etc/crontab
systemctl restart cron
clear

print_msg $YB "INSTALASI SUKSES. . ."

rm -f install.sh

echo -e "${YB}[ WARNING ] reboot now ? (Y/N)${NC} "
read answer
if [ "$answer" == "${answer#[Yy]}" ] ;then
exit 0
else
reboot
fi
