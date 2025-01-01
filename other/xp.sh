clear
# VMESS
data=($(cat /usr/local/etc/xray/04_inbounds.json | grep '^###' | cut -d ' ' -f 2 | sort | uniq))
now=$(date +"%Y-%m-%d")
for user in "${data[@]}"; do
exp=$(grep -w "^### $user" "/usr/local/etc/xray/04_inbounds.json" | cut -d ' ' -f 3 | sort | uniq)
d1=$(date -d "$exp" +%s)
d2=$(date -d "$now" +%s)
exp2=$(((d1 - d2) / 86400))
if [[ "$exp2" -le "0" ]]; then
sed -i "/^### $user $exp/,/^},{/d" /usr/local/etc/xray/04_inbounds.json
sed -i "/^### $user $exp/,/^},{/d" /usr/local/etc/xray/04_inbounds.json
systemctl restart xray
fi
done

# VLESS
data=($(cat /usr/local/etc/xray/04_inbounds.json | grep '^##!' | cut -d ' ' -f 2 | sort | uniq))
now=$(date +"%Y-%m-%d")
for user in "${data[@]}"; do
exp=$(grep -w "^##! $user" "/usr/local/etc/xray/04_inbounds.json" | cut -d ' ' -f 3 | sort | uniq)
d1=$(date -d "$exp" +%s)
d2=$(date -d "$now" +%s)
exp2=$(((d1 - d2) / 86400))
if [[ "$exp2" -le "0" ]]; then
sed -i "/^##! $user $exp/,/^},{/d" /usr/local/etc/xray/04_inbounds.json
sed -i "/^##! $user $exp/,/^},{/d" /usr/local/etc/xray/04_inbounds.json
systemctl restart xray
fi
done

# TROJAN
data=($(cat /usr/local/etc/xray/04_inbounds.json | grep '^##?' | cut -d ' ' -f 2 | sort | uniq))
now=$(date +"%Y-%m-%d")
for user in "${data[@]}"; do
exp=$(grep -w "^##? $user" "/usr/local/etc/xray/04_inbounds.json" | cut -d ' ' -f 3 | sort | uniq)
d1=$(date -d "$exp" +%s)
d2=$(date -d "$now" +%s)
exp2=$(((d1 - d2) / 86400))
if [[ "$exp2" -le "0" ]]; then
sed -i "/^##? $user $exp/,/^},{/d" /usr/local/etc/xray/04_inbounds.json
sed -i "/^##? $user $exp/,/^},{/d" /usr/local/etc/xray/04_inbounds.json
systemctl restart xray
fi
done

# SS
data=($(cat /usr/local/etc/xray/04_inbounds.json | grep '^##@' | cut -d ' ' -f 2 | sort | uniq))
now=$(date +"%Y-%m-%d")
for user in "${data[@]}"; do
exp=$(grep -w "^##@ $user" "/usr/local/etc/xray/04_inbounds.json" | cut -d ' ' -f 3 | sort | uniq)
d1=$(date -d "$exp" +%s)
d2=$(date -d "$now" +%s)
exp2=$(((d1 - d2) / 86400))
if [[ "$exp2" -le "0" ]]; then
sed -i "/^##@ $user $exp/,/^},{/d" /usr/local/etc/xray/04_inbounds.json
sed -i "/^##@ $user $exp/,/^},{/d" /usr/local/etc/xray/04_inbounds.json
systemctl restart xray
fi
done


