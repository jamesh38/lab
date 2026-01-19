# Home Lab K3s Cluster - Claude Instructions

## Cluster Overview

This is a two-node K3s (lightweight Kubernetes) cluster for a home lab environment.

**Internet:** 1 Gbps symmetric (1 Gbps up / 1 Gbps down)

**Network:** UniFi

### Nodes

| Node | Role | IP | Hardware | Notes |
|------|------|-----|----------|-------|
| **opti** | Control plane | 192.168.1.104 | Intel i7-7700T @ 2.9GHz (4 cores), 32GB RAM | Primary storage node, Intel QuickSync GPU |
| **thinkpad** | Worker | 192.168.1.12 | Laptop | Secondary compute |

### Storage Layout

All persistent data lives on the **opti** node under `/srv/`:

| Path | Purpose |
|------|---------|
| `/srv/media` | Main media library (movies, TV shows) - Jellyfin primary |
| `/srv/media2` | Secondary media storage |
| `/srv/jellyfin/config` | Jellyfin configuration |
| `/srv/jellyfin/cache` | Jellyfin transcoding cache |
| `/srv/downloads` | qBittorrent download directory |
| `/srv/qbittorrent/config` | qBittorrent config |
| `/srv/radarr/config` | Radarr config |
| `/srv/sonarr/config` | Sonarr config |
| `/srv/prowlarr/config` | Prowlarr config |
| `/srv/postgres` | PostgreSQL data |
| `/srv/grafana/dashboards` | Grafana dashboard JSONs |
| `/srv/grafana/provisioning` | Grafana provisioning config |
| `/srv/fonts` | Custom fonts for Jellyfin subtitles |

## Namespaces

| Namespace | Applications |
|-----------|--------------|
| `media` | Jellyfin |
| `downloads` | qBittorrent, Radarr, Sonarr, Prowlarr, FlareSolverr (all in one pod with Gluetun VPN) |
| `monitoring` | Prometheus, Node Exporter |
| `grafana` | Grafana |
| `db` | PostgreSQL |
| `teslamate` | TeslaMate, Mosquitto MQTT |
| `kube-system` | Traefik, k3s system components |

## Applications

### Media Stack

- **Jellyfin** (`stream.lab.jjh.us`) - Media server with Intel QuickSync hardware transcoding
  - Pinned to opti node for GPU access (`/dev/dri`)
  - Uses `jellyfin/jellyfin:latest` image
  - Hardware acceleration: VAAPI + QSV for transcoding
  - NodePort: 30096

### Download Stack (VPN-protected)

All download apps run in a single pod behind **Gluetun** (WireGuard VPN to AirVPN):

- **qBittorrent** (`download.lab.jjh.us`) - Torrent client, NodePort: 30088
- **Radarr** (`radarr.lab.jjh.us`) - Movie automation, NodePort: 30787
- **Sonarr** (`sonarr.lab.jjh.us`) - TV show automation, NodePort: 30898
- **Prowlarr** (`prowlarr.lab.jjh.us`) - Indexer manager, NodePort: 30969
- **FlareSolverr** - Cloudflare bypass proxy (internal)

### Monitoring

- **Prometheus** - Metrics collection, NodePort: 30090, 30-day retention
- **Grafana** (`grafana.lab.jjh.us`) - Dashboards, NodePort: 30300
- **Node Exporter** - DaemonSet on all nodes for host metrics

### Database

- **PostgreSQL 17** - Shared database, NodePort: 30432
  - Used by TeslaMate
  - Credentials: postgres / pass (internal only)

### TeslaMate

- **TeslaMate** - Tesla vehicle tracking, NodePort: 30400
- **Mosquitto** - MQTT broker for TeslaMate

### Ingress

- **Traefik** - Ingress controller with Let's Encrypt SSL
  - Domain: `*.lab.jjh.us`
  - ACME email: admin@jjh.us

## Common Commands

```bash
# View all pods
kubectl get pods -A

# View Jellyfin logs
kubectl logs -n media -l app=jellyfin --tail=100

# View download stack logs
kubectl logs -n downloads -l app=qbittorrent -c <container-name>
# Containers: gluetun, qbittorrent, radarr, sonarr, prowlarr, flaresolverr

# Restart Jellyfin
kubectl rollout restart deployment/jellyfin -n media

# Apply manifest changes
kubectl apply -f <app>/

# Check node resources
kubectl top nodes
```

## Hardware Transcoding Notes

The i7-7700T has Intel HD Graphics 630 with QuickSync. Capabilities:

- **Can hardware encode**: H.264, HEVC (8-bit)
- **Can hardware decode**: H.264, HEVC, VP9, VC-1
- **Cannot do in hardware**: HDR tone-mapping (Kaby Lake limitation)

Problematic media formats:
- **4K HDR/Dolby Vision** - Requires CPU-intensive tone-mapping if client needs SDR
- **VC-1** - Old Blu-ray codec, can decode in HW but many clients can't play it

Recommended clients for direct play (no transcoding):
- **Mac**: Jellyfin Media Player
- **iOS/iPadOS**: Swiftfin or Infuse
- **Web browsers**: Force transcoding, avoid if possible

## File Paths for Media

Movies: `/srv/media/movies/`
TV Shows: `/srv/media/tv/`

Example movie path:
```
/srv/media/movies/Movie Name (Year)/Movie.Name.Year.Quality.Codec.mkv
```

## Secrets

VPN credentials stored in Kubernetes secret `airvpn-wireguard` in `downloads` namespace.
