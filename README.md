# 🎬 Video Downloader Bot

A powerful Telegram bot that downloads videos from 500+ platforms including YouTube, TikTok, Instagram, Twitter, Pinterest, Facebook, Reddit, and more!

## ✨ Features

- **Multi-Platform Support**: Download from YouTube, TikTok, Instagram, Twitter/X, Pinterest, Facebook, Reddit, Snapchat, and 500+ other sites
- **High Quality Downloads**: Gets the best available quality
- **Fast Processing**: Async processing for quick downloads
- **Download History**: Tracks all user downloads in database
- **Monetization System**: Built-in ad system for revenue generation
- **Premium Features**: Ready for paid membership integration
- **User Stats**: Track downloads and usage patterns

## 🎯 Monetization Strategy

### 1. **Ad-Based Revenue** (Current Implementation)
- 5-second ad break shown before each video download
- Ad impressions tracked in database
- Customizable ad content

### 2. **Premium Membership**
```
Premium Benefits:
✅ No ads
✅ 4K/8K video quality  
✅ Priority fast processing
✅ Unlimited downloads
✅ Direct MP3 conversion
✅ Batch downloads
```

### 3. **Revenue Integration Methods**
- **Stripe/PayPal**: Monthly subscription payments
- **Telegram Stars**: Native Telegram payment system
- **CoinPayments**: Cryptocurrency payments
- **Affiliate Links**: Embed in ads

### 4. **Ad Network Integration**
```python
# Ad impression logging (database tracked)
- Google AdSense
- Facebook Audience Network
- Custom ad campaigns
- Sponsored content
```

## 📋 Database Schema

### Users Table
```sql
users (
  telegram_id BIGINT PRIMARY KEY,
  username VARCHAR(100),
  first_name VARCHAR(100),
  is_premium BOOLEAN,
  downloads_count INT,
  created_at TIMESTAMP
)
```

### Downloads Table
```sql
downloads (
  download_id SERIAL PRIMARY KEY,
  user_id BIGINT,
  platform VARCHAR(50),
  url TEXT,
  title VARCHAR(255),
  file_id VARCHAR(255),
  saw_ad BOOLEAN,
  created_at TIMESTAMP
)
```

### Ad Impressions Table (Monetization)
```sql
ad_impressions (
  impression_id SERIAL PRIMARY KEY,
  user_id BIGINT,
  ad_content VARCHAR(255),
  clicked BOOLEAN,
  created_at TIMESTAMP
)
```

## 🚀 Deployment

### Option 1: Render.com (Recommended)
1. Fork this repository
2. Connect to Render
3. Set environment variables:
   - `BOT_TOKEN`: Your Telegram bot token
   - `DATABASE_URL`: PostgreSQL connection string
4. Deploy!

### Option 2: Railway.app
1. Create railway.json (included)
2. Push to GitHub
3. Connect to Railway
4. Configure PostgreSQL addon
5. Deploy

### Option 3: Docker
```bash
docker build -t video-bot .
docker run -e BOT_TOKEN=your_token -e DATABASE_URL=your_db video-bot
```

## 🔧 Setup Instructions

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export BOT_TOKEN=your_token_here
export DATABASE_URL=postgresql://user:pass@localhost/dbname

# Run the bot
python bot.py
```

### Create Telegram Bot
1. Message @BotFather on Telegram
2. Create new bot `/newbot`
3. Copy the token
4. Set it in environment variables

### PostgreSQL Setup
```bash
# Create database
createdb downloader_bot

# Bot will auto-create tables on first run
```

## 💰 Monetization Implementation

### Step 1: Upgrade to Premium (Stripe)
```python
# Add to your bot
from stripe import Customer, Subscription

async def handle_premium_purchase(update, context):
    user_id = update.effective_user.id
    # Create Stripe customer
    # Send payment link
    # Update is_premium in database
