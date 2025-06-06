# ChipEngine Deployment Guide

Deploy ChipEngine with a single command using Docker!

## Quick Start

### 1. Local Development

```bash
# Clone the repository
git clone https://github.com/chiptuned/chipengine.git
cd chipengine

# Copy environment variables
cp .env.example .env

# Start everything with one command!
./scripts/deploy.sh up
```

That's it! The API is now running at http://localhost:8000

### 2. Available Commands

```bash
# Start services
./scripts/deploy.sh up

# Stop services
./scripts/deploy.sh down

# View logs
./scripts/deploy.sh logs

# Check status
./scripts/deploy.sh status

# Run tests
./scripts/deploy.sh test

# Open shell in container
./scripts/deploy.sh shell

# Restart services
./scripts/deploy.sh restart

# Clean up everything
./scripts/deploy.sh clean
```

## Production Deployment

### Option 1: Railway (Recommended)

1. Fork the repository
2. Connect to Railway: https://railway.app/new
3. Select your forked repo
4. Railway will auto-detect the Dockerfile
5. Add environment variables:
   ```
   ENVIRONMENT=production
   DATABASE_URL=<auto-provided>
   SECRET_KEY=<generate-secure-key>
   ```
6. Deploy! 🚀

### Option 2: Render

1. Fork the repository
2. Create new Web Service on Render
3. Connect your GitHub repo
4. Render will use `render.yaml` configuration
5. Add environment variables in Render dashboard
6. Deploy automatically on push to main

### Option 3: DigitalOcean App Platform

1. Create new App
2. Choose GitHub repository
3. Select Dockerfile as build method
4. Configure environment variables:
   ```yaml
   - key: ENVIRONMENT
     value: production
   - key: DATABASE_URL
     value: ${db.DATABASE_URL}
   ```
5. Deploy!

### Option 4: Self-Hosted VPS

```bash
# On your VPS
git clone https://github.com/chiptuned/chipengine.git
cd chipengine

# Configure production environment
cp .env.example .env
# Edit .env with production values

# Use Docker Compose for production
docker-compose -f docker-compose.yml up -d

# Or use the deploy script
ENVIRONMENT=production ./scripts/deploy.sh up
```

## Environment Variables

Key environment variables for production:

```bash
# Required
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@host:5432/chipengine
SECRET_KEY=your-very-secure-secret-key

# Optional
LOG_LEVEL=info
RATE_LIMIT_REQUESTS=1000
REDIS_URL=redis://localhost:6379/0
```

## Database Setup

### SQLite (Default)
- Perfect for development and small deployments
- Zero configuration required
- Data stored in `data/chipengine.db`

### PostgreSQL (Production)
```bash
# Update .env
DATABASE_URL=postgresql://user:password@localhost:5432/chipengine

# Run migrations
./scripts/deploy.sh migrate
```

## Health Monitoring

All deployment options include health checks:

```bash
# Check API health
curl http://localhost:8000/health

# Response
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2024-01-01T12:00:00Z",
  "bots_count": 42,
  "active_games": 10
}
```

## SSL/HTTPS

### Railway/Render
- HTTPS included automatically
- No configuration needed

### Self-Hosted
Use a reverse proxy like Nginx:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Or use Caddy for automatic HTTPS:

```caddyfile
your-domain.com {
    reverse_proxy localhost:8000
}
```

## Scaling

### Horizontal Scaling
```yaml
# docker-compose.yml
services:
  api:
    deploy:
      replicas: 3
```

### With Load Balancer
```nginx
upstream chipengine {
    server api1:8000;
    server api2:8000;
    server api3:8000;
}
```

## Backup

### Database Backup
```bash
# SQLite
cp data/chipengine.db backups/chipengine-$(date +%Y%m%d).db

# PostgreSQL
pg_dump $DATABASE_URL > backups/chipengine-$(date +%Y%m%d).sql
```

### Automated Backups
Add to crontab:
```cron
0 2 * * * /path/to/chipengine/scripts/backup.sh
```

## Troubleshooting

### Container won't start
```bash
# Check logs
./scripts/deploy.sh logs

# Verify environment
docker-compose config
```

### Database connection issues
```bash
# Test connection
docker-compose exec api python -c "from chipengine.api.database import engine; print(engine.url)"
```

### Port already in use
```bash
# Change port in docker-compose.yml
ports:
  - "8001:8000"
```

## CI/CD Integration

### GitHub Actions
```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        run: |
          curl -fsSL https://railway.app/install.sh | sh
          railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

## Performance Optimization

### Enable Redis for Rate Limiting
```bash
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### Use PostgreSQL for Production
- Better performance at scale
- Connection pooling support
- Advanced indexing options

### CDN for Static Assets
- Use Cloudflare or similar
- Cache API responses where appropriate

## Security Best Practices

1. **Always use HTTPS in production**
2. **Set strong SECRET_KEY**
3. **Use environment variables for secrets**
4. **Enable rate limiting**
5. **Regular security updates**
6. **Monitor logs for suspicious activity**

## Support

- GitHub Issues: https://github.com/chiptuned/chipengine/issues
- Documentation: https://chipengine.dev/docs
- API Reference: https://your-deployment.com/docs

Happy deploying! 🚀