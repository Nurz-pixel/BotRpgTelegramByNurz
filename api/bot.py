#!/usr/bin/env python3
"""
Webhook handler untuk Vercel
"""
import os
import asyncio
from main import main

def handler(request):
    """Handler untuk Vercel serverless function"""
    async def run_bot():
        await main()
    
    # Jalankan bot dalam event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(run_bot())
        return {
            'statusCode': 200,
            'body': 'Bot is running'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }