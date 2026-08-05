#!/bin/bash
# One-command development environment setup for Telegram PHP Bot
# Run: bash scripts/setup-dev-env.sh

set -euo pipefail

echo "🚀 Setting up Telegram PHP Bot development environment..."

# Check PHP
if ! command -v php &> /dev/null; then
    echo "❌ PHP not found. Installing..."
    apt-get update && apt-get install -y php php-cli php-curl php-json php-mbstring php-pdo php-sqlite3 php-zip php-xml
else
    echo "✅ PHP $(php -r 'echo PHP_VERSION;')"
fi

# Check Composer
if ! command -v composer &> /dev/null; then
    echo "📦 Installing Composer..."
    curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer
else
    echo "✅ Composer $(composer --version --no-ansi | cut -d' ' -f3)"
fi

# Check sqlite3
if ! command -v sqlite3 &> /dev/null; then
    echo "🗄️ Installing SQLite..."
    apt-get install -y sqlite3
else
    echo "✅ SQLite $(sqlite3 --version | cut -d' ' -f1)"
fi

# Check ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "🎬 Installing ffmpeg..."
    apt-get install -y ffmpeg
else
    echo "✅ ffmpeg $(ffmpeg -version | head -1 | cut -d' ' -f3)"
fi

# Check yt-dlp
if ! command -v yt-dlp &> /dev/null; then
    echo "📥 Installing yt-dlp..."
    pip3 install --no-cache-dir yt-dlp
else
    echo "✅ yt-dlp $(yt-dlp --version)"
fi

# Install PHP dependencies
if [ -f "composer.json" ]; then
    echo "📚 Installing PHP dependencies..."
    composer install --no-dev --optimize-autoloader
else
    echo "⚠️ No composer.json found"
fi

# Create database
if [ -f "database/schema.sql" ]; then
    echo "🗄️ Creating database..."
    mkdir -p database tmp
    sqlite3 database/bot.sqlite < database/schema.sql
    echo "✅ Database ready"
fi

# Create .env from example if missing
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "⚙️ Creating .env from example..."
    cp .env.example .env
    echo "✏️  Edit .env with your bot token and settings"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your BOT_TOKEN, BOT_USERNAME, ADMIN_ID"
echo "2. Start dev server: php -S localhost:8000 webhook.php"
echo "3. Test with: curl -X POST http://localhost:8000/webhook.php -H 'Content-Type: application/json' -d '{\"message\":{\"chat\":{\"id\":YOUR_ID},\"from\":{\"id\":YOUR_ID},\"text\":\"/start\"}}'"