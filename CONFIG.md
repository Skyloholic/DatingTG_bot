# Configuration Template

Copy this file and fill in your values. Save as `.env` and load it in your bot.

## Bot Configuration

```ini
# Telegram Bot Token (from @BotFather)
BOT_TOKEN=your_bot_token_here

# Database Connection
DATABASE_URL=postgresql://username:password@localhost:5432/downloader_bot

# Optional: Admin ID for dashboard access
ADMIN_USER_ID=your_telegram_id_here

# Optional: Webhook URL (for remote deployment)
WEBHOOK_URL=https://your-domain.com

# Optional: Stripe API Key (for premium)
STRIPE_API_KEY=sk_live_your_stripe_key_here

# Optional: Stripe Product IDs
STRIPE_PREMIUM_PRICE_ID=price_xxx

# Optional: Bot Owner Contact (for premium upsell)
BOT_OWNER_CONTACT=@your_username
SUPPORT_GROUP=https://t.me/your_support_group
```

## Environment Setup

### For Render.com
Add these in project Settings → Environment:
```
BOT_TOKEN = your_token
DATABASE_URL = your_postgres_url
ADMIN_USER_ID = your_id
```

### For Railway.app
Create `railway.json`:
```json
{
  "variables": {
    "BOT_TOKEN": {
      "description": "Telegram Bot Token",
      "isOptional": false
    },
    "DATABASE_URL": {
      "description": "PostgreSQL Connection String",
      "isOptional": false
    }
  }
}
```

### For Local Development
Create `.env` file in project root:
```bash
# .env
BOT_TOKEN=123456789:ABCdefGHIJKlmnoPQRstUVwxYZ
DATABASE_URL=postgresql://user:password@localhost:5432/downloader_bot
ADMIN_USER_ID=123456789
```

Then load it:
```python
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
```

## Database Setup

### PostgreSQL Connection String Format
```
postgresql://username:password@host:port/database
```

### Local Example
```
postgresql://postgres:password@localhost:5432/downloader_bot
```

### Render Example
```
postgresql://user:pass@dpg-xxxxx.render.internal/downloader_bot
```

### Railway Example
```
postgresql://user:pass@containers-us-west-xxx.railway.app:5432/downloader_bot
```

## Video Download Settings

### Quality Presets (in bot.py)

#### Standard Quality
```python
ydl_opts = {
    'format': 'best[ext=mp4]/best',  # Good balance
}
```

#### High Quality (4K)
```python
ydl_opts = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
}
```

#### Low Quality (Fast)
```python
ydl_opts = {
    'format': 'worst[ext=mp4]/worst',  # Smallest file
}
```

## Ad Configuration

### Default Ad Settings

```python
# Show ad every N downloads (prevent ad fatigue)
AD_FREQUENCY = 1  # Show every download

# Max ads per hour per user
MAX_ADS_PER_HOUR = 3

# Ad display time (seconds)
AD_DISPLAY_TIME = 5

# Premium user gets ads removed after
PREMIUM_USERS_EXEMPT_FROM_ADS = True
```

### Custom Sponsorship

```python
SPONSORSHIP_ENABLED = True

SPONSORED_ADS = {
    'vpn': {
        'campaigns': [
            {
                'title': '🔒 ExpressVPN',
                'text': 'Secure your downloads. 30% off →',
                'url': 'https://affiliate.expressvpn.com/ref',
                'enabled': True
            }
        ]
    }
}
```

## Monetization Settings

### Premium Pricing

```python
PREMIUM_CONFIG = {
    'monthly': {
        'price_usd': 2.99,
        'price_stars': 119,  # Telegram Stars
        'duration_days': 30,
        'features': [
            'no_ads',
            'quality_4k',
            'priority_speed',
            'mp3_conversion',
            'batch_downloads'
        ]
    },
    'yearly': {
        'price_usd': 25.00,
        'price_stars': 999,
        'duration_days': 365,
        'features': 'all'
    }
}
```

### Ad Revenue Settings

