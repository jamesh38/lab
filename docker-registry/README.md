# Docker Registry

Private Docker container registry for your homelab.

## Deployment

```bash
kubectl apply -f registry.yaml
```

This deploys both the registry and the web UI.

## Access

- **Registry API**: https://docker.lab.jjh.us
- **Registry UI**: https://registry-ui.lab.jjh.us (browse images)
- **Registry NodePort**: http://192.168.1.104:30500
- **UI NodePort**: http://192.168.1.104:30501
- **Internal**: docker-registry.registry.svc.cluster.local:5000

## Usage

### Login to Registry

```bash
docker login docker.lab.jjh.us
```

Note: Since this is a basic registry without authentication, you may need to configure Docker to allow the registry.

### Push an Image

```bash
# Tag your image
docker tag myapp:latest docker.lab.jjh.us/myapp:latest

# Push to registry
docker push docker.lab.jjh.us/myapp:latest
```

### Pull an Image

```bash
docker pull docker.lab.jjh.us/myapp:latest
```

### List Images via API

```bash
# List repositories
curl https://docker.lab.jjh.us/v2/_catalog

# List tags for a repository
curl https://docker.lab.jjh.us/v2/myapp/tags/list
```

## Storage

- Registry data stored at: `/srv/docker-registry` on opti node
- Capacity: 100GB
- Images can be deleted via API

## Adding Authentication (Optional)

If you want to add basic authentication:

1. Generate htpasswd file:
```bash
docker run --rm --entrypoint htpasswd httpd:2 -Bbn username password > /srv/docker-registry/htpasswd
```

2. Create secret:
```bash
kubectl create secret generic registry-auth \
  --from-file=htpasswd=/srv/docker-registry/htpasswd \
  -n registry
```

3. Update the deployment to mount the secret and add environment variables for auth.

## Troubleshooting

### View logs
```bash
kubectl logs -n registry -l app=docker-registry
```

### Check status
```bash
kubectl get pods -n registry
kubectl get svc -n registry
kubectl get ingress -n registry
```

### Test registry health
```bash
curl https://docker.lab.jjh.us/v2/
```
Should return: `{}`
