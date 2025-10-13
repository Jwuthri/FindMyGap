#!/bin/bash
# Start script for FindMyGap Backend

set -e

echo "🚀 Starting FindMyGap Backend..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Default environment
ENVIRONMENT=${1:-development}

case $ENVIRONMENT in
    "development" | "dev")
        echo "🔧 Starting development environment..."

        # Build and start development services
        docker-compose -f docker/docker-compose.dev.yml up --build -d

        echo "✅ Development services started!"
        echo ""
        echo "📍 Available services:"
        echo "   🔗 Backend API: http://localhost:8000"
        echo "   🔗 API Docs: http://localhost:8000/docs"
        echo "   🔗 Health Check: http://localhost:8000/health"
        
        echo "   🗄️ PostgreSQL: localhost:5432"
        echo "   🔗 pgAdmin: http://localhost:5050 (admin@findmygap.local / admin)"
        
        echo "   🔗 Redis: localhost:6379"
        echo "   🔗 Kafka: localhost:9092"
        echo "   🔗 RabbitMQ: localhost:5672"
        echo "   🔗 RabbitMQ Management: http://localhost:15672 (guest/guest)"
        echo ""
        echo "📊 Optional UIs (use profiles):"
        echo "   docker-compose -f docker/docker-compose.dev.yml --profile kafka-ui up -d"
        echo "   docker-compose -f docker/docker-compose.dev.yml --profile redis-ui up -d"
        
        echo "   docker-compose -f docker/docker-compose.dev.yml --profile pgadmin up -d"
        
        echo ""
        echo "🔍 View logs: docker-compose -f docker/docker-compose.dev.yml logs -f backend-dev"
        ;;

    "production" | "prod")
        echo "🏭 Starting production environment..."

        # Check for required environment variables
        if [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
            echo "⚠️  Warning: No LLM API keys found in environment variables."
            echo "   Set OPENAI_API_KEY or ANTHROPIC_API_KEY before running in production."
        fi

        if [ "$SECRET_KEY" = "your-secret-key-change-in-production" ]; then
            echo "⚠️  Warning: Using default SECRET_KEY. Change it in production!"
        fi

        # Build and start production services
        docker-compose -f docker/docker-compose.yml up --build -d

        echo "✅ Production services started!"
        echo ""
        echo "📍 Available services:"
        echo "   🔗 Backend API: http://localhost:8000"
        echo "   🔗 Nginx Proxy: http://localhost:80 (optional, use --profile nginx)"
        
        echo "   🗄️ PostgreSQL: localhost:5432"
        
        echo "   🔗 Redis: localhost:6379"
        echo "   🔗 Kafka: localhost:9092"
        echo "   🔗 RabbitMQ: localhost:5672"
        echo ""
        echo "🔍 View logs: docker-compose -f docker/docker-compose.yml logs -f backend"
        ;;

    *)
        echo "❌ Invalid environment: $ENVIRONMENT"
        echo "Usage: $0 [development|production]"
        exit 1
        ;;
esac

echo ""
echo "🎉 FindMyGap Backend is starting up!"
echo "⏳ Wait a few seconds for all services to be ready..."
echo ""
echo "💡 Tips:"
echo "   • Run 'docker-compose logs -f <service>' to view logs"
echo "   • Run './scripts/stop.sh' to stop all services"
echo "   • Run './scripts/status.sh' to check service status"
