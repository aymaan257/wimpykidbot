import os
import random
import asyncio
import discord
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN") or "YOUR_DISCORD_BOT_TOKEN_HERE"
GUILD_ID = 1391105396910981211

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

locked_channel_id = None

trivia_questions = {
    "Who is Greg's best friend?": "Rowley",
    "What is the name of Greg’s brother in the band Löded Diper?": "Rodrick",
    "What does Greg hate most in the Cheese Touch game?": "The Cheese",
    "Who is Greg's little brother?": "Manny",
    "Who does Greg try to impress by the pool in Dog Days?": "Holly Hills",
    "What is the name of the book club that Greg’s mom sets up in Dog Days?": "Reading is Fun",
    "Why was Greg trapped indoors with his family during the Christmas holidays in Cabin Fever?": "He got snowed in",
    "In The Ugly Truth, Greg’s school announces a special fundraiser for the music programme called a _____.": "Lock-in",
    "True or False: Rowley felt really sick after riding the Cranium Shaker in Dog Days.": "False",
    "Who wins Athlete of the Month in book one?": "P. Mudd",
    "Where did Rowley go on holiday in Rodrick Rules?": "Australia",
    "What’s the name of the lawn-care company that Greg and Rowley start in Dog Days?": "V.I.P Lawn Service",
    "What do the Heffleys name their dog in Dog Days?": "Sweetie",
    "What did Manny shoot out of his nose when Greg made him laugh in the car in Rodrick Rules?": "Milk",
    "True or False: Greg’s pen pal is named Mamadou.": "True",
    "In which book did Mom and Dad go away and leave Greg and Rodrick in charge for the night?": "Rodrick Rules",
    "How many people had to share the ice-cream cone that Mrs Jefferson bought while on holiday in Dog Days?": "Four",
    "True or False: Mom has a Teddy Cuddles bumper sticker on her car.": "False",
    "Where did Greg and Rowley’s family stay during their holiday in Dog Days?": "Quiet Cove",
    "What does Greg use to take his books to school in Hard Luck?": "A wheeled suitcase",
    "What is the name of Rowley’s comic strip that becomes a catchphrase?": "Zoo-wee-mama!",
    "In what type of transport does Greg want to arrive at the big Valentine’s Dance in The Last Straw?": "A limousine",
    "Why didn’t Greg, Rodrick and their dad stay at the campsite at the end of The Last Straw?": "It was raining",
    "Why did Greg pass the geography exam really easily in book one?": "He sat next to the world map"
}

quotes = [
    "I'm not crazy, okay? My reality is just different from yours. - Greg",
    "Zoo-Wee Mama! - Rowley",
    "Löded Diper forever! - Rodrick",
    "I'm always thinking about the future, you know? Because I’m gonna be famous one day. - Greg",
    "The best person I know is ME. - Greg",
    "Don’t call me lazy. I prefer the term ‘selective participation’. - Greg",
    "I’ll be famous one day, but for now I’m stuck in middle school with a bunch of morons. - Greg",
    "Me and Rowley might not be cool now, but one day people will remember us! - Greg",
    "This is not a diary, it’s a journal. - Greg",
    "You can’t expect everyone to have the same level of dedication as you. - Greg",
    "I'm not sure if I’m cut out for this whole 'growing up' thing. - Greg",
    "Löded Diper RULES! - Rodrick",
    "I’m pretty sure my family came from a long line of idiots. - Greg",
    "Maybe I’ll just wait until I’m rich and famous before I start caring about school. - Greg",
    "It’s not easy being this awesome. - Greg"
]

@client.event
async def on_ready():
    try:
        guild = discord.Object(id=GUILD_ID)
        await tree.sync(guild=guild)
        print(f"✅ Commands synced successfully to guild ID: {GUILD_ID}")
    except Exception as e:
        print("❌ Error syncing commands:", e)
    print(f"🤖 Logged in as {client.user}")

def is_locked_channel(interaction: discord.Interaction):
    global locked_channel_id
    if locked_channel_id is None:
        return True
    return interaction.channel_id == locked_channel_id

def is_admin(interaction: discord.Interaction):
    return interaction.user.guild_permissions.administrator or interaction.user == interaction.guild.owner

@tree.command(name="help", description="Show available commands", guild=discord.Object(id=GUILD_ID))
async def help_command(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)
    if not is_locked_channel(interaction):
        await interaction.followup.send("❌ This bot is locked to another channel.", ephemeral=True)
        return
    help_text = (
        "📖 **Available Commands:**\n"
        "/help - Show this message\n"
        "/trivia - Play a Wimpy Kid trivia question\n"
        "/quote - Get a random Wimpy Kid quote\n"
        "/lock - Lock the bot to this channel (Admins only)\n"
        "/unlock - Unlock the bot (Admins only)"
    )
    await interaction.followup.send(help_text)

@tree.command(name="lock", description="Lock the bot to this channel (Admins only)", guild=discord.Object(id=GUILD_ID))
async def lock(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    global locked_channel_id
    if not is_admin(interaction):
        await interaction.followup.send("❌ Only admins or the server owner can lock the bot.")
        return
    locked_channel_id = interaction.channel_id
    await interaction.followup.send(f"🔒 The bot is now locked to {interaction.channel.mention}.")

@tree.command(name="unlock", description="Unlock the bot (Admins only)", guild=discord.Object(id=GUILD_ID))
async def unlock(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    global locked_channel_id
    if not is_admin(interaction):
        await interaction.followup.send("❌ Only admins or the server owner can unlock the bot.")
        return
    locked_channel_id = None
    await interaction.followup.send("🔓 The bot is now unlocked and can respond anywhere.")

@tree.command(name="quote", description="Get a random Wimpy Kid quote", guild=discord.Object(id=GUILD_ID))
async def quote(interaction: discord.Interaction):
    await interaction.response.defer()
    if not is_locked_channel(interaction):
        await interaction.followup.send("❌ This bot is locked to another channel.", ephemeral=True)
        return
    await interaction.followup.send(random.choice(quotes))

@tree.command(name="trivia", description="Play a Wimpy Kid trivia question!", guild=discord.Object(id=GUILD_ID))
async def trivia(interaction: discord.Interaction):
    await interaction.response.defer()
    if not is_locked_channel(interaction):
        await interaction.followup.send("❌ This bot is locked to another channel.", ephemeral=True)
        return

    question = random.choice(list(trivia_questions.keys()))
    answer = trivia_questions[question]

    await interaction.followup.send(f"🧠 Trivia Time!\n{question}")

    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    try:
        msg = await client.wait_for("message", timeout=15.0, check=check)
        if msg.content.strip().lower() == answer.lower():
            await interaction.channel.send("✅ Correct!")
        else:
            await interaction.channel.send(f"❌ Wrong! The answer was **{answer}**.")
    except asyncio.TimeoutError:
        await interaction.channel.send(f"⏰ Time’s up! The answer was **{answer}**.")

if __name__ == "__main__":
    if TOKEN == "YOUR_DISCORD_BOT_TOKEN_HERE":
        print("⚠️ Please add your bot token before running this script.")
    else:
        client.run(TOKEN)
