import os
import time
import threading
import discord
import requests
from discord.ext import commands, tasks
from flask import Flask

DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8080))
POLLINATIONS_API_URL = "https://text.pollinations.ai/{prompt}"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

app = Flask(__name__)


@app.route("/")
def index():
    if bot.user:
        return f"<h2>✅ {bot.user.name} is online</h2><p>Use <code>!ask</code> or @mention the bot in Discord.</p>"
    return "<h2>⏳ Bot is starting up...</h2>", 503


@app.route("/health")
def health():
    return {"status": "ok", "bot": str(bot.user) if bot.user else None}


def run_flask():
    app.run(host="0.0.0.0", port=PORT)


@tasks.loop(minutes=5)
async def keep_alive_ping():
    try:
        response = await bot.loop.run_in_executor(
            None, lambda: requests.get(f"http://127.0.0.1:{PORT}/health", timeout=10)
        )
        print(f"[keep-alive] ping ok — {response.status_code}")
    except Exception as e:
        print(f"[keep-alive] ping failed — {e}")


def query_pollinations(prompt: str) -> str:
    try:
        url = POLLINATIONS_API_URL.format(prompt=requests.utils.quote(prompt))
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text.strip()
    except requests.exceptions.Timeout:
        return "The AI took too long to respond. Please try again."
    except requests.exceptions.RequestException as e:
        return f"Error contacting Pollinations AI: {e}"


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")
    if not keep_alive_ping.is_running():
        keep_alive_ping.start()


@bot.command(name="ask")
async def ask(ctx: commands.Context, *, prompt: str):
    """Ask the Pollinations AI a question. Usage: !ask <your question>"""
    async with ctx.typing():
        reply = await bot.loop.run_in_executor(None, query_pollinations, prompt)

    if len(reply) > 2000:
        chunks = [reply[i:i+1990] for i in range(0, len(reply), 1990)]
        for chunk in chunks:
            await ctx.reply(chunk)
    else:
        await ctx.reply(reply)


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if bot.user in message.mentions:
        prompt = message.content.replace(f"<@{bot.user.id}>", "").strip()
        if prompt:
            async with message.channel.typing():
                reply = await bot.loop.run_in_executor(None, query_pollinations, prompt)

            if len(reply) > 2000:
                chunks = [reply[i:i+1990] for i in range(0, len(reply), 1990)]
                for chunk in chunks:
                    await message.reply(chunk)
            else:
                await message.reply(reply)

    await bot.process_commands(message)


if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN:
        raise RuntimeError("DISCORD_BOT_TOKEN environment variable is not set.")

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print(f"Keep-alive server running on port {PORT}")

    bot.run(DISCORD_BOT_TOKEN)
