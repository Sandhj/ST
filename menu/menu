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
    echo -e "${BB}————————————————————————————————————————————————————————${NC}"
    echo -e "                   ${WB}----- [ Menu ] -----${NC}               "
    echo -e "${BB}————————————————————————————————————————————————————————${NC}"
    echo -e " ${MB}[1]${NC} ${YB}Vmess Menu${NC}"
    echo -e " ${MB}[2]${NC} ${YB}Vless Menu${NC}"
    echo -e " ${MB}[3]${NC} ${YB}Trojan Menu${NC}"
    echo -e " ${MB}[4]${NC} ${YB}Shodosok Menu${NC}"
    echo -e " ${MB}[5]${NC} ${YB}Menu Lain${NC}"
    echo -e "${BB}————————————————————————————————————————————————————————${NC}"
    read -p " Select Menu :  " opt
    echo -e ""
    case $opt in
        1) clear ; vmessmenu ;;
        2) clear ; vlessmenu ;;
        3) clear ; trojanmenu ;;
        4) clear ; sodosokmenu ;;
        5) clear ; settingmenu ;;
        *) echo -e "${YB}Invalid input${NC}" ; sleep 1 ; menu ;;
    esac
