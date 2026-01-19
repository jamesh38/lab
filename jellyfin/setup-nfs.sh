#!/bin/bash
# Setup NFS server on the media node for sharing media across k8s nodes

set -e

echo "Setting up NFS server for media storage..."

# Install NFS server
echo "Installing NFS server..."
sudo apt update
sudo apt install -y nfs-kernel-server

# Create NFS exports configuration
echo "Configuring NFS exports..."
sudo tee -a /etc/exports > /dev/null <<EOF

# Media storage for Kubernetes
/srv/media 192.168.1.0/24(rw,sync,no_subtree_check,no_root_squash)
EOF

# Export the shares
echo "Exporting NFS shares..."
sudo exportfs -ra

# Enable and start NFS server
echo "Starting NFS server..."
sudo systemctl enable nfs-kernel-server
sudo systemctl restart nfs-kernel-server

echo ""
echo "NFS server setup complete!"
echo ""
echo "Exported: /srv/media"
echo "Network: 192.168.1.0/24"
echo ""
echo "To mount on other nodes, run:"
echo "  sudo apt install nfs-common"
echo "  sudo mount 192.168.1.104:/srv/media /mnt/media"
echo ""
echo "Next steps:"
echo "1. Apply the NFS PersistentVolume: kubectl apply -f nfs-media-pv.yaml"
echo "2. Update jellyfin deployment to use NFS PVC"
