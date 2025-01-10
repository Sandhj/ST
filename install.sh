#!/bin/bash

clear
# Warna untuk output (sesuaikan dengan kebutuhan)
NC='\e[0m'       # No Color (mengatur ulang warna teks ke default)
RB='\e[31;1m'    # Red Bold
GB='\e[32;1m'    # Green Bold
YB='\e[33;1m'    # Yellow Bold
BB='\e[34;1m'    # Blue Bold
MB='\e[35;1m'    # Magenta Bold
CB='\e[36;1m'    # Cyan Bold
WB='\e[37;1m'    # White Bold

HOSTING="https://raw.githubusercontent.com/Sandhj/ST/main"

# Fungsi untuk mencetak pesan dengan warna
print_msg() {
    COLOR=$1
    MSG=$2
    echo -e "${COLOR}${MSG}${NC}"
}

# Fungsi untuk memeriksa keberhasilan perintah
check_success() {
    if [ $? -eq 0 ]; then
        print_msg $GB "Berhasil"
    else
        print_msg $RB "Gagal: $1"
        exit 1
    fi
}

# Fungsi untuk menampilkan pesan kesalahan
print_error() {
    MSG=$1
    print_msg $RB "Error: ${MSG}"
}

# Memastikan pengguna adalah root
if [ "$EUID" -ne 0 ]; then
  print_error "Harap jalankan skrip ini sebagai root."
  exit 1
fi

