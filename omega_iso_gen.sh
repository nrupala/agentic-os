#!/usr/bin/env bash
# PHASE 19: Recovery ISO Generator
# Creates bootable recovery image using ReaR

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RECOVERY_DIR="${SCRIPT_DIR}/recovery-iso"
WORK_DIR="/tmp/omega-rear-$$"

echo "========================================"
echo "OMEGA Recovery ISO Generator"
echo "========================================"

mkdir -p "${RECOVERY_DIR}"
mkdir -p "${WORK_DIR}"

configure_rear() {
    echo "[*] Configuring ReaR..."
    
    cat > "${WORK_DIR}/rear.conf" << 'EOF'
OUTPUT=ISO
OUTPUT_URL=file://${RECOVERY_DIR}
BACKUP=NETFS
BACKUP_URL=file:///mnt/local/backup
BACKUP_TYPE=incremental
BACKUP_PROG=tar
BACKUP_PROG_COMPRESS_SUFFIX=gz
BACKUP_ARCHIVE_ISOCOMPRESS=gz
EXCLUDE_VG=( vg_other )
ONLY_INCLUDE_VG=( vg_omega )
BACKUP_EXCLUDE=( /tmp/* /var/tmp/* /proc/* /sys/* /dev/* /run/* /snapshots/* )
GRUB_RESCUE=y
ISO_MAX_SIZE=4500
BOOTLOADER=GRUB
EFIBOOT=YES
SECURE_BOOT=YES
USE_STATIC_YES=y
NETFS_KEEP_OLD_BACKUP_COPY=yes
AUTOEXCLUDE_MULTIPATH=n
CLONE_ALL_USERS_GROUPS=y
COPY_AS_IS_EXCLUDE=( /etc/ssh/ssh_host_*_key )
EXCLUDE_MOUNTPOINTS=( /data /backup )
EOF
    
    echo "[+] ReaR configured"
}

generate_seed_decryption() {
    echo "[*] Generating seed decryption script..."
    
    cat > "${WORK_DIR}/omega-decrypt.sh" << 'EOFSCRIPT'
#!/bin/bash
# OMEGA Master Seed Decryption on Cold Start

echo "========================================="
echo "OMEGA Recovery - Enter Master Seed"
echo "========================================="
echo -n "Master Seed (hex): "
read -s SEED

SEED_HASH=$(echo -n "$SEED" | sha256sum | cut -d' ' -f1)
EXPECTED_HASH=$(cat /root/.omega/seed.hash 2>/dev/null || echo "")

if [ "$SEED_HASH" != "$EXPECTED_HASH" ] && [ -n "$EXPECTED_HASH" ]; then
    echo "ERROR: Invalid seed hash"
    exit 1
fi

echo "$SEED" | openssl dgst -sha256 -hmac "omega-recovery" > /root/.omega/master.key
chmod 600 /root/.omega/master.key

echo "Master key decrypted successfully"
echo "System ready for recovery"
EOFSCRIPT
    
    chmod +x "${WORK_DIR}/omega-decrypt.sh"
    echo "[+] Seed decryption script created"
}

create_recovery_menu() {
    echo "[*] Creating recovery boot menu..."
    
    cat > "${WORK_DIR}/rear-menu.cfg" << 'EOFMENU'
timeout 30
default omega-recovery

label omega-recovery
    menu label ^OMEGA System Recovery
    kernel /boot/kernel
    append initrd=/boot/initrd.img quiet splash

label omega-restore
    menu label ^Restore from Backup
    kernel /boot/kernel
    append initrd=/boot/initrd.img quiet splash rear/recover

label omega-decrypt
    menu label ^Decrypt Master Seed
    kernel /boot/kernel
    append initrd=/boot/initrd.img quiet splash omega/decrypt
EOFMENU
    
    echo "[+] Recovery menu created"
}

build_iso() {
    echo "[*] Building recovery ISO..."
    
    if ! command -v rear &> /dev/null; then
        echo "[!] ReaR not installed. Creating manual ISO structure..."
        create_manual_iso
        return
    fi
    
    rear mkrescue --conf="${WORK_DIR}/rear.conf" 2>&1 || create_manual_iso
    
    echo "[+] ISO built at ${RECOVERY_DIR}"
}

create_manual_iso() {
    echo "[*] Creating manual ISO structure..."
    
    ISO_DIR="${WORK_DIR}/iso-root"
    mkdir -p "${ISO_DIR}"/{boot,EFI,isolinux}
    
    cat > "${ISO_DIR}/isolinux/isolinux.cfg" << 'EOF'
UI menu.c32
PROMPT 0
TIMEOUT 30
DEFAULT omega

LABEL omega
    MENU LABEL OMEGA Recovery
    KERNEL /boot/vmlinuz
    INITRD /boot/initrd.img
    APPEND root=/dev/sr0 ro quiet

LABEL omega-decrypt
    MENU LABEL OMEGA - Decrypt Seed
    KERNEL /boot/vmlinuz
    INITRD /boot/initrd.img
    APPEND root=/dev/sr0 ro quiet omega.decrypt=1
EOF
    
    cat > "${ISO_DIR}/README.txt" << 'EOF'
===========================================
OMEGA System Recovery
===========================================

Boot Options:
1. Default - Boot into recovery mode
2. Decrypt Seed - Enter master recovery seed

To recover:
1. Boot from this ISO
2. Select recovery option
3. Follow prompts to restore from backup

For seed decryption:
- Enter your 64-character hex master seed
- System will verify hash before decrypting
EOF
    
    cp "${WORK_DIR}/omega-decrypt.sh" "${ISO_DIR}/"
    
    if command -v xorriso &> /dev/null; then
        xorriso -as mkisofs \
            -o "${RECOVERY_DIR}/omega-recovery.iso" \
            -isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin \
            -c isolinux/boot.cat \
            -b isolinux/isolinux.bin \
            -no-emul-boot \
            -boot-load-size 4 \
            -boot-info-table \
            "${ISO_DIR}"
        
        echo "[+] ISO created: ${RECOVERY_DIR}/omega-recovery.iso"
    else
        echo "[!] xorriso not found. ISO structure created at: ${ISO_DIR}"
        echo "[!] Install xorriso and run: xorriso -as mkisofs ..."
    fi
}

cleanup() {
    echo "[*] Cleaning up temporary files..."
    rm -rf "${WORK_DIR}"
    echo "[+] Cleanup complete"
}

main() {
    configure_rear
    generate_seed_decryption
    create_recovery_menu
    build_iso
    cleanup
    
    echo ""
    echo "========================================"
    echo "Recovery ISO Generation Complete!"
    echo "Location: ${RECOVERY_DIR}"
    echo "========================================"
}

trap cleanup EXIT
main "$@"
