import os
import logging
import json
import time
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import yt_dlp
import requests

# Try to import psycopg2 (optional)
try:
    import psycopg2
    from psycopg2 import pool
    HAS_DATABASE = True
except ImportError:
    HAS_DATABASE = False

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get environment variables
TOKEN = os.environ.get('BOT_TOKEN')
DATABASE_URL = os.environ.get('DATABASE_URL')

# Database connection pool
db_pool = None

def init_pool():
    """Initialize database connection pool"""
    global db_pool
    if not HAS_DATABASE:
        logger.warning("psycopg2 not installed. Running without database.")
        return
    
    try:
        if DATABASE_URL:
            db_pool = psycopg2.pool.SimpleConnectionPool(1, 10, DATABASE_URL)
            logger.info("Database pool created successfully")
    except Exception as e:
        logger.error(f"Error creating connection pool: {e}")
        logger.warning("Database unavailable. Bot will work without logging.")

def get_db():
    """Get connection from pool"""
    if not db_pool:
        return None
    try:
        return db_pool.getconn()
    except Exception as e:
        logger.error(f"Error getting connection: {e}")
        return None

def return_db(conn):
    """Return connection to pool"""
    if conn and db_pool:
        try:
            db_pool.putconn(conn)
        except Exception as e:
            logger.error(f"Error returning connection: {e}")

