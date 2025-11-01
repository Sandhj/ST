#!/bin/bash

FILE="/usr/local/etc/xray/config/04_inbounds.json"

echo "——————————————————————————————————————————————"
echo "    ATUR SEMUA AKUN (###, ##!, #&!)    "
echo "    Gunakan angka positif (+) atau negatif (-)"
echo "——————————————————————————————————————————————"

if [[ ! -f "$FILE" ]]; then
    echo "❌ File konfigurasi tidak ditemukan: $FILE"
    exit 1
fi

# Input: bisa positif (perpanjang) atau negatif (kurangi)
read -p "Masukkan penyesuaian hari (contoh: 7 atau -3): " EXP_INPUT

# Validasi: hanya angka, boleh diawali tanda minus
if ! [[ "$EXP_INPUT" =~ ^-?[0-9]+$ ]]; then
    echo "❌ Input harus berupa bilangan bulat (misal: 5, -2, 0)."
    exit 1
fi

# Hindari perubahan nol hari kecuali disengaja — opsional, tapi izinkan
if [[ "$EXP_INPUT" -eq 0 ]]; then
    echo "ℹ️ Input 0 hari — tidak ada perubahan yang akan dilakukan."
    exit 0
fi

echo "Memproses penyesuaian akun dengan $EXP_INPUT hari..."
echo "——————————————————————————————————————————————"

# Fungsi helper untuk memproses tiap pola
process_pattern() {
    local PATTERN_PREFIX="$1"
    local LABEL="$2"
    echo "🔹 Memproses pola: $LABEL"

    # Gunakan grep dengan pola dinamis; pastikan awal baris atau karakter apa pun sebelum prefix
    while IFS= read -r LINE; do
        [[ -z "$LINE" ]] && continue

        # Ekstrak username dan tanggal — asumsi format: <prefix> <username> <YYYY-MM-DD>
        USER=$(echo "$LINE" | awk -v pat="$PATTERN_PREFIX" '$0 ~ pat {print $2}')
        OLD_DATE=$(echo "$LINE" | awk -v pat="$PATTERN_PREFIX" '$0 ~ pat {print $3}')

        # Validasi tanggal
        if ! date -d "$OLD_DATE" >/dev/null 2>&1; then
            echo "   ⚠️ Tanggal tidak valid untuk $LABEL user: $USER"
            continue
        fi

        # Hitung tanggal baru (bisa maju atau mundur)
        NEW_DATE=$(date -d "$OLD_DATE $EXP_INPUT days" +"%Y-%m-%d" 2>/dev/null)
        if [[ $? -ne 0 ]]; then
            echo "   ⚠️ Gagal menghitung tanggal baru untuk $LABEL $USER"
            continue
        fi

        # Escape baris lama untuk sed
        ESC_OLD=$(printf '%s' "$LINE" | sed 's/[[\.*^$()+?{|]/\\&/g; s/]/\\]/g')
        REPLACEMENT="$PATTERN_PREFIX $USER $NEW_DATE"

        # Ganti di file
        sed -i "s|$ESC_OLD|$REPLACEMENT|" "$FILE"

        echo "   ✓ $LABEL $USER → $NEW_DATE"
    done < <(grep -E "\\$PATTERN_PREFIX [a-zA-Z0-9_\-]+ [0-9]{4}-[0-9]{2}-[0-9]{2}" "$FILE")
}

# ————————————————————————————————————————
# Proses ketiga pola secara terpisah
# ————————————————————————————————————————
process_pattern "###" "###"
echo ""
process_pattern "##!" "##!"
echo ""
process_pattern "#&!" "#&!"

echo ""
echo "✅ Semua akun telah disesuaikan dengan $EXP_INPUT hari."
echo "📁 File konfigurasi: $FILE"
# Opsional: systemctl reload xray
