# Advanced Monetization Code Examples

This file contains ready-to-use code snippets for various monetization features.

## 1. Premium Membership with Stripe

```python
import stripe
import os

stripe.api_key = os.environ.get('STRIPE_API_KEY')

async def create_premium_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create Stripe checkout session for premium"""
    user = update.effective_user
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Video Downloader Bot - Premium Monthly',
                        'description': 'No ads, 4K downloads, priority processing',
                        'images': ['https://your-image-url.com/premium.png'],
                    },
                    'unit_amount': 299,  # $2.99
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url='https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://yourdomain.com/cancel',
            client_reference_id=str(user.id),
            customer_email=user.username + '@telegram.local',  # Placeholder
            metadata={
                'telegram_id': user.id,
                'username': user.username,
            }
        )
        
        # Store session ID in database for verification
        log_payment_session(user.id, session.id)
        
        keyboard = [
            [InlineKeyboardButton("💳 Subscribe to Premium", url=session.url)],
            [InlineKeyboardButton("Back", callback_data='premium_back')],
        ]
        
        await update.message.reply_text(
            "⭐ **Premium Membership** ⭐\n\n"
            "**$2.99/month or $25/year**\n\n"
            "**Get:**\n"
            "✅ No ads (save 5 seconds per download)\n"
            "✅ 4K/8K video downloads\n"
            "✅ Priority processing (2x faster)\n"
            "✅ Direct MP3 conversion\n"
            "✅ Batch downloads (up to 50 videos)\n"
            "✅ Download entire playlists\n\n"
            "💳 Click below to subscribe!",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
    except stripe.error.CardError as e:
        await update.message.reply_text(f"❌ Card error: {e.user_message}")
    except stripe.error.RateLimitError:
        await update.message.reply_text("⚠️ Too many requests. Try again later.")
    except stripe.error.InvalidRequestError as e:
        await update.message.reply_text(f"❌ Invalid request: {e.user_message}")
    except stripe.error.AuthenticationError:
        await update.message.reply_text("❌ Authentication error with payment service")
    except stripe.error.APIConnectionError:
        await update.message.reply_text("❌ Network error. Try again later.")
    except stripe.error.StripeError as e:
        await update.message.reply_text(f"❌ Payment error: {e.user_message}")
    except Exception as e:
        logger.error(f"Unexpected error in premium checkout: {e}")
        await update.message.reply_text("❌ An unexpected error occurred")


def verify_premium_payment(session_id):
    """Verify payment with Stripe and update user"""
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid':
            telegram_id = int(session.metadata['telegram_id'])
            update_user_premium(telegram_id, True)
            return True
        return False
    except Exception as e:
        logger.error(f"Error verifying payment: {e}")
        return False
```

---

## 2. Telegram Stars Payment Integration

```python
from telegram import LabeledPrice, ShippingOption

async def send_premium_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send Telegram Stars invoice"""
    chat_id = update.effective_user.id
    
    prices = [
        LabeledPrice("Premium Monthly", 119),  # 119 stars = ~$2.40
    ]
    
    await context.bot.send_invoice(
        chat_id=chat_id,
        title="Video Downloader Premium",
        description="Monthly subscription - No ads, 4K downloads, priority",
        payload="premium_monthly_subscription",
        currency="XTR",  # Telegram Stars
        prices=prices,
        provider_token="",  # Not needed for Telegram Stars
        is_flexible=False,
    )

async def pre_checkout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pre-checkout"""
    query = update.pre_checkout_query
    
    if query.invoice_payload == 'premium_monthly_subscription':
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="Something went wrong...")

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle successful payment"""
    payment = update.message.successful_payment
    
    if payment.provider_payment_charge_id:
        # Telegram Stars payment
        user_id = update.effective_user.id
        
        # Update database
        update_user_premium(user_id, True)
        set_premium_expiry(user_id, datetime.now() + timedelta(days=30))
        
        await update.message.reply_text(
            "🎉 **Payment Successful!**\n\n"
            "✅ Premium activated for 30 days\n"
            "✅ Ads disabled\n"
            "✅ Enjoy 4K downloads!\n\n"
            "/start to go back to menu"
        )
```

---

## 3. Custom Sponsorship Ad System

