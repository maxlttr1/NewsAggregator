import discord
from discord.ext import commands, tasks
import yaml
from feeds import get_latest_video

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# YAML
def load_data():
    with open("data.yaml", "r") as f:
        return yaml.safe_load(f)

def save_data(data):
    with open("data.yaml", "w") as f:
        yaml.safe_dump(data, f)

# BOT COMMANDS
@bot.command()
async def subscribe(ctx, channel_id):
    data = load_data()
    if channel_id in data["subscriptions"]:
        await ctx.send("🔁 Already subscribed.")
    else:
        data["subscriptions"].append(channel_id)
        save_data(data)
        await ctx.send("✅ Subscribed to new channel.")

@bot.command()
async def unsubscribe(ctx, channel_id):
    data = load_data()
    if channel_id in data["subscriptions"]:
        data["subscriptions"].remove(channel_id)
        save_data(data)
        await ctx.send("🗑️ Unsubscribed.")
    else:
        await ctx.send("❌ Channel not in list.")

@bot.command()
async def latest(ctx):
    data = load_data()
    results = []
    for cid in data["subscriptions"]:
        video = get_latest_video(cid)
        if video:
            results.append(video["link"])
    await ctx.send("\n".join(results) or "No videos found.")

@bot.command()
async def add(ctx, url):
    data = load_data()
    if url in data["watch_later"]:
        await ctx.send("🔁 Already in Watch Later.")
    else:
        data["watch_later"].append(url)
        save_data(data)
        await ctx.send("✅ Added to Watch Later.")

@bot.command()
async def remove(ctx, url):
    data = load_data()
    if url in data["watch_later"]:
        data["watch_later"].remove(url)
        save_data(data)
        await ctx.send("🗑️ Removed from Watch Later.")
    else:
        await ctx.send("❌ Video not found.")

@bot.command()
async def show(ctx):
    data = load_data()
    if not data["watch_later"]:
        await ctx.send("📭 Watch Later list is empty.")
    else:
        await ctx.send("\n".join(data["watch_later"]))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    check_new_videos.start()

@tasks.loop(seconds=1)
async def check_new_videos():
    data = load_data()

    if "last_seen" not in data:
        data["last_seen"] = {}

    channel = None
    notify_channel_id = 1398592076379193395  
    notify_channel = bot.get_channel(notify_channel_id)
    if notify_channel is None:
        print(f"Cannot find channel with ID {notify_channel_id}")
        return

    for cid in data.get("subscriptions", []):
        video = get_latest_video(cid)
        if not video:
            continue

        last_link = data["last_seen"].get(cid)
        if video["link"] != last_link:
            await notify_channel.send(video['link'])
            data["last_seen"][cid] = video["link"]
    save_data(data)

bot.run(load_data()["bot_token"])
