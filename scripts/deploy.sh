#!/bin/bash
# One-command deployment script for ChipEngine

set -e

echo "🚀 ChipEngine Deployment Script"
echo "================================"

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Load environment variables if .env exists
if [ -f .env ]; then
    echo "📋 Loading environment variables from .env"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  No .env file found. Using defaults."
    echo "💡 Copy .env.example to .env and configure as needed."
fi

# Parse command line arguments
COMMAND=${1:-up}
ENVIRONMENT=${ENVIRONMENT:-development}

case $COMMAND in
    up|start)
        echo "🔨 Building and starting services..."
        docker-compose up --build -d
        echo "✅ Services started!"
        echo "📊 API available at: http://localhost:8000"
        echo "📚 API docs at: http://localhost:8000/docs"
        ;;
    
    down|stop)
        echo "🛑 Stopping services..."
        docker-compose down
        echo "✅ Services stopped!"
        ;;
    
    restart)
        echo "🔄 Restarting services..."
        docker-compose restart
        echo "✅ Services restarted!"
        ;;
    
    logs)
        echo "📜 Showing logs..."
        docker-compose logs -f ${2:-api}
        ;;
    
    status)
        echo "📊 Service status:"
        docker-compose ps
        ;;
    
    test)
        echo "🧪 Running tests..."
        docker-compose exec api pytest tests/
        ;;
    
    shell)
        echo "🐚 Opening shell in API container..."
        docker-compose exec api /bin/bash
        ;;
    
    migrate)
        echo "🔄 Running database migrations..."
        docker-compose exec api alembic upgrade head
        echo "✅ Migrations complete!"
        ;;
    
    build)
        echo "🔨 Building images..."
        docker-compose build
        echo "✅ Build complete!"
        ;;
    
    clean)
        echo "🧹 Cleaning up..."
        docker-compose down -v
        docker system prune -f
        echo "✅ Cleanup complete!"
        ;;
    
    *)
        echo "Usage: $0 {up|down|restart|logs|status|test|shell|migrate|build|clean}"
        echo ""
        echo "Commands:"
        echo "  up/start  - Build and start all services"
        echo "  down/stop - Stop all services"
        echo "  restart   - Restart all services"
        echo "  logs      - Show logs (optional: service name)"
        echo "  status    - Show service status"
        echo "  test      - Run tests"
        echo "  shell     - Open shell in API container"
        echo "  migrate   - Run database migrations"
        echo "  build     - Build Docker images"
        echo "  clean     - Stop services and clean up volumes"
        exit 1
        ;;
esac