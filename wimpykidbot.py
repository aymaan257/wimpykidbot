import os
import json
import random
import time
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

# ------------------ DATA ------------------
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
    return any(role.name == STAFF_ROLE_NAME for role in member.roles)

def is_locked(interaction: discord.Interaction):
    return locked_channel_id is not None and interaction.channel_id != locked_channel_id

# ------------------ TRIVIA DATA ------------------
trivia_questions = {
    "Who is Greg's best friend?": "Rowley",
    "What is the name of Greg’s brother in the band Löded Diper?": "Rodrick",
    "What does Greg hate most in the Cheese Touch game?": "The Cheese",
    "Who is Greg's little brother?": "Manny",
    "Who does Greg try to impress by the pool in Dog Days?": "Holly Hills",
    "What is the name of the book club Greg’s mom sets up in Dog Days?": "Reading is Fun",
    "Why was Greg trapped indoors with his family during Cabin Fever?": "He got snowed in",
    "What fundraiser happens in The Ugly Truth?": "Lock-in",
    "Who wins Athlete of the Month in book one?": "P. Mudd",
    "Where did Rowley go on holiday in Rodrick Rules?": "Australia",
    "What lawn-care company do Greg and Rowley start?": "V.I.P Lawn Service",
    "What do the Heffleys name their dog?": "Sweetie",
    "What did Manny shoot out of his nose?": "Milk",
    "Where did Greg’s family stay in Dog Days?": "Quiet Cove",
    "What does Greg use to take books to school in Hard Luck?": "A wheeled suitcase",
    "What is Rowley’s comic strip catchphrase?": "Zoo-wee-mama!",
    "In what transport does Greg want to arrive at the Valentine’s Dance?": "A limousine",
    "Why didn’t Greg’s family stay at the campsite in The Last Straw?": "It was raining",
    "Why did Greg pass geography easily in book one?": "He sat next to the world map"
}

wrong_answer_pool = [
    "Frank", "Susan", "Fregley", "Chirag", "Bryce",
    "California", "Florida", "Canada",
    "Backpack", "Briefcase",
    "Spot", "Buster",
    "Sleepover", "Fundraiser",
    "Zoo-wee-wow!"
]

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

# ------------------ TRIVIA VIEW ------------------
class TriviaView(discord.ui.View):
    def __init__(self, answer, stop_flag):
        super().__init__(timeout=15)
        self.answer = answer
        self.stop_flag = stop_flag

        options = {answer}
        while len(options) < 4:
            wrong = random.choice(wrong_answer_pool)
            if wrong.lower() != answer.lower():
                options.add(wrong)

        for opt in random.sample(list(options), len(options)):
            self.add_item(TriviaButton(opt, answer, stop_flag))

        self.add_item(StopButton(stop_flag))

    async def on_timeout(self):
        for c in self.children:
            c.disabled = True

class TriviaButton(discord.ui.Button):
    def __init__(self, label, answer, stop_flag):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.answer = answer
        self.stop_flag = stop_flag

    async def callback(self, interaction: discord.Interaction):
        for c in self.view.children:
            c.disabled = True

        if self.label == self.answer:
            await interaction.response.edit_message(
                content="✅ Correct!",
                view=self.view
            )
        else:
            self.stop_flag["stop"] = True
            await interaction.response.edit_message(
                content=f"❌ Wrong! Correct answer was **{self.answer}**",
                view=self.view
            )

class StopButton(discord.ui.Button):
    def __init__(self, stop_flag):
        super().__init__(label="Stop", style=discord.ButtonStyle.danger)
        self.stop_flag = stop_flag

    async def callback(self, interaction: discord.Interaction):
        self.stop_flag["stop"] = True
        for c in self.view.children:
            c.disabled = True
        await interaction.response.edit_message(
            content="🛑 Trivia stopped.",
            view=self.view
        )

