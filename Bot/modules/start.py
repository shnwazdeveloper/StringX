from Bot import bot, LOGGER
from Bot.core.decorators.error_handler import handle_errors
from Bot.mongo.users import (
    has_accepted_terms as hat, accept_terms as at, add_user as au,
    get_user_count as guc, get_active_users as gau,
)
from pyrogram import filters
from pyrogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    LinkPreviewOptions, InputMediaPhoto,
)
try:
    from pyrogram.enums import ButtonStyle as BS
except ImportError:
    BS = None

PURL = "https://graph.org/Privacy-Policy---StringX-02-11-3"
IMG = "https://files.catbox.moe/wtkynt.png"
CURL = "https://t.me/iwantandroid"


PTXT = (
    "<b>Privacy Policy & Terms of Use</b>\n\n"
    "Before using this bot, please review our terms.\n\n"
    "<b>What we store:</b>\n"
    "  - Telegram user ID, username, display name\n"
    "  - Timestamp of terms acceptance\n\n"
    "<b>What we never store:</b>\n"
    "  - Phone numbers, OTP codes\n"
    "  - API ID / Hash, session strings\n"
    "  - 2FA passwords\n\n"
    "<b>Important:</b>\n"
    "  - This bot is for educational purposes only.\n"
    "  - We don't share data with third parties\n"
    "  - We are not responsible for account bans or misuse\n"
    "  - Credentials are processed in memory only\n"
    "  - You are responsible for keeping your data safe\n\n"
    "Read the full policy using the button below."
)

def _s(s):
    return {"style": s} if s and BS else {}

def m_kb(url: str = None) -> InlineKeyboardMarkup:
    r = [
        [
            InlineKeyboardButton("API Credentials", callback_data="gen_again", **_s(BS.PRIMARY if BS else None)),
            InlineKeyboardButton("Session String", callback_data="sess_again", **_s(BS.PRIMARY if BS else None)),
        ],
        [
            InlineKeyboardButton("Help & Commands", callback_data="help", **_s(BS.DEFAULT if BS else None)),
            InlineKeyboardButton("Bot Stats", callback_data="stats", **_s(BS.DEFAULT if BS else None)),
        ],
    ]
    if url:
        r.append([InlineKeyboardButton("Privacy Policy", url=url)])
    else:
        r.append([InlineKeyboardButton("Privacy Policy", callback_data="privacy", **_s(BS.DEFAULT if BS else None))])
    r.append([
        InlineKeyboardButton("Update Channel", url=CURL),
        InlineKeyboardButton("Close", callback_data="close", **_s(BS.DANGER if BS else None))
    ])
    return InlineKeyboardMarkup(r)

def t_kb(url: str = None) -> InlineKeyboardMarkup:
    r = []
    if url:
        r.append([InlineKeyboardButton("Read Full Policy", url=url)])
    r.append([
        InlineKeyboardButton("I Accept", callback_data="accept_terms", **_s(BS.SUCCESS if BS else None)),
        InlineKeyboardButton("Decline", callback_data="decline_terms", **_s(BS.DANGER if BS else None)),
    ])
    return InlineKeyboardMarkup(r)

@bot.on_message(filters.command("start") & filters.private)
@handle_errors
async def start(_, m: Message):
    u = m.from_user
    await au(u.id, u.username, u.first_name, u.last_name)
    if not await hat(u.id):
        await m.reply_text(PTXT, reply_markup=t_kb(PURL), link_preview_options=LinkPreviewOptions(is_disabled=True))
        return
    await m.reply_photo(photo=IMG, caption=f"<b>StringX</b>\n\nWelcome back, {u.first_name}.\n\nGenerate API credentials from my.telegram.org or create\nsession strings for Pyrogram and Telethon.\n\nUse the buttons below to get started.", reply_markup=m_kb(PURL))

@bot.on_callback_query(filters.regex(r"^accept_terms$"))
@handle_errors
async def at_cb(_, cb: CallbackQuery):
    u = cb.from_user
    await at(u.id)
    await cb.answer("Terms accepted")
    await cb.message.edit_text(f"<b>Terms Accepted</b>\n\nWelcome, {u.first_name}.\nYou now have full access to all features.\n\nUse the buttons below to get started.", reply_markup=m_kb(PURL), link_preview_options=LinkPreviewOptions(is_disabled=True))

@bot.on_callback_query(filters.regex(r"^decline_terms$"))
@handle_errors
async def dt_cb(_, cb: CallbackQuery):
    await cb.answer("You must accept the terms to use this bot.\nPress /start to try again.", show_alert=True)

@bot.on_message(filters.command("privacy") & filters.private)
@handle_errors
async def p_cmd(_, m: Message):
    a = await hat(m.from_user.id)
    if a:
        t = PTXT + "\n\nYou have already accepted these terms."
        r = []
        if PURL: r.append([InlineKeyboardButton("Read Full Policy", url=PURL)])
        r.append([
            InlineKeyboardButton("Back", callback_data="back_start", **_s(BS.DEFAULT if BS else None)),
            InlineKeyboardButton("Close", callback_data="close", **_s(BS.DANGER if BS else None)),
        ])
        await m.reply_text(t, reply_markup=InlineKeyboardMarkup(r), link_preview_options=LinkPreviewOptions(is_disabled=True))
    else:
        await m.reply_text(PTXT, reply_markup=t_kb(PURL), link_preview_options=LinkPreviewOptions(is_disabled=True))

