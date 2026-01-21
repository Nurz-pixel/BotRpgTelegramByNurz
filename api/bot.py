#!/usr/bin/env python3
"""
WEBHOOK Handler untuk Vercel
"""
import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
import json

# Import modul utama Anda
import sys
sys.path.append('..')

# Token dari environment variable
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Inisialisasi bot
application = Application.builder().token(TOKEN).build()

# ========== HANDLER SEDERHANA DULU ==========
async def start(update: Update, context):
    await update.message.reply_text("🎮 RPG Bot aktif di Vercel!")

async def help_command(update: Update, context):
    await update.message.reply_text("⚔️ RPG Bot Commands:\n/start - Mulai game\n/profile - Lihat profil\n/hunt - Berburu monster")

# ========== VERCEL HTTP HANDLER ==========
async def webhook_handler(request):
    """Handler untuk Vercel serverless function"""
    if request.method != "POST":
        return {"statusCode": 405, "body": "Method not allowed"}
    
    try:
        # Parse update dari Telegram
        body = await request.json()
        update = Update.de_json(body, application.bot)
        
        # Dispatch update ke handler
        await application.update_queue.put(update)
        
        return {
            "statusCode": 200,
            "body": "OK"
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }

# ========== SETUP FUNCTION ==========
async def setup():
    """Setup bot handlers"""
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Setup webhook
    webhook_url = os.environ.get("VERCEL_URL", "")
    if webhook_url:
        await application.bot.set_webhook(url=f"{webhook_url}/api/bot.py")
        print(f"Webhook set to: {webhook_url}/api/bot.py")
    
    # Start polling (untuk development)
    await application.initialize()
    await application.start()
    
    print("🤖 Bot setup completed!")

# ========== VERCEL HANDLER ==========
def handler(request):
    """Vercel serverless handler"""
    async def process():
        # Setup bot jika belum
        if not application.running:
            await setup()
        
        # Handle webhook request
        return await webhook_handler(request)
    
    # Run in event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        return loop.run_until_complete(process())
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Handler Error: {str(e)}"
        }

# Untuk development lokal
if __name__ == "__main__":
    import asyncio
    asyncio.run(setup())
    print("Bot running...")