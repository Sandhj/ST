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
    echo -e "          ${WB}[ Menu Vless ]${NC}               "
    echo -e "${BB}———————————————————————————————————————${NC}"
    echo -e " ${MB}[1]${NC} ${YB}Create Account${NC}"
    echo -e " ${MB}[2]${NC} ${YB}Renew Account${NC}"
    echo -e " ${MB}[3]${NC} ${YB}List Account${NC}"
    echo -e " ${MB}[4]${NC} ${YB}Delete Accoount${NC}"
    echo -e " ${GB}[4]${NC} ${GB}Main Menu${NC}"
    echo -e "${BB}———————————————————————————————————————${NC}"
    read -p " Select Menu :  " opt
    echo -e ""
    case $opt in
        1) clear ; create_vless ;;
        2) clear ; renew_vless ;;
        3) clear ; list_vless ;;
        4) clear ; delete_vless ;;
        0) clear ; menu ;;
        *) echo -e "${YB}Invalid input${NC}" ; sleep 1 ; vlessmenu ;;
    esac
