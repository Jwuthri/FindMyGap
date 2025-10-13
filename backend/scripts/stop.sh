#!/bin/bash
# Stop script for FindMyGap Backend

set -e

echo "🛑 Stopping FindMyGap Backend..."

# Default environment
ENVIRONMENT=${1:-development}

case $ENVIRONMENT in
    "development" | "dev")
        echo "🔧 Stopping development environment..."

        # Stop development services
        docker-compose -f docker/docker-compose.dev.yml down

        echo "✅ Development services stopped!"
        ;;

    "production" | "prod")
        echo "🏭 Stopping production environment..."

        # Stop production services
        docker-compose -f docker/docker-compose.yml down

        echo "✅ Production services stopped!"
        ;;

    "all")
        echo "🧹 Stopping all environments..."

        # Stop both development and production
        docker-compose -f docker/docker-compose.dev.yml down 2>/dev/null || true
        docker-compose -f docker/docker-compose.yml down 2>/dev/null || true

        echo "✅ All services stopped!"
        ;;

    *)
        echo "❌ Invalid environment: $ENVIRONMENT"
        echo "Usage: $0 [development|production|all]"
        exit 1
        ;;
esac

# Clean up option
if [ "$2" = "--clean" ]; then
    echo ""
    echo "🧹 Cleaning up Docker resources..."

    # Remove unused containers, networks, and images
    docker system prune -f

    # Optionally remove volumes (be careful!)
    read -p "🗑️  Remove Docker volumes? This will delete all data! (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker volume prune -f
        echo "✅ Volumes cleaned!"
    fi
fi

echo ""
echo "🎉 FindMyGap Backend stopped successfully!"
echo ""
echo "💡 Tips:"
echo "   • Use --clean flag to remove unused Docker resources"
echo "   • Run './scripts/start.sh' to start services again"
echo "   • Run 'docker-compose logs' to view recent logs"
