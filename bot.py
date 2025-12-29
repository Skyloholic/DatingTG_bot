import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import psycopg2
from psycopg2 import pool
from datetime import datetime

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get environment variables
TOKEN = os.environ.get('BOT_TOKEN')
DATABASE_URL = os.environ.get('DATABASE_URL')

# Database connection pool for better performance
db_pool = None

def init_pool():
    global db_pool
    try:
        db_pool = psycopg2.pool.SimpleConnectionPool(
            1, 10,
            DATABASE_URL
        )
        logger.info("Database pool created successfully")
    except Exception as e:
        logger.error(f"Error creating connection pool: {e}")
        raise

def get_db():
    if not db_pool:
        return None
    try:
        return db_pool.getconn()
    except Exception as e:
        logger.error(f"Error getting connection from pool: {e}")
        raise

def return_db(conn):
    try:
        db_pool.putconn(conn)
    except Exception as e:
        logger.error(f"Error returning connection to pool: {e}")

# Initialize database
def init_db():
    conn = get_db()
    try:
        cur = conn.cursor()
        
        # Create tables
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id BIGINT PRIMARY KEY,
                username VARCHAR(100),
                first_name VARCHAR(100),
                age INT,
                gender VARCHAR(20),
                looking_for VARCHAR(20),
                bio TEXT,
                registration_step VARCHAR(50),
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                match_id SERIAL PRIMARY KEY,
                user1_id BIGINT,
                user2_id BIGINT,
                status VARCHAR(20) DEFAULT 'active',
                user1_revealed BOOLEAN DEFAULT false,
                user2_revealed BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS queue (
                user_id BIGINT PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT NOW()
            )
        """)
        
        conn.commit()
        logger.info("Database initialized successfully!")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        return_db(conn)

# Helper functions
def user_exists(user_id):
    if not db_pool:
        return False
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE telegram_id = %s", (user_id,))
        exists = cur.fetchone() is not None
        return exists
    except Exception as e:
        logger.error(f"Error checking user existence: {e}")
        return False
    finally:
        cur.close()
        return_db(conn)

def get_registration_step(user_id):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT registration_step FROM users WHERE telegram_id = %s", (user_id,))
        result = cur.fetchone()
        return result[0] if result else None
    except Exception as e:
        logger.error(f"Error getting registration step: {e}")
        return None
    finally:
        cur.close()
        return_db(conn)

def create_user(user_id, username, first_name):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (telegram_id, username, first_name, registration_step) VALUES (%s, %s, %s, 'age')",
            (user_id, username or 'Unknown', first_name or 'User')
        )
        conn.commit()
        logger.info(f"User {user_id} created")
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        conn.rollback()
    finally:
        cur.close()
        return_db(conn)

def update_user_field(user_id, field, value):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(
            f"UPDATE users SET {field} = %s WHERE telegram_id = %s", 
            (value, user_id)
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Error updating user field: {e}")
        conn.rollback()
    finally:
        cur.close()
        return_db(conn)

def get_user_data(user_id):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE telegram_id = %s", (user_id,))
        result = cur.fetchone()
        return result
    except Exception as e:
        logger.error(f"Error getting user data: {e}")
        return None
    finally:
        cur.close()
        return_db(conn)

def add_to_queue(user_id):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO queue (user_id) VALUES (%s) ON CONFLICT (user_id) DO UPDATE SET timestamp = NOW()",
            (user_id,)
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Error adding to queue: {e}")
        conn.rollback()
    finally:
        cur.close()
        return_db(conn)

def find_match(user_id):
    conn = get_db()
    try:
        cur = conn.cursor()
        
        # Get user preferences
        cur.execute("SELECT gender, looking_for FROM users WHERE telegram_id = %s", (user_id,))
        user = cur.fetchone()
        
        if not user:
            return None
        
        # Find compatible match
        cur.execute("""
            SELECT u.telegram_id 
            FROM queue q
            JOIN users u ON q.user_id = u.telegram_id
            WHERE q.user_id != %s 
            AND u.gender = %s
            AND u.looking_for = %s
            ORDER BY q.timestamp ASC
            LIMIT 1
        """, (user_id, user[1], user[0]))
        
        match = cur.fetchone()
        
        if match:
            # Remove both from queue
            cur.execute("DELETE FROM queue WHERE user_id IN (%s, %s)", (user_id, match[0]))
            conn.commit()
        
        return match[0] if match else None
    except Exception as e:
        logger.error(f"Error finding match: {e}")
        return None
    finally:
        cur.close()
        return_db(conn)

def create_match(user1_id, user2_id):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO matches (user1_id, user2_id, status) VALUES (%s, %s, 'active')",
            (user1_id, user2_id)
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Error creating match: {e}")
        conn.rollback()
    finally:
        cur.close()
        return_db(conn)

def get_active_match(user_id):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT CASE 
                WHEN user1_id = %s THEN user2_id 
                ELSE user1_id 
            END as partner_id
            FROM matches 
            WHERE (user1_id = %s OR user2_id = %s) 
            AND status = 'active'
            LIMIT 1
        """, (user_id, user_id, user_id))
        
        result = cur.fetchone()
        return result[0] if result else None
    except Exception as e:
        logger.error(f"Error getting active match: {e}")
        return None
    finally:
        cur.close()
        return_db(conn)