```

### Step 2: Track Ad Revenue
```python
# Modify show_ad_and_download() to:
log_ad_impression(user_id, ad_content)
# Calculate CPM: (impressions / 1000) * rate
# Typical rates: $0.50 - $5 per 1000 impressions
```

### Step 3: Integrate Ad Network
```python
ad_networks = {
    'google_adsense': 'Your Publisher ID',
    'facebook': 'Your App ID',
    'custom_ads': 'Your campaign IDs'
}

# Show relevant ads based on user region
```

## 📊 Analytics & Metrics

### Revenue Metrics
- Downloads per day
- Ad impressions per day
- Premium users count
- Revenue per user (ARPU)
- Churn rate

### Performance Metrics
- Download success rate
- Average download time
- User retention
- Engagement rate

### Query Example:
```sql
-- Daily revenue report
SELECT 
    DATE(created_at) as date,
    COUNT(*) as impressions,
    COUNT(CASE WHEN clicked THEN 1 END) as clicks,
    (COUNT(*) / 1000) * 2.5 as estimated_revenue
FROM ad_impressions
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

## 🛡️ Features Summary

| Feature | Free | Premium |
|---------|------|---------|
| Download videos | ✅ | ✅ |
| Ads shown | ✅ | ❌ |
| Download quality | 720p max | 4K/8K |
| Speed | Standard | Priority |
| Download history | ✅ | ✅ |
| MP3 conversion | ❌ | ✅ |
| Batch downloads | ❌ | ✅ |

## 📱 Supported Platforms

✅ YouTube  
✅ TikTok  
✅ Instagram  
✅ Twitter/X  
✅ Pinterest  
✅ Facebook  
✅ Reddit  
✅ Snapchat  
✅ And 490+ more!

## 🔐 Privacy & Security

- No video storage (downloads sent directly to users)
- No personal data sharing
- Database encrypted
- Secure token handling
- GDPR compliant

## 🐛 Troubleshooting

### "Failed to download from platform"
- Platform may have changed
- Update yt-dlp: `pip install --upgrade yt-dlp`
- Check if URL is valid

### Database connection issues
- Verify DATABASE_URL format
- Check PostgreSQL is running
- Ensure database exists

### File size too large
- Bot has 2GB upload limit per file
- Large videos may fail
- Premium: Add split/compression

## 📝 Commands

- `/start` - Start bot & show menu
- `/help` - Show help information

## 🎨 Customization

Edit the following in `bot.py`:
```python
# Change ad message (line ~350)
ad_text = "Your custom ad here"

# Change supported platforms (line ~180)
def get_platform(url):
    # Add/remove platforms

# Change video quality (line ~205)
ydl_opts = {
    'format': 'best[ext=mp4]/best'  # Modify format string
}
```

## 📈 Growth Tips

1. **Bot Marketing**
   - Share @YourBotUsername on Reddit
   - Post on Twitter/TikTok communities
   - List on BotStore websites

2. **Premium Upsell**
   - Show premium features after 5 downloads
   - Offer free trial period
   - Create comparison graphics

3. **Affiliate Program**
   - Partner with VPN services
   - Link to video hosting platforms
   - Earn commission per referral

4. **Ad Optimization**
   - A/B test different ad content
   - Target by geography
   - Increase frequency gradually

## 🤝 Contributing

Contributions welcome! Please:
1. Test thoroughly
2. Follow existing code style
3. Update README
4. Submit PR

## 📄 License

MIT License - Feel free to use and modify

## 💬 Support

For issues or questions:
- Check troubleshooting section
- Review bot.py comments
- Test on Telegram with @BotFather

## 🚀 Next Steps

1. Deploy to Render/Railway
2. Set up PostgreSQL database
3. Configure Stripe for premium
4. Integrate Google AdSense
5. Monitor analytics dashboard

---

**Estimated Monthly Revenue (1,000 daily active users):**
- Ad impressions: ~30,000/day = 900,000/month
- At $2.50 CPM: **$2,250/month**
- Premium (10% conversion @ $5/month): **$500/month**
- **Total: ~$2,750/month**

*Note: Actual revenue varies based on geography, traffic quality, and ad network rates.*
