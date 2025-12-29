# 🚀 Quick Start Guide

Get your video downloader bot running in 5 minutes!

## Step 1: Get Your Bot Token (2 min)

1. Open Telegram and message **@BotFather**
2. Type `/newbot`
3. Give it a name (e.g., "My Video Downloader")
4. Give it a username (e.g., @my_video_downloader_bot)
5. **Copy the token** - you'll need it soon

Example token: `123456789:ABCdefGHIJKlmnoPQRstUVwxYZ`

---

## Step 2: Deploy on Render.com (3 min)

### Option A: Use Render (Recommended - Free tier available)

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Connect your GitHub account
4. Click "New +" → "Web Service"
5. Select this repository
6. Fill in settings:
   - **Name**: `video-downloader-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Environment Variables**:
     - `BOT_TOKEN`: Paste your token from Step 1
7. Click "Create Web Service"
8. Add PostgreSQL database:
   - Click "New +" → "PostgreSQL"
   - Name: `downloader-bot-db`
9. Deploy!

### Option B: Railway (Also free)

1. Go to [railway.app](https://railway.app)
2. Create account
3. New Project → "Deploy from GitHub"
4. Select this repo
5. Add environment variables
6. Add PostgreSQL plugin
7. Deploy

### Option C: Local (For testing)

```bash
# Clone/download this repo
cd telegram-dating-bot

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export BOT_TOKEN=your_token_here
export DATABASE_URL=postgresql://localhost/downloader_bot

# Run
python bot.py
```

---

## Step 3: Test Your Bot (1 min)

1. Open Telegram
2. Search for your bot username (e.g., @my_video_downloader_bot)
3. Click "Start"
4. Try sending a YouTube link:
   ```
   https://www.youtube.com/watch?v=dQw4w9WgXcQ
   ```
5. Bot should download it! 🎉

---

## Features Overview

### Supported Platforms
✅ YouTube  
✅ TikTok  
✅ Instagram  
✅ Twitter/X  
✅ Pinterest  
✅ Facebook  
✅ Reddit  
✅ Snapchat  
✅ **500+ more!**

### User Commands
- `/start` - Main menu with options
- `/help` - Help & instructions
- Send any video URL - Download it!

### What Users See
1. Send a video link
2. Bot shows "Processing..."
3. 5-second ad break (monetization!)
4. Video is sent to them
5. Download is logged to database

---

## Monetization Setup

### Immediate (No Code Changes)
- 5-second ad breaks included ✅
- Ad impressions tracked in database ✅
- Ready for ad network integration

### Quick Wins (Add in first week)
1. **Google AdSense**
   - Go to [adsense.google.com](https://adsense.google.com)
   - Apply for publisher account
   - Get approved (usually 1-2 weeks)
   - Use your publisher ID in ads

2. **Telegram Stars** (Native Telegram Payment)
   - Already integrated in code
   - Users pay in Telegram Stars
   - You receive ~70% value

3. **Stripe Premium** (See MONETIZATION_CODE.md)
   - $2.99/month premium tier
   - Remove ads for paying users
   - Expected 2-5% conversion rate

### Projected Monthly Revenue
- **100 daily users** → $20-50
- **1,000 daily users** → $200-500
- **10,000 daily users** → $2,000-5,000
- **100,000 daily users** → $20,000-50,000

---

## Important Files

| File | Purpose |
|------|---------|
| `bot.py` | Main bot code (ready to use) |
| `requirements.txt` | Python dependencies |
| `Dockerfile` | Container deployment |
| `render.yaml` | Render.com config |
| `README.md` | Full documentation |
| `MONETIZATION.md` | Revenue strategies |
| `MONETIZATION_CODE.md` | Code examples |

---

## Troubleshooting

### Bot doesn't respond
- Check `BOT_TOKEN` is correct
- Verify environment variables are set
- Check deployment logs

### Downloads fail
- Platform may have changed structure
- Update yt-dlp: `pip install --upgrade yt-dlp`
- Try a different platform first

### Database errors
- Ensure PostgreSQL is running
- Check `DATABASE_URL` format
- Verify database exists

### Memory/timeout issues
- Render free tier: 512MB RAM
- Large videos may fail
- Add paid tier for bigger files

---

## Growth Tips

### Week 1-2: Get Users
- Post on Reddit (r/botnet, r/Telegram, etc.)
- Share on Twitter with hashtags
- List on [BotStore](https://botstore.com/)

### Week 2-4: Monetize
- Enable ads for all users
- Add premium tier
- Promote premium after 5 downloads

### Month 2-3: Optimize
- Monitor analytics
- A/B test ad content
- Improve download success rate

---

## Common Setups

### Production Setup (Recommended)
```
├── Render.com (Bot hosting)
├── PostgreSQL (Data storage)
├── Google AdSense (Ad revenue)
├── Stripe (Premium payments)
└── Analytics Dashboard
```

### Minimal Setup
```
├── Render.com (Free)
├── PostgreSQL (Free on Render)
└── Bot with ads (No payment setup needed)
```

### Advanced Setup
```
├── Multiple deployment regions
├── 5+ ad networks
├── Premium tiers + Telegram Stars
├── Affiliate programs
├── Analytics selling
└── Estimated: $5,000+/month at scale
```

---

## Next Steps

1. **Deploy** (5 minutes)
   - [ ] Get bot token from @BotFather
   - [ ] Deploy to Render/Railway
   - [ ] Test with a YouTube link

2. **Optimize** (1 week)
   - [ ] Add more ad content (MONETIZATION_CODE.md)
   - [ ] Monitor analytics
   - [ ] Fix any issues

3. **Monetize** (2 weeks)
   - [ ] Apply to Google AdSense
   - [ ] Add Stripe premium (optional)
   - [ ] Setup premium checkout

4. **Scale** (1 month+)
   - [ ] Marketing & user growth
   - [ ] More affiliates & partnerships
   - [ ] Advanced analytics

---

## Useful Commands

### View Bot Logs (Render)
Settings → Logs

### Database Access
- Use pgAdmin or SQL client
- Connection string in environment

### Monitor Revenue
```sql
SELECT 
    DATE(created_at) as date,
    COUNT(*) as impressions