verif_ip() {
    # Ambil informasi IP dan tanggal dari URL
    url="https://raw.githubusercontent.com/Sandhj/registrasi-ip/main/IP"
    ip_date=$(curl -s $url)

    # Ambil IP dan Tanggal dari data yang diambil
    ip=$(echo $ip_date | awk '{print $1}')
    date=$(echo $ip_date | awk '{print $2}')

    # Ambil IP dan Tanggal hari ini
    current_ip=$(curl -s https://ipinfo.io/ip)
    current_date=$(date +%Y-%m-%d)
    

    # Hitung tanggal satu hari setelah tanggal hari ini
    expiry_date=$(date -d "$current_date + 1 day" +%Y-%m-%d)

    # Periksa apakah IP cocok dan apakah tanggal tidak kadaluarsa
    if [[ "$current_ip" == "$ip" && ( "$date" == "$current_date" || "$date" == "$expiry_date" ) ]]; then
        echo "————————————————————————————————————"
        echo "           ${GB}Success Massage !! ${NC} "
        echo "————————————————————————————————————"
        echo "    ${GB}   IP ANDA TERVERIFIKASI ✓  ${NC}   "
        echo "————————————————————————————————————"
    else
        echo "————————————————————————————————————"
        echo "           ${RB}Eror Massage !! ${NC} "
        echo "————————————————————————————————————"
        echo "${GB}     Anda Belum Terdaftar Untuk"
        echo "   Menggunakan Script ini Silahkan "
        echo "            Registrasi ke ${NC}          "
        echo "  Tele : Sanmaxx | Wa : 085155208019"
        echo "————————————————————————————————————"
        exit 1
    fi
}


# Script untuk Verifikasi Pengguna
while true; do
    echo "Pilih tipe pengguna:"
    echo "1. Owner SC"
    echo "2. Pengguna"
    read -p "Masukkan pilihan Anda (1/2): " pilihan

    if [ "$pilihan" == "1" ]; then
        read -sp "Masukkan Password Owner: " password
        echo
        if [ "$password" == "@sandi" ]; then
            echo -e "${GB}Selamat Datang Tuan${NC}"
            sleep 2
            break
        else
            echo -e "Password Salah, Jika Kamu Pengguna Silahkan Memilih Opsi No.2"
        fi
    elif [ "$pilihan" == "2" ]; then
        verif_ip
        break
    else
        echo -e "Pilihan tidak valid. Silakan coba lagi."
    fi
done
clear
# ============= BATAS AWAL SCRIPT UTAMA ============
mkdir -p /usr/local/etc/xray/config >> /dev/null 2>&1
mkdir -p /usr/local/etc/xray/dns >> /dev/null 2>&1
touch /usr/local/etc/xray/dns/domain
# Fungsi untuk memvalidasi domain
validate_domain() {
    local domain=$1
    if [[ $domain =~ ^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
        return 0
    else
        return 1
    fi
}

# Fungsi untuk meminta input domain
input_domain() {
    while true; do
        read -rp $'\e[33;1mInput domain kamu: \e[0m' -e dns

        if [ -z "$dns" ]; then
            echo -e "${RB}Tidak ada input untuk domain!${NC}"
        elif ! validate_domain "$dns"; then
            echo -e "${RB}Format domain tidak valid! Silakan input domain yang valid.${NC}"
        else
            echo "$dns" > /usr/local/etc/xray/dns/domain
            echo "DNS=$dns" > /var/lib/dnsvps.conf
            break
        fi
    done
}



#Fungsi Input Domain
echo -e "${BB}————————————————————————————————————————————————————————"
echo -e "${YB}                      SETUP DOMAIN"
echo -e "${BB}————————————————————————————————————————————————————————"

input_domain


# Update package list
print_msg $YB "Setup Domain Done"
print_msg $YB "Install Paket Yang Dibutuhkan"
sleep 2
apt update -y
apt install socat netfilter-persistent bsdmainutils -y
apt install vnstat lsof fail2ban -y
apt install jq curl sudo cron -y
apt install build-essential libpcre3 libpcre3-dev zlib1g zlib1g-dev openssl libssl-dev gcc clang llvm g++ valgrind make cmake debian-keyring debian-archive-keyring apt-transport-https systemd bind9-host gnupg2 ca-certificates lsb-release ubuntu-keyring debian-archive-keyring -y
apt install unzip python-is-python3 python3-pip -y
pip install psutil pandas tabulate rich py-cpuinfo distro requests pycountry geoip2 --break-system-packages


# Membuat direktori yang diperlukan
print_msg $YB "Membuat direktori yang diperlukan..."
sudo mkdir -p /user /tmp /usr/local/etc/xray /var/log/xray
check_success "Gagal membuat direktori."

# Menghapus file konfigurasi lama jika ada
print_msg $YB "Menghapus file konfigurasi lama..."
sudo rm -f /usr/local/etc/xray/city /usr/local/etc/xray/org /usr/local/etc/xray/timezone /usr/local/etc/xray/region
check_success "Gagal menghapus file konfigurasi lama."

# Fungsi untuk mendeteksi OS dan distribusi
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VERSION=$VERSION_ID
    else
        print_msg $RB "Tidak dapat mendeteksi OS. Skrip ini hanya mendukung distribusi berbasis Debian dan Red Hat."
        exit 1
    fi
}

# Fungsi untuk memeriksa versi terbaru Xray-core
get_latest_xray_version() {
    LATEST_VERSION=$(curl -s https://api.github.com/repos/XTLS/Xray-core/releases/latest | jq -r '.tag_name')
    if [ -z "$LATEST_VERSION" ]; then
        print_msg $RB "Tidak dapat menemukan versi terbaru Xray-core."
        exit 1
    fi
}

# Fungsi untuk memasang Xray-core
install_xray_core() {
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
    print_msg $YB "Mengunduh dan memasang Xray-core..."
    curl -L -o xray.zip $DOWNLOAD_URL
    check_success "Gagal mengunduh Xray-core."

    sudo unzip -o xray.zip -d /usr/local/bin
    check_success "Gagal mengekstrak Xray-core."
    rm xray.zip

    sudo chmod +x /usr/local/bin/xray
    check_success "Gagal mengatur izin eksekusi untuk Xray-core."

    # Membuat layanan systemd
    print_msg $YB "Mengkonfigurasi layanan systemd untuk Xray-core..."
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
    check_success "Gagal mengkonfigurasi layanan systemd untuk Xray-core."

    sudo systemctl daemon-reload
    sudo systemctl enable xray
    sudo systemctl start xray
    check_success "Gagal memulai layanan Xray-core."
}

# Deteksi OS
print_msg $YB "Mendeteksi sistem operasi..."
detect_os

# Cek apakah OS didukung
if [[ "$OS" == "Ubuntu" || "$OS" == "Debian" || "$OS" == "Debian GNU/Linux" || "$OS" == "CentOS" || "$OS" == "Fedora" || "$OS" == "Red Hat Enterprise Linux" ]]; then
    print_msg $GB "Mendeteksi OS: $OS $VERSION"
else
    print_msg $RB "Distribusi $OS tidak didukung oleh skrip ini. Proses instalasi dibatalkan."
    exit 1
fi

# Memeriksa versi terbaru Xray-core
print_msg $YB "Memeriksa versi terbaru Xray-core..."
get_latest_xray_version
print_msg $GB "Versi terbaru Xray-core: $LATEST_VERSION"

# Memasang dependensi yang diperlukan
print_msg $YB "Memasang dependensi yang diperlukan..."
if [[ "$OS" == "Ubuntu" || "$OS" == "Debian" ]]; then
    sudo apt update
    sudo apt install -y curl unzip
elif [[ "$OS" == "CentOS" || "$OS" == "Fedora" || "$OS" == "Red Hat Enterprise Linux" ]]; then
    sudo yum install -y curl unzip
fi
check_success "Gagal memasang dependensi yang diperlukan."

# Memasang Xray-core
install_xray_core

print_msg $GB "Pemasangan Xray-core versi $LATEST_VERSION selesai."

# Mengumpulkan informasi dari ipinfo.io
print_msg $YB "Mengumpulkan informasi lokasi dari ipinfo.io..."
curl -s ipinfo.io/city?token=f209571547ff6b | sudo tee /usr/local/etc/xray/city
curl -s ipinfo.io/org?token=f209571547ff6b | cut -d " " -f 2-10 | sudo tee /usr/local/etc/xray/org
curl -s ipinfo.io/timezone?token=f209571547ff6b | sudo tee /usr/local/etc/xray/timezone
curl -s ipinfo.io/region?token=f209571547ff6b | sudo tee /usr/local/etc/xray/region
check_success "Gagal mengumpulkan informasi lokasi."

# Mengunduh dan menginstal Speedtest CLI
print_msg $YB "Mengunduh dan menginstal Speedtest CLI..."
curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | sudo bash &>/dev/null
sudo apt-get install -y speedtest &>/dev/null
print_msg $YB "Speedtest CLI berhasil diinstal."

# Mengatur zona waktu ke Asia/Jakarta
print_msg $YB "Mengatur zona waktu ke Asia/Jakarta..."
sudo timedatectl set-timezone Asia/Jakarta &>/dev/null
print_msg $YB "Zona waktu berhasil diatur."

print_msg $YB "Instalasi WireProxy"
rm -rf /usr/local/bin/wireproxy >> /dev/null 2>&1
wget -O /usr/local/bin/wireproxy ${HOSTING}/wireproxy
chmod +x /usr/local/bin/wireproxy
check_success "Gagal instalasi WireProxy."
print_msg $YB "Mengkonfigurasi WireProxy"
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
check_success "Gagal mengkonfigurasi WireProxy."

print_msg $YB "Membuat service untuk WireProxy"
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
check_success "Gagal membuat service untuk WireProxy."
sudo systemctl daemon-reload
sudo systemctl enable wireproxy
sudo systemctl start wireproxy
sudo systemctl restart wireproxy
print_msg $YB "Instalasi selesai."
sleep 3
clear

# Fungsi untuk mendeteksi OS
detect_os() {
  if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VERSION=$VERSION_ID
  else
    print_error "OS tidak didukung. Hanya mendukung Ubuntu dan Debian."
    exit 1
  fi
}

# Fungsi untuk menambahkan repositori Nginx
add_nginx_repo() {
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
}

# Fungsi untuk menginstal Nginx
install_nginx() {
  sudo apt update
  sudo apt install nginx -y
  sudo systemctl start nginx
  sudo systemctl enable nginx
}

# Fungsi utama
detect_os
add_nginx_repo
install_nginx


# Menghapus konfigurasi default Nginx dan konten default web
print_msg $YB "Menghapus konfigurasi default Nginx dan konten default web..."
rm -rf /etc/nginx/conf.d/default.conf >> /dev/null 2>&1
rm -rf /etc/nginx/sites-enabled/default >> /dev/null 2>&1
rm -rf /etc/nginx/sites-available/default >> /dev/null 2>&1
rm -rf /var/www/html/* >> /dev/null 2>&1
sudo systemctl restart nginx
check_success "Gagal menghapus konfigurasi default Nginx dan konten default web."

# Membuat direktori untuk Xray
print_msg $YB "Membuat direktori untuk Xray di /var/www/html..."
mkdir -p /var/www/html/xray >> /dev/null 2>&1
check_success "Gagal membuat direktori untuk Xray."

# Pesan selesai
print_msg $GB "Pemasangan dan konfigurasi Nginx telah selesai."
sleep 3
clear
systemctl restart nginx
systemctl stop nginx
systemctl stop xray

#Cert Domain
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

echo -e "${GB}[ INFO ]${NC} ${YB}Setup Nginx & Xray Config${NC}"
# Generate variabel
uuid=$(cat /proc/sys/kernel/random/uuid)
pwtr=$(openssl rand -hex 4)
pwss=$(echo $RANDOM | md5sum | head -c 6; echo;)
userpsk=$(openssl rand -base64 32)
serverpsk=$(openssl rand -base64 32)

# Escape karakter khusus dalam variabel
escaped_uuid=$(printf '%s\n' "$uuid" | sed 's/[\/&]/\\&/g')
escaped_pwtr=$(printf '%s\n' "$pwtr" | sed 's/[\/&]/\\&/g')
escaped_pwss=$(printf '%s\n' "$pwss" | sed 's/[\/&]/\\&/g')
escaped_userpsk=$(printf '%s\n' "$userpsk" | sed 's/[\/&]/\\&/g')
escaped_serverpsk=$(printf '%s\n' "$serverpsk" | sed 's/[\/&]/\\&/g')

# Konfigurasi Xray-core
print_msg $YB "Mengonfigurasi Xray-core..."
wget -q -O /usr/local/etc/xray/config/00_log.json "${HOSTING}/config/00_log.json"
wget -q -O /usr/local/etc/xray/config/01_api.json "${HOSTING}/config/01_api.json"
wget -q -O /usr/local/etc/xray/config/02_dns.json "${HOSTING}/config/02_dns.json"
wget -q -O /usr/local/etc/xray/config/03_policy.json "${HOSTING}/config/03_policy.json"
wget -q -O /usr/local/etc/xray/config/04_inbounds.json "${HOSTING}/config/04_inbounds.json"
wget -q -O /usr/local/etc/xray/config/05_outbonds.json "${HOSTING}/config/05_outbonds.json"
wget -q -O /usr/local/etc/xray/config/06_routing.json "${HOSTING}/config/06_routing.json"
wget -q -O /usr/local/etc/xray/config/07_stats.json "${HOSTING}/config/07_stats.json"

# Ganti placeholder di dalam 04_inbounds JSON 
sed -i \
    -e "s/UUID/$escaped_uuid/g" \
    -e "s/PWTR/$escaped_pwtr/g" \
    -e "s/PWSS/$escaped_pwss/g" \
    -e "s/USERPSK/$escaped_userpsk/g" \
    -e "s/SERVERPSK/$escaped_serverpsk/g" \
    /usr/local/etc/xray/config/04_inbounds.json
sleep 1.5

# Membuat file log Xray yang diperlukan
print_msg $YB "Membuat file log Xray yang diperlukan..."
sudo touch /var/log/xray/access.log /var/log/xray/error.log
sudo chown nobody:nogroup /var/log/xray/access.log /var/log/xray/error.log
sudo chmod 664 /var/log/xray/access.log /var/log/xray/error.log
check_success "Gagal membuat file log Xray yang diperlukan."
sleep 1.5

# Konfigurasi Nginx
print_msg $YB "Mengonfigurasi Nginx..."
wget -q -O /var/www/html/index.html ${HOSTING}/index.html
wget -q -O /etc/nginx/nginx.conf ${HOSTING}/nginx.conf
domain=$(cat /usr/local/etc/xray/dns/domain)
sed -i "s/server_name web.com;/server_name $domain;/g" /etc/nginx/nginx.conf
sed -i "s/server_name \*.web.com;/server_name \*.$domain;/" /etc/nginx/nginx.conf
# Jika sampai di sini tidak ada error, maka konfigurasi berhasil
print_msg $GB "Konfigurasi Xray-core dan Nginx berhasil."
sleep 3
systemctl restart nginx
systemctl restart xray
echo -e "${GB}[ INFO ]${NC} ${YB}Setup Done${NC}"
sleep 3
clear

# Blokir lalu lintas torrent (BitTorrent)
sudo iptables -A INPUT -p udp --dport 6881:6889 -j DROP
sudo iptables -A INPUT -p tcp --dport 6881:6889 -j DROP
# Blokir lalu lintas torrent dengan modul string
sudo iptables -A INPUT -p tcp --dport 6881:6889 -m string --algo bm --string "BitTorrent" -j DROP
sudo iptables -A INPUT -p udp --dport 6881:6889 -m string --algo bm --string "BitTorrent" -j DROP

print_msg $YB "MEMASANG MENU. . ."
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

wget -q ${HOSTING}/traffic.py

#Berikan Izin Eksekusi dan memindahkan ke /usr/bin
cd
chmod +x /root/san/*
mv /root/san/* /usr/bin/

menu_default() {
    cat >/root/.profile <<EOF
# ~/.profile: executed by Bourne-compatible login shells.
if [ "$BASH" ]; then
    if [ -f ~/.bashrc ]; then
        . ~/.bashrc
    fi
fi
mesg n || true
menu
EOF
}

#Pasang Default Menu Ketika Login VPS
menu_default

#Pasang Web Restore
print_msg $YB "MEMASANG WEB RESTORE. . ."
bash -c "$(wget -qO- https://raw.githubusercontent.com/Sandhj/Web-restore/main/setup.sh)"

cd
echo "0 5 * * * /sbin/reboot" >> /etc/crontab
echo "0 0 * * * root xp2" >> /etc/crontab
echo "*/3 * * * * root clear-log" >> /etc/crontab
systemctl restart cron
clear
echo ""
echo -e "${BB}—————————————————————————————————————————————————————————${NC}"
echo -e "                 ${WB}»»» Protocol Service «««${NC}  "
echo -e "${BB}—————————————————————————————————————————————————————————${NC}"
echo -e "${YB}Vmess Websocket${NC}     : ${YB}443 & 80${NC}"
echo -e "${YB}Vmess HTTPupgrade${NC}   : ${YB}443 & 80${NC}"
echo -e "${YB}Vmess gRPC${NC}          : ${YB}443${NC}"
echo ""
echo -e "${YB}Vless XTLS-Vision${NC}   : ${YB}443${NC}"
echo -e "${YB}Vless Websocket${NC}     : ${YB}443 & 80${NC}"
echo -e "${YB}Vless HTTPupgrade${NC}   : ${YB}443 & 80${NC}"
echo -e "${YB}Vless gRPC${NC}          : ${YB}443${NC}"
echo ""
echo -e "${YB}Trojan TCP TLS${NC}      : ${YB}443${NC}"
echo -e "${YB}Trojan Websocket${NC}    : ${YB}443 & 80${NC}"
echo -e "${YB}Trojan HTTPupgrade${NC}  : ${YB}443 & 80${NC}"
echo -e "${YB}Trojan gRPC${NC}         : ${YB}443${NC}"
echo ""
echo -e "${YB}SS Websocket${NC}        : ${YB}443 & 80${NC}"
echo -e "${YB}SS HTTPupgrade${NC}      : ${YB}443 & 80${NC}"
echo -e "${YB}SS gRPC${NC}             : ${YB}443${NC}"
echo ""
echo -e "${YB}SS 2022 Websocket${NC}   : ${YB}443 & 80${NC}"
echo -e "${YB}SS 2022 HTTPupgrade${NC} : ${YB}443 & 80${NC}"
echo -e "${YB}SS 2022 gRPC${NC}        : ${YB}443${NC}"
echo -e "${BB}————————————————————————————————————————————————————————${NC}"
echo ""
rm -f install.sh
echo -e "${YB}[ WARNING ] reboot now ? (Y/N)${NC} "
read answer
if [ "$answer" == "${answer#[Yy]}" ] ;then
exit 0
else
reboot
fi
