#!/usr/bin/env python3
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    filters, CallbackQueryHandler, ContextTypes
)
import sqlite3
import random
from datetime import datetime

# ========== KONFIGURASI ==========
# Token dari environment variable Railway
TOKEN = os.environ.get("BOT_TOKEN", "8192322948:AAFgcuyiKxyoeGFyZ2F3ROIOfbvemVMLaGM")
DATABASE = "rpg_game.db"

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== SETUP DATABASE ==========
def setup_database():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Table Players
    c.execute('''CREATE TABLE IF NOT EXISTS players
                 (user_id INTEGER PRIMARY KEY,
                  username TEXT,
                  level INTEGER DEFAULT 1,
                  exp INTEGER DEFAULT 0,
                  health INTEGER DEFAULT 100,
                  max_health INTEGER DEFAULT 100,
                  mana INTEGER DEFAULT 50,
                  max_mana INTEGER DEFAULT 50,
                  class TEXT DEFAULT 'Warrior',
                  gold INTEGER DEFAULT 100,
                  attack INTEGER DEFAULT 10,
                  defense INTEGER DEFAULT 5,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Table Inventory
    c.execute('''CREATE TABLE IF NOT EXISTS inventory
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  item_name TEXT,
                  quantity INTEGER DEFAULT 1,
                  FOREIGN KEY(user_id) REFERENCES players(user_id))''')
    
    # Insert default items
    c.execute('''INSERT OR IGNORE INTO inventory (user_id, item_name, quantity)
                 VALUES (999999, 'Health Potion', 100)''')
    
    conn.commit()
    conn.close()
    logger.info("✅ Database setup complete!")

# ========== FUNGSI DATABASE ==========
def get_player(user_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM players WHERE user_id=?', (user_id,))
    player = c.fetchone()
    conn.close()
    
    if player:
        return {
            'user_id': player[0],
            'username': player[1],
            'level': player[2],
            'exp': player[3],
            'health': player[4],
            'max_health': player[5],
            'mana': player[6],
            'max_mana': player[7],
            'class': player[8],
            'gold': player[9],
            'attack': player[10],
            'defense': player[11]
        }
    return None

def create_player(user_id, username, player_class='Warrior'):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    stats = {
        'Warrior': {'health': 120, 'mana': 30, 'attack': 15, 'defense': 10},
        'Mage': {'health': 80, 'mana': 100, 'attack': 20, 'defense': 5},
        'Archer': {'health': 100, 'mana': 50, 'attack': 18, 'defense': 7},
        'Cleric': {'health': 110, 'mana': 80, 'attack': 12, 'defense': 8}
    }
    
    stat = stats.get(player_class, stats['Warrior'])
    
    c.execute('''INSERT OR IGNORE INTO players 
                 (user_id, username, class, health, max_health, mana, max_mana, attack, defense, gold)
                 VALUES (?,?,?,?,?,?,?,?,?,?)''',
              (user_id, username, player_class, 
               stat['health'], stat['health'],
               stat['mana'], stat['mana'],
               stat['attack'], stat['defense'], 100))
    
    # Give starting items
    starting_items = [('Health Potion', 3), ('Mana Potion', 2), ('Basic Sword', 1)]
    for item, qty in starting_items:
        c.execute('INSERT INTO inventory (user_id, item_name, quantity) VALUES (?,?,?)',
                  (user_id, item, qty))
    
    conn.commit()
    conn.close()
    logger.info(f"✅ Player created: {username} ({player_class})")

# ========== COMMAND HANDLERS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    
    if not player:
        keyboard = [
            [InlineKeyboardButton("⚔️ Warrior", callback_data='class_Warrior')],
            [InlineKeyboardButton("🔮 Mage", callback_data='class_Mage')],
            [InlineKeyboardButton("🏹 Archer", callback_data='class_Archer')],
            [InlineKeyboardButton("✝️ Cleric", callback_data='class_Cleric')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🎮 *WELCOME TO RPG FANTASY* 🎮\n\n"
            f"Hello {user.first_name}!\n"
            f"Choose your class to begin:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        await show_status(update, context)

async def class_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    class_choice = query.data.split('_')[1]
    
    create_player(user.id, user.first_name, class_choice)
    
    await query.edit_message_text(
        f"✅ *Account Created Successfully!*\n\n"
        f"🎭 **Class**: {class_choice}\n"
        f"👤 **Player**: {user.first_name}\n"
        f"💰 **Starting Gold**: 100\n"
        f"🎒 **Items**: 3x Health Potion, 2x Mana Potion, 1x Basic Sword\n\n"
        f"Type /menu to begin your adventure!",
        parse_mode='Markdown'
    )

async def show_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    
    if not player:
        await update.message.reply_text("Please use /start to create your account first!")
        return
    
    status_text = (
        f"👤 *{player['username']}* - Level {player['level']}\n"
        f"🎭 Class: {player['class']}\n"
        f"❤️  Health: {player['health']}/{player['max_health']}\n"
        f"🔵 Mana: {player['mana']}/{player['max_mana']}\n"
        f"💰 Gold: {player['gold']}\n"
        f"⚔️  Attack: {player['attack']}\n"
        f"🛡️  Defense: {player['defense']}\n"
        f"⭐ EXP: {player['exp']}/100"
    )
    
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🏹 Hunt Monster", callback_data='hunt')],
        [InlineKeyboardButton("🧭 Explore", callback_data='explore')],
        [InlineKeyboardButton("🎒 Inventory", callback_data='inventory')],
        [InlineKeyboardButton("🛒 Shop", callback_data='shop')],
        [InlineKeyboardButton("🏥 Heal", callback_data='heal')],
        [InlineKeyboardButton("📊 Status", callback_data='status')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎮 *MAIN MENU* 🎮\nChoose your action:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def hunt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    player = get_player(user.id)
    
    if not player:
        return
    
    # Simple battle system
    monsters = [
        {"name": "🐺 Wolf", "health": 30, "attack": 5, "gold": 10, "exp": 15},
        {"name": "👹 Goblin", "health": 40, "attack": 7, "gold": 15, "exp": 20},
        {"name": "🐉 Dragon", "health": 100, "attack": 15, "gold": 50, "exp": 50}
    ]
    
    monster = random.choice(monsters)
    
    # Calculate battle
    damage = random.randint(player['attack'] - 2, player['attack'] + 5)
    monster_damage = random.randint(max(1, monster['attack'] - player['defense']), monster['attack'])
    
    # Update player
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    new_gold = player['gold'] + monster['gold']
    new_exp = player['exp'] + monster['exp']
    new_health = max(0, player['health'] - monster_damage)
    
    # Check level up
    new_level = player['level']
    if new_exp >= 100:
        new_exp = new_exp - 100
        new_level += 1
        # Increase stats on level up
        c.execute('''UPDATE players SET 
                    level=?, exp=?, gold=?,
                    health=?, max_health=max_health+10,
                    attack=attack+2, defense=defense+1
                    WHERE user_id=?''',
                 (new_level, new_exp, new_gold, new_health, user.id))
        level_up_msg = "\n🎉 *LEVEL UP!* Stats increased!"
    else:
        c.execute('UPDATE players SET gold=?, exp=?, health=? WHERE user_id=?',
                 (new_gold, new_exp, new_health, user.id))
        level_up_msg = ""
    
    conn.commit()
    conn.close()
    
    # Create result message
    result_text = (
        f"⚔️ *BATTLE RESULTS* ⚔️\n\n"
        f"Encountered: {monster['name']}\n"
        f"💥 You dealt: {damage} damage\n"
        f"💀 Monster dealt: {monster_damage} damage\n"
        f"💰 Gold earned: {monster['gold']}\n"
        f"⭐ EXP earned: {monster['exp']}\n"
        f"❤️  Your health: {new_health}/{player['max_health']}\n"
        f"🏆 Level: {new_level}{level_up_msg}"
    )
    
    keyboard = [
        [InlineKeyboardButton("⚔️ Hunt Again", callback_data='hunt')],
        [InlineKeyboardButton("📋 Back to Menu", callback_data='menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        result_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def explore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    player = get_player(user.id)
    
    if not player:
        return
    
    events = [
        ("🎁", "You found a treasure chest!", 50, "💰 +50 Gold"),
        ("💊", "You discovered a healing herb!", 0, "❤️ Health restored"),
        ("💎", "You mined some gems!", 30, "💰 +30 Gold"),
        ("👻", "A ghost scared you!", -20, "❤️ -20 Health"),
        ("🪙", "You found gold coins on the road!", 25, "💰 +25 Gold")
    ]
    
    event = random.choice(events)
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    new_gold = player['gold'] + event[2]
    new_health = player['health']
    
    if event[2] < 0:  # Negative event (lost health)
        new_health = max(0, player['health'] + event[2])
    elif event[1] == "You discovered a healing herb!":
        new_health = min(player['max_health'], player['health'] + 30)
    
    c.execute('UPDATE players SET gold=?, health=? WHERE user_id=?',
             (new_gold, new_health, user.id))
    
    conn.commit()
    conn.close()
    
    result_text = (
        f"{event[0]} *EXPLORATION* {event[0]}\n\n"
        f"{event[1]}\n"
        f"{event[3]}\n\n"
        f"💰 Gold: {player['gold']} → {new_gold}\n"
        f"❤️  Health: {player['health']} → {new_health}"
    )
    
    keyboard = [
        [InlineKeyboardButton("🧭 Explore Again", callback_data='explore')],
        [InlineKeyboardButton("📋 Back to Menu", callback_data='menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        result_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT item_name, SUM(quantity) FROM inventory WHERE user_id=? GROUP BY item_name',
              (user.id,))
    items = c.fetchall()
    conn.close()
    
    if not items:
        items_text = "Your inventory is empty!"
    else:
        items_text = "\n".join([f"• {item[0]} x{item[1]}" for item in items])
    
    result_text = f"🎒 *INVENTORY*\n\n{items_text}"
    
    keyboard = [[InlineKeyboardButton("📋 Back to Menu", callback_data='menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        result_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    shop_items = [
        {"name": "💊 Health Potion", "price": 30, "callback": "buy_health"},
        {"name": "🔮 Mana Potion", "price": 40, "callback": "buy_mana"},
        {"name": "⚔️ Iron Sword", "price": 100, "callback": "buy_sword"},
        {"name": "🛡️ Iron Shield", "price": 80, "callback": "buy_shield"}
    ]
    
    keyboard = []
    for item in shop_items:
        keyboard.append([InlineKeyboardButton(
            f"{item['name']} - {item['price']}g", 
            callback_data=item['callback']
        )])
    keyboard.append([InlineKeyboardButton("📋 Back to Menu", callback_data='menu')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🛒 *ITEM SHOP* 🛒\nWhat would you like to buy?",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def heal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    player = get_player(user.id)
    
    if not player:
        return
    
    heal_cost = 20
    if player['gold'] >= heal_cost:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('UPDATE players SET health=max_health, gold=gold-? WHERE user_id=?',
                 (heal_cost, user.id))
        conn.commit()
        conn.close()
        
        result_text = (
            f"🏥 *HEALING COMPLETE* 🏥\n\n"
            f"Paid {heal_cost} gold for full healing\n"
            f"💰 Gold: {player['gold']} → {player['gold'] - heal_cost}\n"
            f"❤️  Health: {player['health']} → {player['max_health']}"
        )
    else:
        result_text = f"❌ Not enough gold! Need {heal_cost}g, but you have {player['gold']}g"
    
    keyboard = [[InlineKeyboardButton("📋 Back to Menu", callback_data='menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        result_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == 'menu':
        await query.answer()
        await menu_callback(update, context)
    elif data == 'hunt':
        await hunt(update, context)
    elif data == 'explore':
        await explore(update, context)
    elif data == 'inventory':
        await inventory(update, context)
    elif data == 'shop':
        await shop(update, context)
    elif data == 'heal':
        await heal(update, context)
    elif data == 'status':
        await query.answer()
        await show_status_callback(update, context)
    elif data.startswith('class_'):
        await class_callback(update, context)
    elif data.startswith('buy_'):
        await query.answer("Purchase feature coming soon!", show_alert=True)

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await menu(update, context)

async def show_status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await show_status(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🎮 *RPG FANTASY BOT HELP* 🎮\n\n"
        "*/start* - Start game or create character\n"
        "*/menu* - Show main menu\n"
        "*/status* - Show your status\n"
        "*/help* - Show this help message\n\n"
        "🎯 *How to play:*\n"
        "1. Use /start to create character\n"
        "2. Use /menu to access all features\n"
        "3. Hunt monsters to earn gold and EXP\n"
        "4. Explore to find treasures\n"
        "5. Heal when health is low\n\n"
        "⚔️ *Happy adventuring!*"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

# ========== MAIN FUNCTION ==========
def main():
    # Setup database
    setup_database()
    
    # Create bot application
    application = Application.builder().token(TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", show_status))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("help", help_command))
    
    # Add callback handlers
    application.add_handler(CallbackQueryHandler(class_callback, pattern='^class_'))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Start bot
    logger.info("🤖 Starting RPG Fantasy Bot...")
    application.run_polling()

if __name__ == '__main__':
    main()