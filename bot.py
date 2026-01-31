import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
import ctypes.util

# ===== OPUS =====
opus = ctypes.util.find_library("opus")
if opus:
    discord.opus.load_opus(opus)

# ===== BOT =====
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ===== YTDLP =====
ytdlp_opts = {
    "format": "bestaudio/best",
    "quiet": True,
    "default_search": "ytsearch",
    "cookiefile": "cookies/cookies.txt",
}

ytdlp = yt_dlp.YoutubeDL(ytdlp_opts)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send("❌ ادخل روم صوتي")
        return
    await ctx.author.voice.channel.connect()
    await ctx.send("🎧 دخلت")

@bot.command()
async def p(ctx, *, query):
    if not ctx.voice_client:
        await ctx.invoke(join)

    vc = ctx.voice_client
    await ctx.send("🔍 جاري البحث...")

    loop = asyncio.get_event_loop()
    info = await loop.run_in_executor(
        None, lambda: ytdlp.extract_info(query, download=False)
    )

    if "entries" in info:
        info = info["entries"][0]

    url = info["url"]
    title = info.get("title", "Unknown")

    source = await discord.FFmpegOpusAudio.from_probe(url)

    vc.stop()
    vc.play(source)

    await ctx.send(f"▶️ {title}")

bot.run(os.getenv("DISCORD_TOKEN"))