```python
AD_REVENUE_CONFIG = {
    'google_adsense': {
        'enabled': False,
        'publisher_id': 'pub-xxxxxxxxxxxxxxxx'
    },
    'facebook_audience': {
        'enabled': False,
        'app_id': 'xxxxxxxxxxxx'
    },
    'custom_cpm': {
        'rate_usd_per_mille': 2.50  # $2.50 per 1000 impressions
    }
}
```

## Feature Flags

```python
# Enable/disable features without redeployment
FEATURES = {
    'premium_enabled': True,
    'ads_enabled': True,
    'analytics_enabled': True,
    'referral_program': False,
    'telegram_stars': True,
    'stripe_payments': False,
    'mp3_conversion': False,
    'batch_downloads': False,
}

# Maintenance mode
MAINTENANCE_MODE = False
MAINTENANCE_MESSAGE = "Bot is under maintenance. Back soon!"
```

## Logging

```python
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL

LOG_FILES = {
    'downloads': 'logs/downloads.log',
    'errors': 'logs/errors.log',
    'payments': 'logs/payments.log',
    'analytics': 'logs/analytics.log',
}
```

## Rate Limiting

```python
RATE_LIMITS = {
    'downloads_per_hour': 50,  # Max downloads per hour
    'downloads_per_day': 200,   # Max downloads per day
    'free_tier_limit': 50,      # Free users
    'premium_tier_limit': 500,  # Premium users
    'messages_per_second': 30,  # Telegram API limit
}
```

## Platform Settings

```python
SUPPORTED_PLATFORMS = [
    'youtube',
    'tiktok',
    'instagram',
    'twitter',
    'pinterest',
    'facebook',
    'reddit',
    'snapchat',
    # 500+ more via yt-dlp
]

# Platform-specific settings
PLATFORM_CONFIG = {
    'tiktok': {
        'include_watermark': False,
        'max_quality': '1080p',
    },
    'youtube': {
        'include_subtitles': False,
        'prefer_format': 'mp4',
    },
    'instagram': {
        'max_quality': '1080p',
    }
}
```

## Deployment Checklist

Before deploying, verify:

- [ ] `BOT_TOKEN` is set and valid
- [ ] `DATABASE_URL` is set and PostgreSQL is accessible
- [ ] `requirements.txt` is up to date
- [ ] `Dockerfile` has ffmpeg installed
- [ ] Environment variables are set in deployment platform
- [ ] Database tables are created (auto-creates on first run)
- [ ] Bot responds to `/start` command
- [ ] Can download from at least one platform
- [ ] Ads display correctly before videos
- [ ] Download history is logged to database

## Quick Deploy Script

```bash
#!/bin/bash

# Set variables
TOKEN="your_token_here"
DB_URL="postgresql://..."
ADMIN_ID="your_id"

# Export to environment
export BOT_TOKEN=$TOKEN
export DATABASE_URL=$DB_URL
export ADMIN_USER_ID=$ADMIN_ID

# Run bot
python bot.py
```

## Troubleshooting Configuration

### Bot not responding?
```bash
# Check token
python -c "import os; print(os.getenv('BOT_TOKEN'))"

# Test bot connection
python -c "from telegram import Bot; Bot(token=os.getenv('BOT_TOKEN')).get_me()"
```

### Database connection fails?
```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Check format is correct:
# postgresql://user:pass@host:port/dbname
```

### Video downloads fail?
```bash
# Update yt-dlp
pip install --upgrade yt-dlp

# Test yt-dlp directly
yt-dlp "https://youtube.com/watch?v=dQw4w9WgXcQ"
```

## Performance Tuning

### Database Connection Pool
```python
db_pool = psycopg2.pool.SimpleConnectionPool(
    1,    # Min connections
    10,   # Max connections
    DATABASE_URL
)
```

### Video Download Timeout
```python
ydl_opts = {
    'socket_timeout': 30,  # 30 seconds
    'http_chunk_size': 10485760,  # 10MB chunks
}
```

### Request Limits
```python
MAX_CONCURRENT_DOWNLOADS = 5
QUEUE_TIMEOUT_SECONDS = 300  # 5 minutes
```

---

**Ready to deploy? Start with QUICKSTART.md!**