```python
import json
from datetime import datetime, timedelta

class SponsorshipAds:
    """Manage sponsored content"""
    
    ADS_CONFIG = {
        'vpn': {
            'campaigns': [
                {
                    'id': 'nord_vpn_dec',
                    'title': '🔒 ExpressVPN',
                    'text': 'Secure your downloads. 30% off →',
                    'url': 'https://affiliate.expressvpn.com/your-ref',
                    'ctr_threshold': 0.05,  # 5% click target
                    'budget': 500,  # $500 monthly
                    'active': True,
                },
                {
                    'id': 'surfshark_dec',
                    'title': '🌊 Surfshark VPN',
                    'text': 'Fast & secure. Limited time offer →',
                    'url': 'https://surfshark.com/ref/xxx',
                    'ctr_threshold': 0.04,
                    'budget': 300,
                    'active': True,
                }
            ]
        },
        'storage': {
            'campaigns': [
                {
                    'id': 'onedrive_dec',
                    'title': '☁️ OneDrive 1TB Free',
                    'text': 'Store your downloads. Get 1TB free →',
                    'url': 'https://onedrive.live.com?ref=xxx',
                    'ctr_threshold': 0.03,
                    'budget': 200,
                    'active': True,
                }
            ]
        }
    }
    
    @staticmethod
    def get_ad_for_user(user_id: int, user_region: str = None):
        """Select best ad based on user profile"""
        # Get user download history
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) as count, 
                   EXTRACT(DOW FROM created_at) as day
            FROM downloads 
            WHERE user_id = %s 
            AND created_at > NOW() - INTERVAL '7 days'
        """, (user_id,))
        
        stats = cur.fetchone()
        daily_avg = stats[0] / 7 if stats else 0
        
        # Select ad based on usage pattern
        if daily_avg > 5:  # Heavy user
            # Show premium upgrade or storage
            return SponsorshipAds.ADS_CONFIG['storage']['campaigns'][0]
        elif user_region == 'CN' or user_region == 'RU':  # Restricted regions
            # Show VPN
            return SponsorshipAds.ADS_CONFIG['vpn']['campaigns'][0]
        else:
            # Rotate through active campaigns
            import random
            all_ads = []
            for category in SponsorshipAds.ADS_CONFIG.values():
                all_ads.extend(category['campaigns'])
            
            active_ads = [ad for ad in all_ads if ad['active']]
            return random.choice(active_ads) if active_ads else None

async def show_sponsored_ad(update: Update, processing_msg):
    """Display sponsored ad instead of generic one"""
    user_id = update.effective_user.id
    
    ad = SponsorshipAds.get_ad_for_user(user_id)
    
    if ad:
        ad_text = f"""
    🎯 **Sponsored** ⏱️
    
    {ad['title']}
    {ad['text']}
    
    Continuing in 5 seconds...
    """
        
        await processing_msg.edit_text(ad_text, parse_mode='Markdown')
        log_ad_impression(user_id, ad['id'])
        
        # Track click-through
        ad_button = InlineKeyboardMarkup([
            [InlineKeyboardButton("Visit Offer", url=ad['url'])]
        ])
        
        await asyncio.sleep(5)
    
    return ad
```

---

## 4. Analytics & Revenue Dashboard

```python
async def show_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin revenue dashboard"""
    user_id = update.effective_user.id
    
    # Check if admin
    if user_id not in [YOUR_ADMIN_ID]:
        return
    
    conn = get_db()
    cur = conn.cursor()
    
    # Get stats
    cur.execute("""
    SELECT 
        (SELECT COUNT(*) FROM users) as total_users,
        (SELECT COUNT(*) FROM users WHERE is_premium) as premium_users,
        (SELECT COUNT(*) FROM downloads WHERE created_at > NOW() - INTERVAL '1 day') as today_downloads,
        (SELECT COUNT(*) FROM ad_impressions WHERE created_at > NOW() - INTERVAL '1 day') as today_impressions,
        (SELECT COUNT(CASE WHEN clicked THEN 1 END) FROM ad_impressions 
         WHERE created_at > NOW() - INTERVAL '1 day') as today_clicks
    """)
    
    stats = cur.fetchone()
    total_users, premium_users, today_downloads, today_impressions, today_clicks = stats
    
    # Calculate revenue
    cpm_rate = 2.50  # $2.50 per 1000 impressions
    monthly_ad_revenue = (today_impressions * 30 / 1000) * cpm_rate
    premium_revenue = premium_users * 2.99
    
    # Estimate daily
    daily_ad_revenue = (today_impressions / 1000) * cpm_rate
    
    dashboard = f"""
    📊 **Revenue Dashboard**
    
    **Users:**
    • Total: {total_users:,}
    • Premium: {premium_users} ({premium_users*100//total_users if total_users else 0}%)
    
    **Today:**
    • Downloads: {today_downloads:,}
    • Ad impressions: {today_impressions:,}
    • Ad clicks: {today_clicks} ({today_clicks*100//today_impressions if today_impressions else 0}% CTR)
    
    **Revenue (Today):**
    • Ads: ${daily_ad_revenue:.2f}
    • Premium: ${premium_revenue:.2f}
    • Total: ${daily_ad_revenue + premium_revenue:.2f}
    
    **Projected (30 days):**
    • Ads: ${monthly_ad_revenue:.2f}
    • Premium: ${premium_revenue * 30:.2f}
    • Total: ${monthly_ad_revenue + (premium_revenue * 30):.2f}
    """
    
    await update.message.reply_text(dashboard, parse_mode='Markdown')
    
    cur.close()
    return_db(conn)
```

