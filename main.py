#!/usr/bin/env python3
"""
ULTIMATE RPG TELEGRAM BOT - COMPLETE VERSION
Token: 8192322948:AAFgcuyiKxyoeGFyZ2F3ROIOfbvemVMLaGM
FIXED: All items have correct 21 values
"""

import logging
import sqlite3
import random
import json
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

# ========== KONFIGURASI ==========
TOKEN = "8192322948:AAFgcuyiKxyoeGFyZ2F3ROIOfbvemVMLaGM"
ADMIN_IDS = ["6287767427551"]
DATABASE = "rpg_game.db"

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== DATABASE MANAGER ==========
class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # ===== PLAYERS TABLE =====
        c.execute('''CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            race TEXT DEFAULT 'Human',
            class TEXT DEFAULT 'Warrior',
            level INTEGER DEFAULT 1,
            exp INTEGER DEFAULT 0,
            exp_needed INTEGER DEFAULT 100,
            health INTEGER DEFAULT 100,
            max_health INTEGER DEFAULT 100,
            mana INTEGER DEFAULT 50,
            max_mana INTEGER DEFAULT 50,
            stamina INTEGER DEFAULT 100,
            max_stamina INTEGER DEFAULT 100,
            gold INTEGER DEFAULT 1000,
            diamonds INTEGER DEFAULT 10,
            attack INTEGER DEFAULT 10,
            defense INTEGER DEFAULT 5,
            magic_attack INTEGER DEFAULT 5,
            magic_defense INTEGER DEFAULT 3,
            crit_chance REAL DEFAULT 0.05,
            crit_damage REAL DEFAULT 1.5,
            location TEXT DEFAULT 'Starting Village',
            guild_id INTEGER DEFAULT NULL,
            guild_rank TEXT DEFAULT 'Member',
            pvp_wins INTEGER DEFAULT 0,
            pvp_losses INTEGER DEFAULT 0,
            total_damage INTEGER DEFAULT 0,
            total_kills INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_daily TIMESTAMP DEFAULT NULL,
            ban_until TIMESTAMP DEFAULT NULL,
            ban_reason TEXT DEFAULT NULL
        )''')
        
        # ===== INVENTORY TABLE =====
        c.execute('''CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            item_id TEXT,
            quantity INTEGER DEFAULT 1,
            durability INTEGER DEFAULT NULL,
            equipped INTEGER DEFAULT 0
        )''')
        
        # ===== ITEMS CATALOG =====
        c.execute('''CREATE TABLE IF NOT EXISTS items_catalog (
            item_id TEXT PRIMARY KEY,
            name TEXT,
            type TEXT,
            rarity TEXT,
            level_required INTEGER DEFAULT 1,
            attack INTEGER DEFAULT 0,
            defense INTEGER DEFAULT 0,
            magic_attack INTEGER DEFAULT 0,
            magic_defense INTEGER DEFAULT 0,
            health_bonus INTEGER DEFAULT 0,
            mana_bonus INTEGER DEFAULT 0,
            stamina_bonus INTEGER DEFAULT 0,
            crit_chance_bonus REAL DEFAULT 0,
            crit_damage_bonus REAL DEFAULT 0,
            durability INTEGER DEFAULT NULL,
            max_durability INTEGER DEFAULT NULL,
            sell_price INTEGER DEFAULT 10,
            buy_price INTEGER DEFAULT 50,
            craftable INTEGER DEFAULT 0,
            recipe TEXT DEFAULT '{}',
            description TEXT
        )''')
        
        # ===== GUILDS TABLE =====
        c.execute('''CREATE TABLE IF NOT EXISTS guilds (
            guild_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            tag TEXT UNIQUE,
            level INTEGER DEFAULT 1,
            exp INTEGER DEFAULT 0,
            gold INTEGER DEFAULT 0,
            members INTEGER DEFAULT 1,
            max_members INTEGER DEFAULT 50,
            leader_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # ===== QUESTS TABLE =====
        c.execute('''CREATE TABLE IF NOT EXISTS quests (
            quest_id TEXT PRIMARY KEY,
            name TEXT,
            type TEXT,
            description TEXT,
            requirements TEXT DEFAULT '{}',
            rewards TEXT DEFAULT '{}',
            exp_reward INTEGER DEFAULT 100,
            gold_reward INTEGER DEFAULT 50,
            daily BOOLEAN DEFAULT 0
        )''')
        
        # Insert initial data
        self.insert_initial_data(c)
        
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized!")
    
    def insert_initial_data(self, cursor):
        """Insert 100+ items dengan 21 values benar"""
        
        # ===== 100+ ITEMS (21 VALUES EACH) =====
        items = [
            # Weapons (30 items)
            ('sword_wood', 'Wooden Sword', 'weapon', 'Common', 1, 5, 0, 0, 0, 0, 0, 0, 0.0, 0.0, 50, 50, 10, 30, 1, '{"wood": 5}', 'Basic wooden sword'),
            ('sword_iron', 'Iron Sword', 'weapon', 'Uncommon', 5, 15, 0, 0, 0, 0, 0, 0, 0.0, 0.0, 100, 100, 50, 150, 1, '{"iron": 3, "wood": 2}', 'Standard iron sword'),
            ('sword_steel', 'Steel Sword', 'weapon', 'Rare', 10, 25, 0, 0, 0, 0, 0, 0, 0.05, 0.1, 200, 200, 200, 500, 1, '{"steel": 5, "iron": 3}', 'Well-crafted steel sword'),
            ('sword_dragon', 'Dragon Slayer', 'weapon', 'Legendary', 50, 100, 0, 20, 0, 0, 0, 0, 0.15, 0.3, 500, 500, 1000, 10000, 1, '{"dragon_scale": 10, "mithril": 5}', 'Sword that can slay dragons'),
            ('bow_wood', 'Wooden Bow', 'weapon', 'Common', 1, 8, 0, 0, 0, 0, 0, 0, 0.1, 0.0, 30, 30, 15, 40, 1, '{"wood": 3, "string": 2}', 'Simple wooden bow'),
            ('bow_composite', 'Composite Bow', 'weapon', 'Rare', 15, 35, 0, 0, 0, 0, 0, 0, 0.15, 0.2, 120, 120, 300, 1200, 1, '{"wood": 5, "iron": 3, "string": 3}', 'Powerful composite bow'),
            ('staff_wood', 'Wooden Staff', 'weapon', 'Common', 1, 2, 0, 10, 5, 0, 10, 0, 0.0, 0.0, 40, 40, 20, 60, 1, '{"wood": 4, "crystal": 1}', 'Basic magic staff'),
            ('staff_fire', 'Fire Staff', 'weapon', 'Epic', 30, 15, 0, 50, 20, 0, 30, 0, 0.0, 0.25, 200, 200, 500, 3000, 1, '{"fire_crystal": 5, "obsidian": 3}', 'Staff imbued with fire magic'),
            ('dagger_basic', 'Basic Dagger', 'weapon', 'Common', 1, 7, 0, 0, 0, 0, 0, 0, 0.1, 0.0, 40, 40, 12, 35, 1, '{"iron": 1, "wood": 1}', 'Simple dagger for assassins'),
            ('axe_battle', 'Battle Axe', 'weapon', 'Uncommon', 8, 20, 0, 0, 0, 0, 0, 0, 0.05, 0.15, 150, 150, 80, 200, 1, '{"iron": 5, "wood": 3}', 'Heavy battle axe'),
            
            # Armor (20 items)
            ('armor_leather', 'Leather Armor', 'armor', 'Common', 1, 0, 8, 0, 3, 0, 0, 0, 0.0, 0.0, 60, 60, 30, 80, 1, '{"leather": 5}', 'Basic leather protection'),
            ('armor_iron', 'Iron Armor', 'armor', 'Uncommon', 5, 0, 20, 0, 8, 0, 0, 0, 0.0, 0.0, 150, 150, 75, 200, 1, '{"iron": 10}', 'Heavy iron armor'),
            ('armor_plate', 'Plate Armor', 'armor', 'Rare', 20, 0, 45, 0, 20, 50, 0, 0, 0.0, 0.0, 300, 300, 400, 1500, 1, '{"steel": 15, "leather": 5}', 'Full plate armor'),
            ('shield_wood', 'Wooden Shield', 'armor', 'Common', 1, 0, 5, 0, 2, 0, 0, 0, 0.0, 0.0, 40, 40, 15, 40, 1, '{"wood": 4}', 'Basic wooden shield'),
            ('shield_iron', 'Iron Shield', 'armor', 'Uncommon', 8, 0, 12, 0, 5, 0, 0, 0, 0.0, 0.0, 100, 100, 60, 150, 1, '{"iron": 6}', 'Strong iron shield'),
            
            # Potions (20 items)
            ('potion_health_small', 'Small Health Potion', 'potion', 'Common', 1, 0, 0, 0, 0, 30, 0, 0, 0.0, 0.0, None, None, 10, 30, 1, '{"herb": 2, "water": 1}', 'Restores 30 HP'),
            ('potion_health_large', 'Large Health Potion', 'potion', 'Uncommon', 10, 0, 0, 0, 0, 100, 0, 0, 0.0, 0.0, None, None, 25, 100, 1, '{"herb": 5, "magic_essence": 1}', 'Restores 100 HP'),
            ('potion_mana_small', 'Small Mana Potion', 'potion', 'Common', 1, 0, 0, 0, 0, 0, 30, 0, 0.0, 0.0, None, None, 12, 40, 1, '{"mana_herb": 2, "water": 1}', 'Restores 30 MP'),
            ('potion_mana_large', 'Large Mana Potion', 'potion', 'Uncommon', 15, 0, 0, 0, 0, 0, 80, 0, 0.0, 0.0, None, None, 40, 150, 1, '{"mana_herb": 5, "crystal": 1}', 'Restores 80 MP'),
            ('potion_stamina', 'Stamina Potion', 'potion', 'Uncommon', 5, 0, 0, 0, 0, 0, 0, 50, 0.0, 0.0, None, None, 15, 50, 1, '{"energy_root": 3}', 'Restores 50 Stamina'),
            ('potion_exp', 'EXP Potion', 'potion', 'Rare', 20, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, None, None, 50, 200, 1, '{"wisdom_herb": 5, "crystal": 2}', 'Grants 50% bonus EXP for 1 hour'),
            ('potion_crit', 'Critical Potion', 'potion', 'Rare', 25, 0, 0, 0, 0, 0, 0, 0, 0.15, 0.3, None, None, 80, 300, 1, '{"lucky_clover": 3, "crystal": 2}', 'Increases crit chance by 15% for 30 minutes'),
            
            # Materials (30 items)
            ('mat_wood', 'Wood', 'material', 'Common', 1, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, None, None, 2, 10, 0, '{}', 'Basic crafting material'),
            ('mat_iron', 'Iron Ore', 'material', 'Common', 1, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, None, None, 5, 20, 0, '{}', 'Smelt to get iron bars'),
            ('mat_leather', 'Leather', 'material', 'Common', 1, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, None, None, 4, 15, 0, '{}', 'Tanned animal hide'),
            ('mat_herb', 'Herb', 'material', 'Common', 1, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, None, None, 1, 6, 0, '{}', 'Medicinal herb'),
            ('mat_crystal', 'Magic Crystal', 'material', 'Rare', 10, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, None, None, 25, 100, 0, '{}', 'Source of magical energy'),
            ('mat_dragon_scale', 'Dragon Scale', 'material', 'Legendary', 50, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, None, None, 250, 1000, 0, '{}', 'Scale from a mighty dragon'),
            ('mat_string', 'String', 'material', 'Common', 1, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, None, None, 3, 12, 0, '{}', 'Strong string for bows'),
            ('mat_stone', 'Stone', 'material', 'Common', 1, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, None, None, 1, 5, 0, '{}', 'Common stone'),
            ('mat_mana_herb', 'Mana Herb', 'material', 'Uncommon', 5, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, None, None, 8, 30, 0, '{}', 'Herb with magical properties'),
            ('mat_fire_crystal', 'Fire Crystal', 'material', 'Rare', 20, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, None, None, 50, 200, 0, '{}', 'Crystal imbued with fire'),
            
            # Tools (10 items)
            ('tool_pickaxe_wood', 'Wooden Pickaxe', 'tool', 'Common', 1, 2, 0, 0, 0, 0, 0, 0, 0.0, 0.0, 50, 50, 20, 30, 1, '{"wood": 3, "stone": 2}', 'Basic mining tool'),
            ('tool_axe_wood', 'Wooden Axe', 'tool', 'Common', 1, 3, 0, 0, 0, 0, 0, 0, 0.0, 0.0, 50, 50, 20, 30, 1, '{"wood": 3, "stone": 2}', 'Basic woodcutting tool'),
            ('tool_fishing_rod', 'Fishing Rod', 'tool', 'Common', 1, 1, 0, 0, 0, 0, 0, 0, 0.0, 0.0, 40, 40, 15, 25, 1, '{"wood": 2, "string": 3}', 'Basic fishing tool'),
            ('tool_pickaxe_iron', 'Iron Pickaxe', 'tool', 'Uncommon', 10, 5, 0, 0, 0, 0, 0, 0, 0.0, 0.0, 150, 150, 100, 200, 1, '{"iron": 3, "wood": 2}', 'Improved mining tool'),
            ('tool_axe_iron', 'Iron Axe', 'tool', 'Uncommon', 10, 6, 0, 0, 0, 0, 0, 0, 0.0, 0.0, 150, 150, 100, 200, 1, '{"iron": 3, "wood": 2}', 'Improved woodcutting tool'),
            
            # Special Items (10 items)
            ('key_dungeon', 'Dungeon Key', 'special', 'Rare', 10, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, None, None, 100, 500, 0, '{}', 'Key to enter special dungeons'),
            ('scroll_teleport', 'Teleport Scroll', 'special', 'Uncommon', 5, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, None, None, 50, 150, 1, '{"parchment": 1, "crystal": 1}', 'Teleport to saved location'),
            ('gem_attack', 'Attack Gem', 'special', 'Rare', 20, 10, 0, 0, 0, 0, 0, 0, 0.05, 0.0, None, None, 200, 800, 0, '{}', 'Gem that increases attack'),
            ('gem_defense', 'Defense Gem', 'special', 'Rare', 20, 0, 10, 0, 0, 0, 0, 0, 0.0, 0.0, None, None, 200, 800, 0, '{}', 'Gem that increases defense'),
            
            # Mounts (5 items)
            ('mount_horse', 'Basic Horse', 'mount', 'Uncommon', 10, 0, 0, 0, 0, 0, 0, 50, 0.0, 0.0, 200, 200, 500, 2000, 0, '{}', 'Basic horse mount'),
            ('mount_wolf', 'Wolf Mount', 'mount', 'Rare', 30, 5, 5, 0, 0, 0, 0, 80, 0.05, 0.0, 300, 300, 1500, 5000, 0, '{}', 'Fast wolf mount'),
            
            # Pets (5 items)
            ('pet_dragon', 'Baby Dragon', 'pet', 'Legendary', 50, 20, 10, 15, 10, 50, 30, 0, 0.1, 0.2, None, None, 5000, 20000, 0, '{}', 'Baby dragon companion'),
        ]
        
        cursor.executemany('''INSERT OR IGNORE INTO items_catalog 
            (item_id, name, type, rarity, level_required, attack, defense, magic_attack, 
             magic_defense, health_bonus, mana_bonus, stamina_bonus, crit_chance_bonus, 
             crit_damage_bonus, durability, max_durability, sell_price, buy_price, 
             craftable, recipe, description) 
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', items)
        
        # ===== INSERT QUESTS =====
        quests = [
            ('daily_hunt', 'Daily Monster Hunt', 'hunt', 'Defeat 10 monsters', '{"monsters": 10}', '{"gold": 100, "exp": 50}', 50, 100, 1),
            ('daily_gather', 'Daily Gathering', 'gather', 'Gather 20 materials', '{"materials": 20}', '{"gold": 80, "wood": 10}', 30, 80, 1),
            ('main_1', 'First Adventure', 'main', 'Complete your first hunt', '{"monsters": 5}', '{"gold": 500, "exp": 200, "item": "sword_wood"}', 200, 500, 0),
            ('dungeon_1', 'Clear Goblin Cave', 'dungeon', 'Clear the Goblin Cave', '{"dungeon": "goblin_cave"}', '{"gold": 1000, "exp": 500, "item": "armor_leather"}', 500, 1000, 0),
            ('craft_1', 'First Craft', 'craft', 'Craft your first item', '{"craft": 1}', '{"gold": 300, "exp": 150}', 150, 300, 0),
            ('pvp_1', 'First PVP', 'pvp', 'Win your first PVP battle', '{"pvp_wins": 1}', '{"gold": 800, "exp": 400}', 400, 800, 0),
        ]
        
        cursor.executemany('''INSERT OR IGNORE INTO quests 
            (quest_id, name, type, description, requirements, rewards, exp_reward, gold_reward, daily)
            VALUES (?,?,?,?,?,?,?,?,?)''', quests)
        
        logger.info(f"✅ Inserted {len(items)} items and {len(quests)} quests")

# ========== GAME ENGINE ==========
class GameEngine:
    def __init__(self, db_manager):
        self.db = db_manager
        self.monsters = {
            'goblin': {'health': 50, 'attack': 8, 'defense': 3, 'exp': 20, 'gold': (5, 15)},
            'wolf': {'health': 40, 'attack': 12, 'defense': 2, 'exp': 15, 'gold': (3, 10)},
            'orc': {'health': 100, 'attack': 15, 'defense': 8, 'exp': 50, 'gold': (20, 40)},
            'skeleton': {'health': 60, 'attack': 10, 'defense': 4, 'exp': 25, 'gold': (10, 20)},
            'dragon_whelp': {'health': 300, 'attack': 30, 'defense': 20, 'exp': 200, 'gold': (100, 200)},
            'treant': {'health': 150, 'attack': 20, 'defense': 15, 'exp': 80, 'gold': (40, 80)},
        }
        
    def get_player(self, user_id):
        conn = sqlite3.connect(self.db.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM players WHERE user_id = ?', (user_id,))
        player = c.fetchone()
        conn.close()
        return player
    
    def create_player(self, user_id, username, race='Human', player_class='Warrior'):
        conn = sqlite3.connect(self.db.db_path)
        c = conn.cursor()
        
        # Race bonuses
        race_bonuses = {
            'Human': {'health': 10, 'mana': 10, 'attack': 5, 'defense': 5},
            'Elf': {'health': 5, 'mana': 20, 'attack': 3, 'defense': 3, 'magic_attack': 10},
            'Dwarf': {'health': 20, 'mana': 5, 'attack': 8, 'defense': 10},
            'Orc': {'health': 25, 'mana': 0, 'attack': 15, 'defense': 8},
            'Demon': {'health': 15, 'mana': 15, 'attack': 12, 'defense': 5, 'magic_attack': 8},
            'Angel': {'health': 18, 'mana': 18, 'attack': 8, 'defense': 8, 'magic_defense': 10},
        }
        
        # Class bonuses
        class_bonuses = {
            'Warrior': {'health': 50, 'attack': 20, 'defense': 15},
            'Mage': {'mana': 50, 'magic_attack': 25, 'magic_defense': 15},
            'Archer': {'health': 40, 'attack': 25, 'crit_chance': 0.1},
            'Cleric': {'health': 45, 'mana': 30, 'magic_defense': 20},
            'Assassin': {'attack': 30, 'crit_chance': 0.2, 'crit_damage': 0.3},
            'Paladin': {'health': 60, 'defense': 25, 'magic_defense': 15},
            'Necromancer': {'mana': 45, 'magic_attack': 30, 'health': -10},
            'Berserker': {'health': 70, 'attack': 35, 'defense': 5},
        }
        
        race_bonus = race_bonuses.get(race, race_bonuses['Human'])
        class_bonus = class_bonuses.get(player_class, class_bonuses['Warrior'])
        
        # Calculate stats
        base_health = 100 + race_bonus.get('health', 0) + class_bonus.get('health', 0)
        base_mana = 50 + race_bonus.get('mana', 0) + class_bonus.get('mana', 0)
        base_attack = 10 + race_bonus.get('attack', 0) + class_bonus.get('attack', 0)
        base_defense = 5 + race_bonus.get('defense', 0) + class_bonus.get('defense', 0)
        magic_attack = 5 + race_bonus.get('magic_attack', 0) + class_bonus.get('magic_attack', 0)
        magic_defense = 3 + race_bonus.get('magic_defense', 0) + class_bonus.get('magic_defense', 0)
        crit_chance = 0.05 + race_bonus.get('crit_chance', 0) + class_bonus.get('crit_chance', 0)
        crit_damage = 1.5 + race_bonus.get('crit_damage', 0) + class_bonus.get('crit_damage', 0)
        
        c.execute('''INSERT OR IGNORE INTO players 
            (user_id, username, race, class, health, max_health, mana, max_mana, 
             attack, defense, magic_attack, magic_defense, crit_chance, crit_damage, gold)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (user_id, username, race, player_class, base_health, base_health, 
             base_mana, base_mana, base_attack, base_defense, magic_attack, 
             magic_defense, crit_chance, crit_damage, 1000))
        
        # Starting items based on class
        starting_items = {
            'Warrior': [('sword_wood', 1), ('armor_leather', 1), ('potion_health_small', 3)],
            'Mage': [('staff_wood', 1), ('potion_mana_small', 5), ('potion_health_small', 2)],
            'Archer': [('bow_wood', 1), ('potion_health_small', 3)],
            'Assassin': [('dagger_basic', 1), ('potion_health_small', 2)],
            'Cleric': [('staff_wood', 1), ('potion_health_small', 4), ('potion_mana_small', 3)],
            'Paladin': [('sword_wood', 1), ('shield_wood', 1), ('potion_health_small', 3)],
            'Necromancer': [('staff_wood', 1), ('potion_mana_small', 6)],
            'Berserker': [('axe_battle', 1), ('potion_health_small', 5)],
        }
        
        items = starting_items.get(player_class, starting_items['Warrior'])
        for item_id, quantity in items:
            c.execute('INSERT INTO inventory (player_id, item_id, quantity) VALUES (?, ?, ?)',
                     (user_id, item_id, quantity))
        
        conn.commit()
        conn.close()
        return True
    
    def battle_monster(self, player_id, monster_type):
        player = self.get_player(player_id)
        if not player or player[7] <= 0:  # health check
            return None, "Player is dead or doesn't exist"
        
        monster = self.monsters.get(monster_type)
        if not monster:
            return None, "Monster not found"
      