# Initialize database
def init_db():
    """Create necessary tables"""
    if not db_pool:
        return
    
    conn = get_db()
    if not conn:
        return
        
    try:
        cur = conn.cursor()
        
        # Users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id BIGINT PRIMARY KEY,
                username VARCHAR(100),
                first_name VARCHAR(100),
                is_premium BOOLEAN DEFAULT false,
                downloads_count INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Downloads history
        cur.execute("""
            CREATE TABLE IF NOT EXISTS downloads (
                download_id SERIAL PRIMARY KEY,
                user_id BIGINT,
                platform VARCHAR(50),
                url TEXT,
                title VARCHAR(255),
                file_id VARCHAR(255),
                saw_ad BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY(user_id) REFERENCES users(telegram_id)
            )
        """)
        
        # Ad impressions for monetization tracking
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ad_impressions (
                impression_id SERIAL PRIMARY KEY,
                user_id BIGINT,
                ad_content VARCHAR(255),
                clicked BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY(user_id) REFERENCES users(telegram_id)
            )
        """)
        
        conn.commit()
        logger.info("Database initialized successfully!")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        return_db(conn)

def get_or_create_user(telegram_id, username, first_name):
    """Get or create user in database"""
    if not db_pool:
        return
    
    conn = get_db()
    if not conn:
        return
        
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (telegram_id, username, first_name)
            VALUES (%s, %s, %s)
            ON CONFLICT (telegram_id) DO UPDATE SET
                username = EXCLUDED.username,
                first_name = EXCLUDED.first_name
            RETURNING is_premium
        """, (telegram_id, username, first_name))
        
        result = cur.fetchone()
        conn.commit()
        return result
    except Exception as e:
        logger.error(f"Error managing user: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        return_db(conn)

def log_download(user_id, platform, url, title):
    """Log a download"""
    if not db_pool:
        return
    
    conn = get_db()
    if not conn:
        return
        
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO downloads (user_id, platform, url, title, saw_ad)
            VALUES (%s, %s, %s, %s, false)
        """, (user_id, platform, url, title))
        
        cur.execute("UPDATE users SET downloads_count = downloads_count + 1 WHERE telegram_id = %s", (user_id,))
        conn.commit()
    except Exception as e:
        logger.error(f"Error logging download: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        return_db(conn)

def log_ad_impression(user_id, ad_content):
    """Log ad impression for monetization"""
    if not db_pool:
        return
    
    conn = get_db()
    if not conn:
        return
        
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO ad_impressions (user_id, ad_content)
            VALUES (%s, %s)
        """, (user_id, ad_content))
        conn.commit()
    except Exception as e:
        logger.error(f"Error logging ad: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        return_db(conn)

# Video downloader functions
class VideoDownloader:
    """Handles video downloading from various platforms"""
    
    @staticmethod
    def get_platform(url):
        """Detect platform from URL"""
        url_lower = url.lower()
        if 'youtube' in url_lower or 'youtu.be' in url_lower:
            return 'youtube'
        elif 'tiktok' in url_lower or 'vm.tiktok' in url_lower or 'vt.tiktok' in url_lower:
            return 'tiktok'
        elif 'instagram' in url_lower or 'instagr' in url_lower:
            return 'instagram'
        elif 'twitter' in url_lower or 'x.com' in url_lower:
            return 'twitter'
        elif 'pinterest' in url_lower:
            return 'pinterest'
        elif 'facebook' in url_lower or 'fb.watch' in url_lower:
            return 'facebook'
        elif 'reddit' in url_lower:
            return 'reddit'
        elif 'snapchat' in url_lower:
            return 'snapchat'
        else:
            return 'unknown'
    
    @staticmethod
    def download_with_yt_dlp(url):
        """Download video using yt-dlp"""
        try:
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': '/tmp/%(title)s.%(ext)s',
                'quiet': False,
                'no_warnings': False,
                'socket_timeout': 60,  # Increased from 30
                'http_chunk_size': 10485760,  # 10MB chunks
                'retries': 3,
                'fragment_retries': 3,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                title = info.get('title', 'Video')
                return {
                    'success': True,
                    'file_path': file_path,
                    'title': title,
                    'duration': info.get('duration', 0)
                }
        except Exception as e:
            logger.error(f"yt-dlp error: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    async def download_video(url):
        """Main download function"""
        platform = VideoDownloader.get_platform(url)
        
        try:
            result = await asyncio.to_thread(
                VideoDownloader.download_with_yt_dlp, url
            )
            if result['success']:
                result['platform'] = platform
                return result
            else:
                return {'success': False, 'error': f"Failed to download from {platform}"}
        except Exception as e:
            logger.error(f"Download error: {e}")
            return {'success': False, 'error': str(e)}

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    user = update.effective_user
    get_or_create_user(user.id, user.username, user.first_name)
    
    keyboard = [
        [InlineKeyboardButton("📥 Download Video", callback_data='start_download')],
        [InlineKeyboardButton("📊 My Stats", callback_data='stats')],
        [InlineKeyboardButton("ℹ️ Supported Platforms", callback_data='platforms')],
        [InlineKeyboardButton("⭐ Premium", callback_data='premium')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🎬 **Welcome to Video Downloader Bot!**\n\n"
        f"Hi {user.first_name}! Download videos from your favorite platforms:\n"
        f"✅ YouTube\n"
        f"✅ TikTok\n"
        f"✅ Instagram\n"
        f"✅ Twitter/X\n"
        f"✅ Pinterest\n"
        f"✅ Facebook & More!\n\n"
        f"Just send me a video link and I'll download it for you!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = """
🎬 **Video Downloader Bot - Help**

**How to use:**
1. Send any video link from supported platforms
2. Wait for processing
3. Receive the downloaded video

**Supported Platforms:**
• YouTube
• TikTok
• Instagram (Reels, Posts, Videos)
• Twitter/X
• Pinterest
• Facebook
• Reddit
• Snapchat
• And many more!

**Features:**
• Fast downloads
• High quality video
• Multiple platform support
• Download history tracking
• Premium features available

**Tips:**
• For best results, send direct links
• Large videos may take longer
• Premium members get priority processing

Send /start to go back to menu
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle URL messages"""
    user = update.effective_user
    url = update.message.text.strip()
    
    # Check if it's a URL
    if not (url.startswith('http://') or url.startswith('https://')):
        await update.message.reply_text(
            "Please send a valid video link (starting with http:// or https://)"
        )
        return
    
    # Show processing message
    processing_msg = await update.message.reply_text("🔄 Processing your video... Please wait")
    
    try:
        # Download video
        result = await VideoDownloader.download_video(url)
        
        if not result['success']:
            await processing_msg.edit_text(f"❌ Error: {result['error']}")
            return
        
        # Log download
        log_download(user.id, result['platform'], url, result.get('title', 'Video'))
        
        # Show ad before sending video (monetization)
        await show_ad_and_download(update, context, result, processing_msg)
        
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await processing_msg.edit_text(f"❌ Error: {str(e)}")

async def show_ad_and_download(update: Update, context: ContextTypes.DEFAULT_TYPE, result, processing_msg):
    """Show 5-second ad then send video"""
    user = update.effective_user
    
    # Show ad message
    ad_text = """
    🎯 **Quick Ad Break!** ⏱️
    
    Watch for 5 seconds...
    
    [AD] Check out Premium features for faster downloads!
    Upgrade now to remove ads and get priority downloads.
    
    ⭐ **Premium Benefits:**
    • No ads
    • 4K downloads
    • Priority processing
    • Unlimited downloads
    
    Continuing in 5 seconds...
    """
    
    await processing_msg.edit_text(ad_text, parse_mode='Markdown')
    log_ad_impression(user.id, "Video Download - Standard")
    
    # Wait 5 seconds
    await asyncio.sleep(5)
    
    # Send video
    try:
        with open(result['file_path'], 'rb') as video_file:
            await update.effective_chat.send_video(
                video=video_file,
                caption=f"✅ {result.get('title', 'Video')}\n\n📱 Platform: {result.get('platform', 'Unknown').upper()}"
            )
        
        await processing_msg.delete()
        
        # Cleanup temp file
        import os
        try:
            os.remove(result['file_path'])
        except:
            pass
            
    except Exception as e:
        logger.error(f"Error sending video: {e}")
        await processing_msg.edit_text(f"❌ Failed to send video: {str(e)}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'start_download':
        await query.edit_message_text(
            "📤 Send me a video link from any of these platforms:\n\n"
            "🎥 YouTube\n"
            "🎵 TikTok\n"
            "📸 Instagram\n"
            "🐦 Twitter/X\n"
            "🎨 Pinterest\n"
            "👥 Facebook\n"
            "🔗 Reddit\n"
            "👻 Snapchat\n\n"
            "Just copy and paste the link here!"
        )
    
    elif query.data == 'stats':
        user_id = update.effective_user.id
        conn = get_db()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT downloads_count, created_at FROM users WHERE telegram_id = %s", (user_id,))
                result = cur.fetchone()
                if result:
                    downloads, created = result
                    days = (datetime.now() - created).days + 1
                    await query.edit_message_text(
                        f"📊 **Your Stats**\n\n"
                        f"📥 Total Downloads: {downloads}\n"
                        f"📅 Member for: {days} days\n"
                        f"⚡ Average: {downloads / days:.1f} per day",
                        parse_mode='Markdown'
                    )
                cur.close()
            finally:
                return_db(conn)
    
    elif query.data == 'platforms':
        await query.edit_message_text(
            "✅ **Supported Platforms:**\n\n"
            "🔴 YouTube - Full videos & shorts\n"
            "🎵 TikTok - Videos & sounds\n"
            "📸 Instagram - Reels, posts, stories\n"
            "🐦 Twitter/X - Videos & gifs\n"
            "🎨 Pinterest - Pins & videos\n"
            "👥 Facebook - Posts & videos\n"
            "🔗 Reddit - Videos & gifs\n"
            "👻 Snapchat - Snaps\n"
            "🎬 And 500+ other sites!\n\n"
            "Just send the link!",
            parse_mode='Markdown'
        )
    
    elif query.data == 'premium':
        await query.edit_message_text(
            "⭐ **Premium Membership** ⭐\n\n"
            "**Benefits:**\n"
            "✅ No ads\n"
            "✅ 4K/8K video quality\n"
            "✅ Priority fast processing\n"
            "✅ Unlimited downloads\n"
            "✅ Direct MP3 conversion\n"
            "✅ Batch downloads\n\n"
            "💳 Coming soon with payment integration!\n"
            "Contact: @Homogenous_bot",
            parse_mode='Markdown'
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Error handler"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Start the bot"""
    # Initialize database
    init_pool()
    init_db()
    
    if not TOKEN:
        logger.error("BOT_TOKEN not found in environment variables")
        return
    
    # Create application with longer timeout for downloads
    application = Application.builder().token(TOKEN).read_timeout(120).write_timeout(120).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("Bot started successfully!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

