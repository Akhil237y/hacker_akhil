from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os, asyncio

API_ID = 21073191
API_HASH = "272a189777e9c47af345a0dd52b1f0f9"
BOT_TOKEN = "7637038432:AAHUJ5cxZSmoeQNrQ4MDWvAnhtDBeTfrZo8"

app = Client("crazy_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_data = {}

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Yes", callback_data="yes"), InlineKeyboardButton("No", callback_data="no")]
    ])
    await message.reply("Are you ready to do something crazy! 💀", reply_markup=buttons)

@app.on_callback_query()
async def button_handler(client, callback_query):
    user_id = callback_query.from_user.id
    if callback_query.data == "no":
        await callback_query.message.edit("Ook, sir # Bot owner : @hacker_akhil_649k")
    elif callback_query.data == "yes":
        user_data[user_id] = {"text": None}
        await callback_query.message.edit("Enter text you want to spam:")

@app.on_message(filters.text & filters.private)
async def save_text(client, message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id]["text"] is None:
        user_data[user_id]["text"] = message.text
        await message.reply("I am ready, let's gooo 🤝", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Edit Text", callback_data="edit"), InlineKeyboardButton("Remove", callback_data="remove")]
        ]))
    elif ".send" in message.text.lower():
        try:
            count = int(message.text.split()[1])
            for _ in range(count):
                await message.reply(user_data[user_id]["text"])
                await asyncio.sleep(0.4)
        except:
            await message.reply("Invalid command format. Use `.send 5`")

@app.on_callback_query(filters.create(lambda _, __, query: query.data in ["edit", "remove"]))
async def handle_edit_remove(client, callback_query):
    user_id = callback_query.from_user.id
    if callback_query.data == "edit":
        user_data[user_id]["text"] = None
        await callback_query.message.edit("Okay, send new text to use.")
    elif callback_query.data == "remove":
        user_data.pop(user_id, None)
        await callback_query.message.edit("Session removed successfully.")

app.run()
