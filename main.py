import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon import events
import os

API_ID = 21073191
API_HASH = "272a189777e9c47af345a0dd52b1f0f9"
BOT_TOKEN = "7637038432:AAHUJ5cxZSmoeQNrQ4MDWvAnhtDBeTfrZo8"

bot = Client("CrazyAkhilBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_sessions = {}

@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("Yes", callback_data="yes"),
        InlineKeyboardButton("No", callback_data="no")
    ]])
    await message.reply_text("Are you ready to do something crazy! 💀", reply_markup=keyboard)

@bot.on_callback_query()
async def button_handler(client, callback):
    user_id = callback.from_user.id
    if callback.data == "no":
        await callback.message.edit("Ook, sir # Bot owner : @hacker_akhil_649k")
    elif callback.data == "yes":
        await callback.message.edit("Send your phone number in international format (e.g. +91xxxxxxxxxx):")
        user_sessions[user_id] = {"stage": "awaiting_phone"}

@bot.on_message(filters.private & filters.text)
async def handle_text(client, message):
    user_id = message.from_user.id
    text = message.text

    if user_id not in user_sessions:
        return

    data = user_sessions[user_id]

    if data.get("stage") == "awaiting_phone":
        data["phone"] = text
        data["client"] = TelegramClient(StringSession(), API_ID, API_HASH)
        await data["client"].connect()
        await data["client"].send_code_request(text)
        data["stage"] = "awaiting_code"
        await message.reply("Code sent. Now send the OTP you received:")

    elif data.get("stage") == "awaiting_code":
        try:
            await data["client"].sign_in(data["phone"], text)
        except:
            await message.reply("If 2FA is enabled, send your password:")
            data["stage"] = "awaiting_password"
            return
        await on_login_success(user_id, message)

    elif data.get("stage") == "awaiting_password":
        await data["client"].sign_in(password=text)
        await on_login_success(user_id, message)

    elif data.get("stage") == "awaiting_text":
        data["text"] = text
        await message.reply("I am ready, let's gooo 🤝", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Edit Text", callback_data="edit"),
             InlineKeyboardButton("Remove", callback_data="remove")]
        ]))
        data["stage"] = "ready"
        start_userbot(user_id)

def start_userbot(user_id):
    session_str = user_sessions[user_id]["client"].session.save()
    spam_text = user_sessions[user_id]["text"]
    client = TelegramClient(StringSession(session_str), API_ID, API_HASH)

    @client.on(events.NewMessage(pattern=r"\.send (\d+)"))
    async def handler(event):
        count = int(event.pattern_match.group(1))
        for _ in range(count):
            await event.respond(spam_text)
            await asyncio.sleep(0.4)

    asyncio.create_task(client.start())
    asyncio.create_task(client.run_until_disconnected())

async def on_login_success(user_id, message):
    user_sessions[user_id]["stage"] = "awaiting_text"
    await message.reply("Login successful ✅\nNow send the spam text you want to use:")

@bot.on_callback_query(filters.create(lambda _, __, query: query.data in ["edit", "remove"]))
async def edit_or_remove(client, callback):
    user_id = callback.from_user.id
    if user_id not in user_sessions:
        return
    if callback.data == "edit":
        user_sessions[user_id]["stage"] = "awaiting_text"
        await callback.message.edit("Okay, send new text:")
    elif callback.data == "remove":
        await user_sessions[user_id]["client"].disconnect()
        del user_sessions[user_id]
        await callback.message.edit("Session removed.")

bot.run()
