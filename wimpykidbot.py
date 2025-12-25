import os
import json
import random
import asyncio
import discord
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 1391105396910981211
STAFF_ROLE_NAME = "staffs"
DATA_FILE = "data.json"

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

locked_channel_id = None
earn_cooldowns = {}

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def has_staff_role(member: discord.Member):
    return any(role.name == STAFF_ROLE_NAME for role in member.roles)

trivia_questions = {
    "Who is Greg's best friend?": "Rowley",
    "What is the name of Greg’s brother in the band Löded Diper?": "Rodrick",
    "What does Greg hate most in the Cheese Touch game?": "The Cheese",
    "Who is Greg's little brother?": "Manny",
    "Who does Greg try to impress by the pool in Dog Days?": "Holly Hills",
    "What is the name of the book club that Greg’s mom sets up in Dog Days?": "Reading is Fun",
    "Why was Greg trapped indoors with his family during the Christmas holidays in Cabin Fever?": "He got snowed in",
    "In The Ugly Truth, Greg’s school announces a special fundraiser for the music programme called a _____.": "Lock-in",
    "Who wins Athlete of the Month in book one?": "P. Mudd",
    "Where did Rowley go on holiday in Rodrick Rules?": "Australia",
    "What’s the name of the lawn-care company that Greg and Rowley start in Dog Days?": "V.I.P Lawn Service",
    "What do the Heffleys name their dog in Dog Days?": "Sweetie",
    "What did Manny shoot out of his nose when Greg made him laugh in the car in Rodrick Rules?": "Milk",
    "Where did Greg and Rowley’s family stay during their holiday in Dog Days?": "Quiet Cove",
    "What does Greg use to take his books to school in Hard Luck?": "A wheeled suitcase",
    "What is the name of Rowley’s comic strip that becomes a catchphrase?": "Zoo-wee-mama!"
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

class TriviaView(discord.ui.View):
    def __init__(self, interaction, question, correct):
        super().__init__(timeout=15)
        self.interaction = interaction
        self.correct = correct

        options = [correct]
        while len(options) < 4:
            choice = random.choice(list(trivia_questions.values()))
            if choice not in options:
                options.append(choice)
        random.shuffle(options)

        for opt in options:
            self.add_item(TriviaButton(opt, correct))

        self.add_item(StopButton())

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.interaction.edit_original_response(view=self)

class TriviaButton(discord.ui.Button):
    def __init__(self, label, correct):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.correct = correct

    async def callback(self, interaction: discord.Interaction):
        if self.label == self.correct:
            await interaction.response.send_message("✅ Correct! Next question...", ephemeral=True)
            await interaction.message.delete()
            await start_trivia(interaction)
        else:
            await interaction.response.send_message(f"❌ Wrong! Correct answer was **{self.correct}**", ephemeral=True)
            await interaction.message.delete()

class StopButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Stop", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("🛑 Trivia stopped.", ephemeral=True)
        await interaction.message.delete()

async def start_trivia(interaction):
    question, answer = random.choice(list(trivia_questions.items()))
    view = TriviaView(interaction, question, answer)
    await interaction.followup.send(f"🧠 **Trivia**\n{question}", view=view)

@tree.command(name="trivia", description="Start a trivia game", guild=discord.Object(id=GUILD_ID))
async def trivia(interaction: discord.Interaction):
    if locked_channel_id and interaction.channel_id != locked_channel_id:
        await interaction.response.send_message("❌ Bot is locked to another channel.", ephemeral=True)
        return
    await interaction.response.send_message("Starting trivia...", ephemeral=True)
    await start_trivia(interaction)

@tree.command(name="quote", description="Get a random quote", guild=discord.Object(id=GUILD_ID))
async def quote(interaction: discord.Interaction):
    await interaction.response.send_message(random.choice(quotes))

@tree.command(name="help", description="Show help", guild=discord.Object(id=GUILD_ID))
async def help_cmd(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Hey, I'm Wimpy kid Bot!\n"
        "👋 I'm a bot made for Wimpy kid Fan club by <@1092411328213291148>\n\n"
        "Feel free to send help, requests, or feedback in:\n"
        "https://discord.com/channels/1391105396910981211/1393167588380643348\n"
        "or\n"
        "https://discord.com/channels/1391105396910981211/1393172073773273129\n\n"
        "**Commands:**\n"
        "/trivia – Starts a trivia game\n"
        "/quote – Gives you a random quote\n"
        "/earn – Earn mom bucks (1h cooldown)\n"
        "/balance – Check mom bucks\n"
        "/lock – Lock bot to channel (staffs)\n"
        "/unlock – Unlock bot (staffs)"
    )

@tree.command(name="lock", description="Lock bot to this channel", guild=discord.Object(id=GUILD_ID))
async def lock(interaction: discord.Interaction):
    if not has_staff_role(interaction.user):
        await interaction.response.send_message("❌ Staffs only.", ephemeral=True)
        return
    global locked_channel_id
    locked_channel_id = interaction.channel_id
    await interaction.response.send_message("🔒 Bot locked to this channel.")

@tree.command(name="unlock", description="Unlock bot", guild=discord.Object(id=GUILD_ID))
async def unlock(interaction: discord.Interaction):
    if not has_staff_role(interaction.user):
        await interaction.response.send_message("❌ Staffs only.", ephemeral=True)
        return
    global locked_channel_id
    locked_channel_id = None
    await interaction.response.send_message("🔓 Bot unlocked.")

@tree.command(name="earn", description="Earn mom bucks (1h cooldown)", guild=discord.Object(id=GUILD_ID))
async def earn(interaction: discord.Interaction):
    now = asyncio.get_event_loop().time()
    user_id = str(interaction.user.id)

    if user_id in earn_cooldowns and now - earn_cooldowns[user_id] < 3600:
        await interaction.response.send_message("⏳ You must wait 1 hour.", ephemeral=True)
        return

    data = load_data()
    earned = random.randint(50, 67)
    data[user_id] = data.get(user_id, 0) + earned
    save_data(data)

    earn_cooldowns[user_id] = now
    await interaction.response.send_message(f"💰 You earned **{earned} Mom Bucks**!")

@tree.command(name="balance", description="Check your mom bucks", guild=discord.Object(id=GUILD_ID))
async def balance(interaction: discord.Interaction):
    data = load_data()
    amount = data.get(str(interaction.user.id), 0)
    await interaction.response.send_message(f"💵 You have **{amount} Mom Bucks**.")

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print("✅ Bot ready and commands synced")

client.run(TOKEN)