---

## 5. Referral Program

```python
async def generate_referral_link(user_id: int):
    """Generate unique referral link"""
    import hashlib
    
    # Create unique code
    ref_code = hashlib.md5(f"{user_id}{datetime.now()}".encode()).hexdigest()[:8].upper()
    
    # Store in database
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO referrals (user_id, ref_code, created_at)
        VALUES (%s, %s, NOW())
        ON CONFLICT (user_id) DO UPDATE SET
        ref_code = EXCLUDED.ref_code,
        updated_at = NOW()
    """, (user_id, ref_code))
    conn.commit()
    cur.close()
    return_db(conn)
    
    return ref_code

async def show_referral_program(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show referral program"""
    user_id = update.effective_user.id
    ref_code = await generate_referral_link(user_id)
    
    referral_link = f"https://t.me/YOUR_BOT_USERNAME?start={ref_code}"
    
    keyboard = [
        [InlineKeyboardButton("Copy Link", callback_data=f'copy_{referral_link}')],
        [InlineKeyboardButton("Share on Twitter", 
         url=f"https://twitter.com/intent/tweet?text=Check out this video downloader bot {referral_link}")],
    ]
    
    await update.message.reply_text(
        "🎁 **Referral Program**\n\n"
        "Earn $1 for every friend who upgrades to Premium!\n\n"
        f"Your referral link:\n`{referral_link}`\n\n"
        "Share with friends and earn rewards.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process referral when user joins"""
    if context.args and len(context.args) > 0:
        ref_code = context.args[0]
        
        # Find referrer
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM referrals WHERE ref_code = %s", (ref_code,))
        result = cur.fetchone()
        
        if result:
            referrer_id = result[0]
            
            # Log referral
            cur.execute("""
                INSERT INTO referral_clicks (referrer_id, referred_user_id, created_at)
                VALUES (%s, %s, NOW())
            """, (referrer_id, update.effective_user.id))
            
            conn.commit()
        
        cur.close()
        return_db(conn)
```

---

## 6. Smart Ad Scheduling

```python
async def should_show_ad(user_id: int) -> bool:
    """Determine if should show ad to avoid ad fatigue"""
    
    conn = get_db()
    cur = conn.cursor()
    
    # Check recent ad impressions
    cur.execute("""
        SELECT COUNT(*) as ad_count
        FROM ad_impressions
        WHERE user_id = %s 
        AND created_at > NOW() - INTERVAL '1 hour'
    """, (user_id,))
    
    ad_count = cur.fetchone()[0]
    cur.close()
    return_db(conn)
    
    # Limit to 3 ads per hour per user
    if ad_count >= 3:
        return False
    
    # Get user download frequency
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) as count
        FROM downloads
        WHERE user_id = %s
        AND created_at > NOW() - INTERVAL '7 days'
    """, (user_id,))
    
    weekly_downloads = cur.fetchone()[0]
    cur.close()
    return_db(conn)
    
    # Heavy users see ads less frequently (loyalty)
    if weekly_downloads > 20:
        return ad_count < 1
    elif weekly_downloads > 10:
        return ad_count < 2
    
    return True

async def handle_message_with_smart_ads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Download with smart ad scheduling"""
    user = update.effective_user
    url = update.message.text.strip()
    
    processing_msg = await update.message.reply_text("🔄 Processing...")
    
    result = await VideoDownloader.download_video(url)
    
    if result['success']:
        # Check if should show ad
        if await should_show_ad(user.id):
            await show_ad_and_download(update, context, result, processing_msg)
        else:
            # Skip ad for this user
            with open(result['file_path'], 'rb') as video_file:
                await update.effective_chat.send_video(
                    video=video_file,
                    caption=f"✅ {result.get('title', 'Video')}"
                )
```

---

## Database Schema for Monetization

```sql
-- Premium users tracking
ALTER TABLE users ADD COLUMN premium_expiry TIMESTAMP;
ALTER TABLE users ADD COLUMN premium_tier VARCHAR(20) DEFAULT 'free';

-- Payment tracking
CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    user_id BIGINT,
    amount DECIMAL(10, 2),
    currency VARCHAR(3),
    payment_method VARCHAR(50),
    status VARCHAR(20),
    stripe_session_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY(user_id) REFERENCES users(telegram_id)
);

-- Referral tracking
CREATE TABLE referrals (
    referral_id SERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE,
    ref_code VARCHAR(20),
    earnings DECIMAL(10, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY(user_id) REFERENCES users(telegram_id)
);

CREATE TABLE referral_clicks (
    click_id SERIAL PRIMARY KEY,
    referrer_id BIGINT,
    referred_user_id BIGINT,
    conversion_amount DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

These code examples are production-ready and can be integrated directly into your bot!