@bot.on_callback_query(filters.regex(r"^privacy$"))
@handle_errors
async def p_cb(_, cb: CallbackQuery):
    await cb.answer()
    a = await hat(cb.from_user.id)
    if a:
        t = PTXT + "\n\nYou have already accepted these terms."
        r = []
        if PURL: r.append([InlineKeyboardButton("Read Full Policy", url=PURL)])
        r.append([
            InlineKeyboardButton("Back", callback_data="back_start", style=BS.DEFAULT if BS else None),
            InlineKeyboardButton("Close", callback_data="close", style=BS.DANGER if BS else None),
        ])
        await cb.message.edit_text(t, reply_markup=InlineKeyboardMarkup(r), link_preview_options=LinkPreviewOptions(is_disabled=True))
    else:
        await cb.message.edit_text(PTXT, reply_markup=t_kb(PURL), link_preview_options=LinkPreviewOptions(is_disabled=True))

HTXT = (
    "<b>Commands</b>\n\n"
    "/start      - Main menu\n/generate   - Generate API ID & Hash\n/session    - Generate session string\n"
    "/stats      - Bot statistics\n/privacy    - Privacy policy\n/cancel     - Cancel current operation\n"
    "/help       - This message\n\n<b>Session Types</b>\n\n<b>Pyrogram</b>\n"
    "Compatible with Pyrogram, Kurigram,\nPyrofork, and Hydrogram.\n\n"
    "<b>Telethon</b>\nCompatible with Telethon and its forks.\n\n"
    "<b>How It Works</b>\n\n1. Your phone number and codes are sent\n   directly to Telegram's servers.\n"
    "2. Nothing sensitive is stored in our database.\n3. Session strings are sent to your Saved\n   Messages automatically for safekeeping."
)

@bot.on_message(filters.command("help") & filters.private)
@handle_errors
async def h_cmd(_, m: Message):
    await m.reply_text(HTXT, link_preview_options=LinkPreviewOptions(is_disabled=True), reply_markup=InlineKeyboardMarkup([
        [
            InlineKeyboardButton("API Credentials", callback_data="gen_again", **_s(BS.PRIMARY if BS else None)),
            InlineKeyboardButton("Session String", callback_data="sess_again", **_s(BS.PRIMARY if BS else None)),
        ],
        [InlineKeyboardButton("Close", callback_data="close", **_s(BS.DANGER if BS else None))],
    ]))

@bot.on_callback_query(filters.regex(r"^help$"))
@handle_errors
async def h_cb(_, cb: CallbackQuery):
    await cb.answer()
    await cb.message.edit_text(HTXT, link_preview_options=LinkPreviewOptions(is_disabled=True), reply_markup=InlineKeyboardMarkup([
        [
            InlineKeyboardButton("API Credentials", callback_data="gen_again", **_s(BS.PRIMARY if BS else None)),
            InlineKeyboardButton("Session String", callback_data="sess_again", **_s(BS.PRIMARY if BS else None)),
        ],
        [InlineKeyboardButton("Back", callback_data="back_start", **_s(BS.DEFAULT if BS else None))],
    ]))

@bot.on_message(filters.command("stats") & filters.private)
@handle_errors
async def s_cmd(_, m: Message):
    t = await guc()
    a7 = await gau(7)
    a24 = await gau(1)
    await m.reply_text(f"<b>Bot Statistics</b>\n\nTotal Users      : <code>{t}</code>\nActive (24h)     : <code>{a24}</code>\nActive (7 days)  : <code>{a7}</code>\n", reply_markup=InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Refresh", callback_data="stats", **_s(BS.DEFAULT if BS else None)),
            InlineKeyboardButton("Close", callback_data="close", **_s(BS.DANGER if BS else None)),
        ],
    ]))

@bot.on_callback_query(filters.regex(r"^stats$"))
@handle_errors
async def s_cb(_, cb: CallbackQuery):
    t = await guc()
    a7 = await gau(7)
    a24 = await gau(1)
    await cb.answer()
    await cb.message.edit_text(f"<b>Bot Statistics</b>\n\nTotal Users      : <code>{t}</code>\nActive (24h)     : <code>{a24}</code>\nActive (7 days)  : <code>{a7}</code>\n", reply_markup=InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Refresh", callback_data="stats", **_s(BS.DEFAULT if BS else None)),
            InlineKeyboardButton("Back", callback_data="back_start", **_s(BS.DEFAULT if BS else None)),
        ],
    ]))

@bot.on_callback_query(filters.regex(r"^back_start$"))
@handle_errors
async def bs_cb(_, cb: CallbackQuery):
    u = cb.from_user
    await cb.answer()
    await cb.message.edit_media(InputMediaPhoto(media=IMG, caption=f"<b>StringX</b>\n\nWelcome back, {u.first_name}.\n\nGenerate API credentials from my.telegram.org or create\nsession strings for Pyrogram and Telethon.\n\nUse the buttons below to get started."), reply_markup=m_kb(PURL))

@bot.on_callback_query(filters.regex(r"^close$"))
@handle_errors
async def c_cb(_, cb: CallbackQuery):
    await cb.answer("Closed")
    await cb.message.delete()