# ------------------ COMMANDS ------------------
@tree.command(name="trivia", guild=discord.Object(id=GUILD_ID))
async def trivia(interaction: discord.Interaction):
    if is_locked(interaction):
        await interaction.response.send_message("🔒 Bot is locked to another channel.", ephemeral=True)
        return

    await interaction.response.send_message("🧠 Trivia starting!")
    stop_flag = {"stop": False}

    while not stop_flag["stop"]:
        q, a = random.choice(list(trivia_questions.items()))
        view = TriviaView(a, stop_flag)
        msg = await interaction.followup.send(f"**{q}**", view=view)
        await view.wait()

@tree.command(name="quote", guild=discord.Object(id=GUILD_ID))
async def quote(interaction: discord.Interaction):
    if is_locked(interaction):
        await interaction.response.send_message("🔒 Bot is locked.", ephemeral=True)
        return
    await interaction.response.send_message(random.choice(quotes))

@tree.command(name="help", guild=discord.Object(id=GUILD_ID))
async def help_cmd(interaction: discord.Interaction):
    if is_locked(interaction):
        await interaction.response.send_message("🔒 Bot is locked.", ephemeral=True)
        return
    await interaction.response.send_message(
        "Hey, I'm Wimpy kid Bot!\n"
        ":wave: I'm a bot made for Wimpy kid Fan club by @aymaan_12567\n\n"
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

@tree.command(name="lock", guild=discord.Object(id=GUILD_ID))
async def lock(interaction: discord.Interaction):
    if not has_staff(interaction.user):
        await interaction.response.send_message("❌ Staffs only.", ephemeral=True)
        return
    global locked_channel_id
    locked_channel_id = interaction.channel_id
    await interaction.response.send_message("🔒 Bot locked to this channel.")

@tree.command(name="unlock", guild=discord.Object(id=GUILD_ID))
async def unlock(interaction: discord.Interaction):
    if not has_staff(interaction.user):
        await interaction.response.send_message("❌ Staffs only.", ephemeral=True)
        return
    global locked_channel_id
    locked_channel_id = None
    await interaction.response.send_message("🔓 Bot unlocked.")

@tree.command(name="earn", guild=discord.Object(id=GUILD_ID))
async def earn(interaction: discord.Interaction):
    if is_locked(interaction):
        await interaction.response.send_message("🔒 Bot is locked.", ephemeral=True)
        return

    now = time.time()
    uid = str(interaction.user.id)

    if uid in earn_cooldowns and now - earn_cooldowns[uid] < 3600:
        await interaction.response.send_message("⏳ 1 hour cooldown.", ephemeral=True)
        return

    data = load_data()
    amount = random.randint(50, 67)
    data[uid] = data.get(uid, 0) + amount
    save_data(data)
    earn_cooldowns[uid] = now

    await interaction.response.send_message(f"💰 You earned **{amount} Mom Bucks**!")

@tree.command(name="balance", guild=discord.Object(id=GUILD_ID))
async def balance(interaction: discord.Interaction, user: discord.Member = None):
    if is_locked(interaction):
        await interaction.response.send_message("🔒 Bot is locked.", ephemeral=True)
        return

    data = load_data()

    if user and not has_staff(interaction.user):
        await interaction.response.send_message("❌ Staffs only.", ephemeral=True)
        return

    target = user or interaction.user
    await interaction.response.send_message(
        f"💵 {target.display_name} has **{data.get(str(target.id), 0)} Mom Bucks**"
    )

@tree.command(name="addbucks", guild=discord.Object(id=GUILD_ID))
async def addbucks(interaction: discord.Interaction, user: discord.Member, amount: int):
    if not has_staff(interaction.user):
        await interaction.response.send_message("❌ Staffs only.", ephemeral=True)
        return

    data = load_data()
    uid = str(user.id)
    data[uid] = data.get(uid, 0) + abs(amount)
    save_data(data)

    await interaction.response.send_message(
        f"✅ Added **{amount} Mom Bucks** to {user.mention}"
    )

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print("Bot ready")

client.run(TOKEN)
