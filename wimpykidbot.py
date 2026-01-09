import os
import discord
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 1391105396910981211

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    # DELETE GLOBAL COMMANDS
    tree.clear_commands(guild=None)
    await tree.sync()

    # DELETE GUILD COMMANDS
    guild = discord.Object(id=GUILD_ID)
    tree.clear_commands(guild=guild)
    await tree.sync(guild=guild)

    print("✅ ALL commands wiped")
    await client.close()

client.run(TOKEN)
