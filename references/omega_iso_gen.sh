#!/bin/bash
# OMEGA-CODE System Recovery ISO Builder
set -e

echo "💿 Initializing OMEGA-CODE Recovery ISO Generation..."

# 1. Install FOSS Recovery Tools
sudo apt-get install -y rear genisoimage xorriso isolinux

# 2. Configure ReaR for Full System Backup
cat <<EOF | sudo tee /etc/rear/local.conf
OUTPUT=ISO
OUTPUT_URL=null
BACKUP=NETFS
BACKUP_URL="iso:///backup"
# Include OMEGA-CODE projects and keys in the ISO
COPY_AS_IS=( "/opt/omega-code" "/home/omega/.ssh" )
EOF

# 3. Generate the Bootable ISO
sudo rear -v mkbackup

echo "✅ Recovery ISO Generated: /var/lib/rear/output/rear-omega-host.iso"
echo "👉 Flash this to a USB drive to restore your entire fortress on new hardware."
