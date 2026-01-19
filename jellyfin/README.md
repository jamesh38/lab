# Jellyfin NFS Setup Guide

## Current Setup
- Media stored at `/srv/media` on opti node
- Using hostPath volumes (single-node only)

## Multi-Node Setup with NFS

### Step 1: Setup NFS Server on Media Node (opti)
```bash
cd /home/james/apps/jellyfin
./setup-nfs.sh
```

This will:
- Install NFS server
- Export `/srv/media` to your local network
- Configure proper permissions

### Step 2: Install NFS Client on Other Nodes
On each additional k8s node:
```bash
sudo apt update
sudo apt install -y nfs-common
```

### Step 3: Create NFS PersistentVolume
```bash
kubectl apply -f nfs-media-pv.yaml
```

This creates:
- PersistentVolume pointing to NFS share
- PersistentVolumeClaim in media namespace

### Step 4: Update Jellyfin to Use NFS
Edit your Jellyfin deployment in Portainer or via kubectl and change the media volume from:
```yaml
- hostPath:
    path: /srv/media
    type: Directory
  name: media
```

To:
```yaml
- persistentVolumeClaim:
    claimName: nfs-media
  name: media
```

## Benefits
- Jellyfin can run on any node
- Media accessible from all nodes
- Easy to add more services that need media access

## Rollback
If you need to go back to single-node:
1. Revert the volume change in Jellyfin deployment
2. Keep NFS server running for future use or uninstall it
