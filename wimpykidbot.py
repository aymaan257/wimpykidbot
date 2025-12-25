import os
import discord
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 1391105396910981211

class MyClient(discord.Client):
    async def setup_hook(self):
        tree = app_commands.CommandTree(self)
        tree.clear_commands(guild=discord.Object(id=GUILD_ID))
        await tree.sync(guild=discord.Object(id=GUILD_ID))
        print("✅ ALL COMMANDS WIPED")
        await self.close()

intents = discord.Intents.default()
client = MyClient(intents=intents)
client.run(TOKEN)
