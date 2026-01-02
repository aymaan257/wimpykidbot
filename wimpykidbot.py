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

def has_staff(member: discord.Member):
    return any(role.name.lower() == STAFF_ROLE_NAME for role in member.roles)

def blocked(interaction):
    return locked_channel_id is not None and interaction.channel_id != locked_channel_id

trivia_questions = {
    "Who is Greg's best friend?": "Rowley",
    "What is the name of Greg’s brother in the band Löded Diper?": "Rodrick",
    "What does Greg hate most in the Cheese Touch game?": "The Cheese",
    "Who is Greg's little brother?": "Manny",
    "Who does Greg try to impress by the pool in Dog Days?": "Holly Hills",
    "What is the name of the book club that Greg’s mom sets up in Dog Days?": "Reading is Fun",
    "Why was Greg trapped indoors with his family during Cabin Fever?": "He got snowed in",
    "In The Ugly Truth, what fundraiser happens?": "Lock-in",
    "Who wins Athlete of the Month in book one?": "P. Mudd",
    "Where did Rowley go on holiday in Rodrick Rules?": "Australia",
    "What lawn-care company do Greg and Rowley start?": "V.I.P Lawn Service",
    "What do the Heffleys name their dog?": "Sweetie",
    "What did Manny shoot out of his nose?": "Milk",
    "Where did Greg’s family stay in Dog Days?": "Quiet Cove",
    "What does Greg use to take books to school in Hard Luck?": "A wheeled suitcase",
    "What is Rowley’s comic strip catchphrase?": "Zoo-wee-mama!"
}

ALL_ANSWERS = list(trivia_questions.values())

class TriviaView(discord.ui.View):
    def __init__(self, interaction, correct):
        super().__init__(timeout=15)
        self.interaction = interaction
        self.correct = correct

        wrong = random.sample([a for a in ALL_ANSWERS if a != correct], 3)
        options = wrong + [correct]
        random.shuffle(options)

        for opt in options:
            self.add_item(TriviaButton(opt, correct))

        self.add_item(StopButton())

    async def on_timeout(self):
        await self.interaction.edit_original_response(
            content=f"⏰ Time’s up! Answer was **{self.correct}**",
            view=None
        )

class TriviaButton(discord.ui.Button):
    def __init__(self, label, correct):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.correct = correct

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != interaction.message.interaction.user:
            await interaction.response.send_message("Not your trivia.", ephemeral=True)
            return

        if self.label == self.correct:
            await interaction.response.edit_message("✅ Correct! Next question...", view=None)
            await start_trivia(interaction)
        else:
            await interaction.response.edit_message(
                f"❌ Wrong! Answer was **{self.correct}**",
                view=None
            )

class StopButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Stop", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message("🛑 Trivia stopped.", view=None)

async def start_trivia(interaction):
    if blocked(interaction):
        return
    question, answer = random.choice(list(trivia_questions.items()))
    await interaction.followup.send(
        f"🧠 **Trivia**\n{question}",
        view=TriviaView(interaction, answer)
    )

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

@tree.command(name="help", guild=discord.Object(id=GUILD_ID))
async def help_cmd(interaction: discord.Interaction):
    if blocked(interaction):
        await interaction.response.send_message("🔒 Bot locked.", ephemeral=True)
        return
    await interaction.response.send_message(
        "Hey, I'm Wimpy kid Bot!\n"
        "👋 I'm a bot made for Wimpy kid Fan club by <@1092411328213291148>\n\n"
        "Feel free to send help,requests,found a bug, have suggestions or feedback, or have any questions/inquiries!\n"
        "https://discord.com/channels/1391105396910981211/1393167588380643348\n"
        "or\n"
        "https://discord.com/channels/1391105396910981211/1393172073773273129\n\n"
        "**Commands:**\n"
        "/trivia – Starts a trivia game\n"
        "/quote – Gives you a random quote\n"
        "/balance – Check Mom Bucks\n"
        "/earn – Earn Mom Bucks (1h cooldown)\n"
        "/lock – Lock bot to a channel (staffs only)\n"
        "/unlock – Unlock bot (staffs only)"
    )

@tree.command(name="quote", guild=discord.Object(id=GUILD_ID))
async def quote(interaction: discord.Interaction):
    if blocked(interaction):
        await interaction.response.send_message("🔒 Bot locked.", ephemeral=True)
        return
    await interaction.response.send_message(random.choice(quotes))

@tree.command(name="trivia", guild=discord.Object(id=GUILD_ID))
async def trivia(interaction: discord.Interaction):
    if blocked(interaction):
        await interaction.response.send_message("🔒 Bot locked.", ephemeral=True)
        return
    await interaction.response.send_message("Starting trivia...")
    await start_trivia(interaction)

@tree.command(name="balance", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="Staff only: check another user's Mom Bucks")
async def balance(interaction: discord.Interaction, user: discord.Member = None):
    data = load_data()

    if user:
        if not has_staff(interaction.user):
            await interaction.response.send_message("❌ Staffs only.", ephemeral=True)
            return
        amount = data.get(str(user.id), 0)
        await interaction.response.send_message(
            f"💵 {user.mention} has **{amount} Mom Bucks**."
        )
    else:
        amount = data.get(str(interaction.user.id), 0)
        await interaction.response.send_message(
            f"💵 You have **{amount} Mom Bucks**."
        )

@tree.command(name="earn", guild=discord.Object(id=GUILD_ID))
async def earn(interaction: discord.Interaction):
    now = asyncio.get_event_loop().time()
    uid = str(interaction.user.id)

    if uid in earn_cooldowns and now - earn_cooldowns[uid] < 3600:
        await interaction.response.send_message("⏳ You must wait 1 hour.", ephemeral=True)
        return

    data = load_data()
    amount = random.randint(50, 67)
    data[uid] = data.get(uid, 0) + amount
    save_data(data)

    earn_cooldowns[uid] = now
    await interaction.response.send_message(f"💰 You earned **{amount} Mom Bucks**!")

@tree.command(name="addbucks", guild=discord.Object(id=GUILD_ID))
async def addbucks(interaction: discord.Interaction, user: discord.Member, amount: int):
    if not has_staff(interaction.user):
        await interaction.response.send_message("❌ Staffs only.", ephemeral=True)
        return
    data = load_data()
    uid = str(user.id)
    data[uid] = data.get(uid, 0) + abs(amount)
    save_data(data)
    await interaction.response.send_message(f"✅ Added Mom Bucks to {user.mention}")

@tree.command(name="lock", guild=discord.Object(id=GUILD_ID))
async def lock(interaction: discord.Interaction):
    global locked_channel_id
    if not has_staff(interaction.user):
        await interaction.response.send_message("❌ Staffs only.", ephemeral=True)
        return
    locked_channel_id = interaction.channel_id
    await interaction.response.send_message("🔒 Bot locked to this channel.")

@tree.command(name="unlock", guild=discord.Object(id=GUILD_ID))
async def unlock(interaction: discord.Interaction):
    global locked_channel_id
    if not has_staff(interaction.user):
        await interaction.response.send_message("❌ Staffs only.", ephemeral=True)
        return
    locked_channel_id = None
    await interaction.response.send_message("🔓 Bot unlocked.")

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print("Bot ready")

client.run(TOKEN)
