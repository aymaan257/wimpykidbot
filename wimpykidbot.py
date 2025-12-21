import os
import random
import asyncio
import discord
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 1391105396910981211
STAFF_ROLE_NAME = "staffs"

intents = discord.Intents.default()
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

def has_staff_role(interaction: discord.Interaction):
    return any(role.name == STAFF_ROLE_NAME for role in interaction.user.roles)

def correct_channel(interaction: discord.Interaction):
    return locked_channel_id is None or interaction.channel_id == locked_channel_id

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"Logged in as {client.user}")

@tree.command(name="help", description="Show bot commands", guild=discord.Object(id=GUILD_ID))
async def help_cmd(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Hey, I'm Wimpy kid Bot!\n"
        "👋 I'm a bot made for Wimpy kid Fan club by <@1092411328213291148>\n\n"
        "Feel free to send help, requests, or report bugs here:\n"
        "https://discord.com/channels/1391105396910981211/1393167588380643348\n"
        "or\n"
        "https://discord.com/channels/1391105396910981211/1393172073773273129\n\n"
        "**Commands:**\n"
        "/trivia – Starts a trivia game\n"
        "/quote – Gives you a random quote\n"
        "/lock – Lock bot to a channel (staffs only)\n"
        "/unlock – Unlock bot (staffs only)"
    )

@tree.command(name="quote", description="Get a random quote", guild=discord.Object(id=GUILD_ID))
async def quote_cmd(interaction: discord.Interaction):
    if not correct_channel(interaction):
        await interaction.response.send_message("Bot is locked to another channel.", ephemeral=True)
        return
    await interaction.response.send_message(random.choice(quotes))

@tree.command(name="lock", description="Lock the bot to this channel", guild=discord.Object(id=GUILD_ID))
async def lock_cmd(interaction: discord.Interaction):
    global locked_channel_id
    if not has_staff_role(interaction):
        await interaction.response.send_message("Staffs only.", ephemeral=True)
        return
    locked_channel_id = interaction.channel_id
    await interaction.response.send_message("🔒 Bot locked to this channel.")

@tree.command(name="unlock", description="Unlock the bot", guild=discord.Object(id=GUILD_ID))
async def unlock_cmd(interaction: discord.Interaction):
    global locked_channel_id
    if not has_staff_role(interaction):
        await interaction.response.send_message("Staffs only.", ephemeral=True)
        return
    locked_channel_id = None
    await interaction.response.send_message("🔓 Bot unlocked.")

class TriviaView(discord.ui.View):
    def __init__(self, correct):
        super().__init__(timeout=15)
        self.correct = correct

        options = random.sample(list(trivia_questions.values()), k=3)
        if correct not in options:
            options[0] = correct
        random.shuffle(options)

        for opt in options:
            self.add_item(TriviaButton(opt, correct))

class TriviaButton(discord.ui.Button):
    def __init__(self, label, correct):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.correct = correct

    async def callback(self, interaction: discord.Interaction):
        if self.label == self.correct:
            msg = await interaction.response.send_message("✅ Correct!", ephemeral=False)
        else:
            msg = await interaction.response.send_message(
                f"❌ Wrong! Correct answer was **{self.correct}**", ephemeral=False
            )
        await asyncio.sleep(5)
        await interaction.delete_original_response()

@tree.command(name="trivia", description="Start a trivia game", guild=discord.Object(id=GUILD_ID))
async def trivia_cmd(interaction: discord.Interaction):
    if not correct_channel(interaction):
        await interaction.response.send_message("Bot is locked to another channel.", ephemeral=True)
        return

    question, answer = random.choice(list(trivia_questions.items()))
    view = TriviaView(answer)
    await interaction.response.send_message(f"🧠 **Trivia Time!**\n{question}", view=view)

client.run(TOKEN)

