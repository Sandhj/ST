#!/bin/bash

# Warna untuk output (sesuaikan dengan kebutuhan)
NC='\e[0m'       # No Color (mengatur ulang warna teks ke default)
DEFBOLD='\e[39;1m' # Default Bold
RB='\e[31;1m'    # Red Bold
GB='\e[32;1m'    # Green Bold
YB='\e[33;1m'    # Yellow Bold
BB='\e[34;1m'    # Blue Bold
MB='\e[35;1m'    # Magenta Bold
CB='\e[36;1m'    # Cyan Bold
WB='\e[37;1m'    # White Bold

# Fungsi untuk menampilkan menu
    clear
    echo -e "${BB}———————————————————————————————————————${NC}"
    echo -e "          ${WB}[ Menu Vmess ]${NC}               "
    echo -e "${BB}———————————————————————————————————————${NC}"
    echo -e " ${MB}[1]${NC} ${YB}Routeing WARP${NC}"
    echo -e " ${MB}[2]${NC} ${YB}Traffic${NC}"
    echo -e " ${MB}[3]${NC} ${YB}Speedtest${NC}"
    echo -e " ${MB}[4]${NC} ${YB}Change Domain${NC}"
    echo -e " ${MB}[5]${NC} ${YB}Cert. Domain${NC}"
    echo -e " ${MB}[6]${NC} ${YB}About Script${NC}"
    echo -e " ${GB}[0]${NC} ${GB}Main Menu${NC}"
    echo -e "${BB}———————————————————————————————————————${NC}"
    read -p " Select Menu :  " opt
    echo -e ""
    case $opt in
        2) clear ; route-xray ;;
        3) clear ; python /usr/bin/traffic.py ; echo " " ; read -n 1 -s -r -p "Press any key to back on menu" ; menu ;;
        6) clear ; speedtest ; echo " " ; read -n 1 -s -r -p "Press any key to back on menu" ; menu ;;
        7) clear ; dns ;;
        8) clear ; certxray ;;
        9) clear ; about ;;
        0) clear ; menu ;;
        *) echo -e "${YB}Invalid input${NC}" ; sleep 1 ; settingmenu ;;
    esac