FROM ad_impressions
GROUP BY date
ORDER BY date DESC;
```

---

## Support Resources

- **Telegram Bot API**: https://core.telegram.org/bots/api
- **python-telegram-bot**: https://python-telegram-bot.readthedocs.io/
- **yt-dlp**: https://github.com/yt-dlp/yt-dlp
- **Render Docs**: https://render.com/docs
- **PostgreSQL**: https://www.postgresql.org/docs/

---

## Expected Bot Stats (First 3 Months)

```
Week 1-2: 0 users (just you testing)
Week 3-4: 10-50 users
Month 2: 100-500 users
Month 3: 500-2,000 users

Revenue (if monetized correctly):
Month 1: $0-10 (testing)
Month 2: $10-50
Month 3: $50-200+
```

---

## Pro Tips

💡 **For Growth:**
- Make a YouTube video about your bot
- Create comparison graphics (YT vs Bot)
- Be active in Telegram communities
- Reply to every user inquiry quickly

💡 **For Revenue:**
- Don't be too aggressive with ads
- Premium should feel worth it
- A/B test different price points
- Track what's working

💡 **For Quality:**
- Keep bot responsive
- Fix issues quickly
- Update yt-dlp regularly
- Monitor platform changes

---

## One-Click Deployment (Copy & Paste)

### Environment Variables to Set:
```
BOT_TOKEN=your_token_here
DATABASE_URL=your_postgres_connection_string
```

### That's it! Your bot will:
✅ Download from 500+ platforms
✅ Show ads (monetization)
✅ Track analytics
✅ Support premium users
✅ Ready to scale to $1000s/month

---

**You're all set! Deploy now and start earning! 🚀**

Questions? Check README.md and MONETIZATION.md for detailed guides.
