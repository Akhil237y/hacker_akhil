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
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Yes", callback_data="yes"), InlineKeyboardButton("No", callback_data="no")]
    ])
    await message.reply_text("Are you ready to do something crazy! 💀", reply_markup=keyboard)

@bot.on_callback_query()
async def handle_buttons(client, callback):
    user_id = callback.from_user.id
    if callback.data == "no":
        await callback.message.edit("Ook, sir # Bot owner : @hacker_akhil_649k")
    elif callback.data == "yes":
        user_sessions[user_id] = {"stage": "awaiting_phone"}
        await callback.message.edit("Send your phone number (with +91):")

@bot.on_message(filters.private & filters.text)
async def handle_input(client, message):
    user_id = message.from_user.id
    text = message.text
    if user_id not in user_sessions:
        return

    data = user_sessions[user_id]

    if data["stage"] == "awaiting_phone":
        data["phone"] = text
        data["client"] = TelegramClient(StringSession(), API_ID, API_HASH)
        await data["client"].connect()
        await data["client"].send_code_request(text)
        data["stage"] = "awaiting_code"
        await message.reply("OTP sent. Enter the code:")

    elif data["stage"] == "awaiting_code":
        try:
            await data["client"].sign_in(data["phone"], text)
        except:
            data["stage"] = "awaiting_password"
            await message.reply("If 2FA is enabled, enter your password:")
            return
        await complete_login(user_id, message)

    elif data["stage"] == "awaiting_password":
        await data["client"].sign_in(password=text)
        await complete_login(user_id, message)

    elif data["stage"] == "awaiting_text":
        data["text"] = text
        await message.reply(
            "I am ready, let's gooo 🤝",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Edit Text", callback_data="edit")],
                [InlineKeyboardButton("Logout", callback_data="logout")]
            ])
        )
        data["stage"] = "ready"
        start_userbot(user_id)

async def complete_login(user_id, message):
    session_str = user_sessions[user_id]["client"].session.save()
    user_sessions[user_id]["session_str"] = session_str
    user_sessions[user_id]["stage"] = "awaiting_text"
    await message.reply_text(
        "✅ Login successful!\n\n🔐 Your Session String:\n`{}`\n\n📌 Save this safely!".format(session_str),
        parse_mode="markdown"
    )
    await message.reply("Now send the spam text:")

@bot.on_callback_query(filters.create(lambda _, __, q: q.data in ["edit", "logout"]))
async def handle_actions(client, callback):
    user_id = callback.from_user.id
    if user_id not in user_sessions:
        return
    if callback.data == "edit":
        user_sessions[user_id]["stage"] = "awaiting_text"
        await callback.message.edit("Send new spam text:")
    elif callback.data == "logout":
        await user_sessions[user_id]["client"].disconnect()
        del user_sessions[user_id]
        await callback.message.edit("🛑 Session ended and removed.")

def start_userbot(user_id):
    session_str = user_sessions[user_id]["session_str"]
    spam_text = user_sessions[user_id]["text"]
    client = TelegramClient(StringSession(session_str), API_ID, API_HASH)

    @client.on(events.NewMessage(pattern=r"\.send (\d+)"))
    async def spammer(event):
        count = int(event.pattern_match.group(1))
        for _ in range(count):
            try:
                await event.respond(spam_text)
                await asyncio.sleep(0.4)
            except Exception as e:
                print("Error:", e)

    asyncio.create_task(client.start())
    asyncio.create_task(client.run_until_disconnected())

bot.run()
