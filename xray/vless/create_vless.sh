#!/bin/bash

# Definisi Warna
NC='\e[0m'
DEFBOLD='\e[39;1m'
RB='\e[31;1m'
GB='\e[32;1m'
YB='\e[33;1m'
BB='\e[34;1m'
MB='\e[35;1m'
CB='\e[36;1m'
WB='\e[37;1m'

# Fungsi untuk menghasilkan UUID
generate_uuid() {
    cat /proc/sys/kernel/random/uuid
}

# Fungsi untuk menambahkan konfigurasi ke file Xray
add_xray_config() {
    local section=$1
    local content=$2
    sed -i "/#$section\$/a\\##! $user $exp\n$content" /usr/local/etc/xray/config/04_inbounds.json
}

# Inisialisasi Variabel
domain=$(cat /usr/local/etc/xray/dns/domain)
uuid=$(generate_uuid)

echo -e "${BB}———————————————————————————————————————${NC}"
echo -e "${BB}            Create New User ${NC}           "
echo -e "${BB}———————————————————————————————————————${NC}"
read -p "Username :" user
while true; do
    read -p "Expired :" masaaktif
    if [[ $masaaktif =~ ^0-9+$ ]]; then
        break
    else
        echo "Masukkan Angka Yang Valid"
    fi
done    

exp=$(date -d "$masaaktif days" +"%Y-%m-%d") 
ISP=$(cat /usr/local/etc/xray/org)
CITY=$(cat /usr/local/etc/xray/city)
REG=$(cat /usr/local/etc/xray/region)

# Menambahkan Konfigurasi ke File Xray
add_xray_config "xtls" "},{\"flow\": \"xtls-rprx-vision\",\"id\": \"$uuid\",\"email\": \"$user\""
add_xray_config "vless" "},{\"id\": \"$uuid\",\"email\": \"$user\""

# Membuat Tautan Vless
vlesslink1="vless://$uuid@$domain:443?path=/vless-ws&security=tls&encryption=none&host=$domain&type=ws&sni=$domain#vless-ws-tls"
vlesslink2="vless://$uuid@$domain:80?path=/vless-ws&security=none&encryption=none&host=$domain&type=ws#vless-ws-ntls"
vlesslink3="vless://$uuid@$domain:443?path=/vless-hup&security=tls&encryption=none&host=$domain&type=httpupgrade&sni=$domain#vless-hup-tls"
vlesslink4="vless://$uuid@$domain:80?path=/vless-hup&security=none&encryption=none&host=$domain&type=httpupgrade#vless-hup-ntls"
vlesslink5="vless://$uuid@$domain:443?security=tls&encryption=none&headerType=gun&type=grpc&serviceName=vless-grpc&sni=$domain#vless-grpc"
vlesslink6="vless://$uuid@$domain:443?security=tls&encryption=none&headerType=none&type=tcp&sni=$domain&flow=xtls-rprx-vision#vless-vision"

# Restart Xray Service
systemctl restart xray
clear
# Menampilkan Informasi ke Pengguna

TEXT="
—————————————————————————————————
           Vless Account
—————————————————————————————————
ISP         : $ISP
REGION      : $REG
CITY        : $CITY
PORT TLS    : 443
PORT HTTP   : 80
EXPIRED ON  : $exp
—————————————————————————————————
WS TLS      : $vlesslink1
WS nTLS     : $vlesslink2
HUP TLS     : $vlesslink3
HUP nTLS    : $vlesslink4
GRPC        : $vlesslink5
XTLS-VISION : $vlesslink6
"

echo "$TEXT"
read -n 1 -s -r -p "Press any key to go back to menu"
clear
menu