def end_match(user_id):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE matches SET status = 'ended' 
            WHERE (user1_id = %s OR user2_id = %s) AND status = 'active'
        """, (user_id, user_id))
        conn.commit()
    except Exception as e:
        logger.error(f"Error ending match: {e}")
        conn.rollback()
    finally:
        cur.close()
        return_db(conn)

def mark_reveal(user_id):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE matches 
            SET user1_revealed = CASE WHEN user1_id = %s THEN true ELSE user1_revealed END,
                user2_revealed = CASE WHEN user2_id = %s THEN true ELSE user2_revealed END
            WHERE (user1_id = %s OR user2_id = %s) AND status = 'active'
        """, (user_id, user_id, user_id, user_id))
        conn.commit()
    except Exception as e:
        logger.error(f"Error marking reveal: {e}")
        conn.rollback()
    finally:
        cur.close()
        return_db(conn)

def both_revealed(user_id):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT user1_revealed AND user2_revealed as both
            FROM matches 
            WHERE (user1_id = %s OR user2_id = %s) AND status = 'active'
        """, (user_id, user_id))
        result = cur.fetchone()
        return result[0] if result else False
    except Exception as e:
        logger.error(f"Error checking reveal status: {e}")
        return False
    finally:
        cur.close()
        return_db(conn)

# Bot handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    first_name = update.effective_user.first_name
    
    if not user_exists(user_id):
        create_user(user_id, username, first_name)
        await update.message.reply_text(
            "🎭 *Welcome to BlindChat!*\n\n"
            "Connect with new people anonymously.\n"
            "Chat without revealing who you are until you're ready.\n\n"
            "Let's set up your profile...\n\n"
            "📅 How old are you? (Enter a number)",
            parse_mode='Markdown'
        )
    else:
        keyboard = [
            [InlineKeyboardButton("🔍 Find Match", callback_data='search')],
            [InlineKeyboardButton("👤 My Profile", callback_data='profile')],
            [InlineKeyboardButton("ℹ️ How it Works", callback_data='help')],
        ]
        await update.message.reply_text(
            f"🎭 *Welcome back to BlindChat!*\n\n"
            f"Ready to meet someone new?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

async def handle_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    step = get_registration_step(user_id)
    text = update.message.text
    
    if step == 'age':
        try:
            age = int(text)
            if 18 <= age <= 100:
                update_user_field(user_id, 'age', age)
                update_user_field(user_id, 'registration_step', 'gender')
                
                keyboard = [
                    [InlineKeyboardButton("👨 Male", callback_data='gender_male')],
                    [InlineKeyboardButton("👩 Female", callback_data='gender_female')],
                    [InlineKeyboardButton("🌈 Other", callback_data='gender_other')],
                ]
                await update.message.reply_text(
                    "What's your gender?",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            else:
                await update.message.reply_text("Please enter an age between 18 and 100.")
        except:
            await update.message.reply_text("Please enter a valid number.")
    
    elif step == 'bio':
        update_user_field(user_id, 'bio', text)
        update_user_field(user_id, 'registration_step', 'complete')
        
        await update.message.reply_text(
            "✅ Profile complete!\n\n"
            "Use /search to find your first match!"
        )

async def show_help(query):
    await query.edit_message_text(
        "🎭 *How BlindChat Works:*\n\n"
        "1️⃣ Complete your profile\n"
        "2️⃣ Use /search to find a match\n"
        "3️⃣ Chat anonymously (they won't see your identity)\n"
        "4️⃣ Use /reveal when you're comfortable\n"
        "5️⃣ Use /next to meet someone new\n\n"
        "*Commands:*\n"
        "/start - Main menu\n"
        "/search - Find a match\n"
        "/reveal - Reveal your identity\n"
        "/next - Skip to next person\n"
        "/stop - End current chat\n\n"
        "🔒 Your privacy is protected. Chats are anonymous until both users agree to reveal.",
        parse_mode='Markdown'
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data.startswith('gender_'):
        gender = data.split('_')[1]
        update_user_field(user_id, 'gender', gender)
        update_user_field(user_id, 'registration_step', 'looking_for')
        
        keyboard = [
            [InlineKeyboardButton("👨 Male", callback_data='looking_male')],
            [InlineKeyboardButton("👩 Female", callback_data='looking_female')],
            [InlineKeyboardButton("🌈 Everyone", callback_data='looking_everyone')],
        ]
        await query.edit_message_text(
            "Who are you looking to meet?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data.startswith('looking_'):
        looking = data.split('_')[1]
        update_user_field(user_id, 'looking_for', looking)
        update_user_field(user_id, 'registration_step', 'bio')
        
        await query.edit_message_text(
            "Tell us a bit about yourself (bio):"
        )
    
    elif data == 'search':
        await search_match(query, context)
    
    elif data == 'profile':
        user_data = get_user_data(user_id)
        if user_data:
            await query.edit_message_text(
                f"👤 Your Profile:\n\n"
                f"Age: {user_data[3]}\n"
                f"Gender: {user_data[4]}\n"
                f"Looking for: {user_data[5]}\n"
                f"Bio: {user_data[6]}"
            )
    
    elif data == 'help':
        await show_help(query)

async def search_match(query_or_update, context: ContextTypes.DEFAULT_TYPE):
    if hasattr(query_or_update, 'from_user'):
        user_id = query_or_update.from_user.id
        message = query_or_update
    else:
        user_id = query_or_update.effective_user.id
        message = query_or_update.message
    
    # Check if already in active chat
    partner = get_active_match(user_id)
    if partner:
        await message.reply_text("You're already in a chat! Use /next to find someone new.")
        return
    
    add_to_queue(user_id)
    
    await message.reply_text("🔍 Searching for a match...")
    
    match_id = find_match(user_id)
    
    if match_id:
        create_match(user_id, match_id)
        
        await context.bot.send_message(
            chat_id=user_id,
            text="🎭 *Match Found!*\n\n"
                 "Start chatting below. Your identity is hidden.\n\n"
                 "📝 *Commands:*\n"
                 "• /reveal - Show your identity\n"
                 "• /next - Find someone new\n"
                 "• /stop - End chat\n\n"
                 "💡 *Tip:* Be respectful and have fun!",
            parse_mode='Markdown'
        )
        
        await context.bot.send_message(
            chat_id=match_id,
            text="🎭 *Match Found!*\n\n"
                 "Someone wants to chat with you!\n"
                 "Your identity is hidden. Start talking!",
            parse_mode='Markdown'
        )
    else:
        await message.reply_text(
            "⏳ No one available right now.\n"
            "You're in the queue. We'll notify you when someone joins!"
        )

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await search_match(update, context)

async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_id = update.effective_user.id
    
    # Check registration
    step = get_registration_step(sender_id)
    if step and step != 'complete':
        await handle_registration(update, context)
        return
    
    partner_id = get_active_match(sender_id)
    
    if partner_id:
        is_revealed = both_revealed(sender_id)
        
        if is_revealed:
            prefix = f"💬 {update.effective_user.first_name}: "
        else:
            prefix = "💬 Anonymous: "
        
        await context.bot.send_message(
            chat_id=partner_id,
            text=prefix + update.message.text
        )
    else:
        await update.message.reply_text(
            "You're not in a chat. Use /search to find someone!"
        )

async def reveal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    partner_id = get_active_match(user_id)
    
    if not partner_id:
        await update.message.reply_text("You're not in an active chat!")
        return
    
    mark_reveal(user_id)
    
    if both_revealed(user_id):
        user = get_user_data(user_id)
        partner = get_user_data(partner_id)
        
        if user and partner:
            await update.message.reply_text(
                f"🎭 Identity Revealed!\n\n"
                f"Name: {partner[2]}\n"
                f"Username: @{partner[1]}\n"
                f"Age: {partner[3]}"
            )
            
            await context.bot.send_message(
                chat_id=partner_id,
                text=f"🎭 Identity Revealed!\n\n"
                     f"Name: {user[2]}\n"
                     f"Username: @{user[1]}\n"
                     f"Age: {user[3]}"
            )
    else:
        await update.message.reply_text("✋ Waiting for partner to reveal...")
        await context.bot.send_message(
            chat_id=partner_id,
            text="👤 Your partner wants to reveal! Type /reveal to accept."
        )

async def next_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    partner_id = get_active_match(user_id)
    
    if partner_id:
        end_match(user_id)
        await context.bot.send_message(
            chat_id=partner_id,
            text="💔 Your chat partner left. Use /search to find someone new."
        )
    
    await search(update, context)

async def stop_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    partner_id = get_active_match(user_id)
    
    if partner_id:
        end_match(user_id)
        await update.message.reply_text("Chat ended.")
        await context.bot.send_message(
            chat_id=partner_id,
            text="💔 Your chat partner ended the conversation."
        )
    else:
        await update.message.reply_text("You're not in a chat.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception while handling an update: {context.error}")

def main():
    try:
        # Initialize connection pool only if DATABASE_URL is set
        if DATABASE_URL:
            init_pool()
            init_db()
        else:
            logger.warning("DATABASE_URL not set. Running without database. Add PostgreSQL to Railway.")
        
        # Create application
        app = Application.builder().token(TOKEN).build()
        
        # Add handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("search", search))
        app.add_handler(CommandHandler("next", next_match))
        app.add_handler(CommandHandler("reveal", reveal))
        app.add_handler(CommandHandler("stop", stop_chat))
        app.add_handler(CallbackQueryHandler(handle_callback))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))
        
        # Add error handler
        app.add_error_handler(error_handler)
        
        # Start bot
        logger.info("🎭 Anonymous Dating Bot started successfully!")
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == '__main__':
    main()

