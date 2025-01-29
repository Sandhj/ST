config_file="/usr/local/etc/xray/config/04_inbounds.json"
vmess_count=$(awk '/###/ {count++} END {print count+0}' "$config_file" 2>/dev/null)
vless_count=$(awk '/##!/ {count++} END {print count+0}' "$config_file" 2>/dev/null)
trojan_count=$(awk '/#&!/ {count++} END {print count+0}' "$config_file" 2>/dev/null)
ss_count=$(awk '/##@/ {count++} END {print count+0}' "$config_file" 2>/dev/null)
vmess=$(( vmess_count / 3 ))
vless=$(( vless_count / 4 ))
trojan=$(( trojan_count / 6 ))
ss=$(( ss_count / 6 ))
total=$((vmess + vless + trojan + ss))
echo $total
