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
SHOP_FILE = "roles.txt"

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

locked_channel_id = None
earn_cooldowns = {}

# ---------- DATA ----------
def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE) as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def is_staff(member):
    return any(r.name == STAFF_ROLE_NAME for r in member.roles)

def locked(interaction):
    return locked_channel_id and interaction.channel_id != locked_channel_id

# ---------- TRIVIA ----------
trivia_questions = {
    "Who is Greg's best friend?": "Rowley",
    "What is the name of Greg’s brother in the band Löded Diper?": "Rodrick",
    "What does Greg hate most in the Cheese Touch game?": "The Cheese",
    "Who is Greg's little brother?": "Manny",
    "Who does Greg try to impress by the pool in Dog Days?": "Holly Hills",
    "What is the name of the book club Greg’s mom sets up in Dog Days?": "Reading is Fun",
    "Why was Greg trapped indoors in Cabin Fever?": "He got snowed in",
    "What fundraiser happens in The Ugly Truth?": "Lock-in",
    "Who wins Athlete of the Month in book one?": "P. Mudd",
    "Where did Rowley go on holiday in Rodrick Rules?": "Australia",
    "What lawn-care company do Greg and Rowley start?": "V.I.P Lawn Service",
    "What do the Heffleys name their dog?": "Sweetie",
    "What did Manny shoot out of his nose?": "Milk",
    "Where did Greg’s family stay in Dog Days?": "Quiet Cove",
    "What does Greg use to take books to school in Hard Luck?": "A wheeled suitcase",
    "What is Rowley’s comic strip catchphrase?": "Zoo-wee-mama!"
}


wrong_answers = [
    "Frank", "Susan", "Fregley", "Chirag", "Bryce",
    "California", "Florida", "Canada",
    "Book Club", "Lockdown", "Sleepover",
    "Buster", "Max", "Spot",
    "Backpack", "Bus", "Scooter",
    "Zoo-wee-wow!", "Boom!"
]

class TriviaView(discord.ui.View):
    def __init__(self, correct):
        super().__init__(timeout=15)
        self.correct = correct
        choices = {correct}
        while len(choices) < 4:
            choices.add(random.choice(wrong_answers))

        for c in random.sample(list(choices), 4):
            self.add_item(TriviaButton(c, correct))

        self.add_item(StopButton())

    async def disable_all(self):
        for i in self.children:
            i.disabled = True

    async def on_timeout(self):
        await self.disable_all()

class TriviaButton(discord.ui.Button):
    def __init__(self, label, correct):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.correct = correct

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        await view.disable_all()
        await interaction.response.edit_message(view=view)

        if self.label == self.correct:
            await interaction.followup.send("✅ Correct!", ephemeral=True)
            await start_trivia(interaction)
        else:
            await interaction.followup.send(f"❌ Wrong! Answer: **{self.correct}**", ephemeral=True)

class StopButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Stop", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="🛑 Trivia stopped.", view=None)

async def start_trivia(interaction):
    q, a = random.choice(list(trivia_questions.items()))
    await interaction.followup.send(f"🧠 **Trivia Time!**\n{q}", view=TriviaView(a))

@tree.command(name="trivia", guild=discord.Object(id=GUILD_ID))
async def trivia(interaction: discord.Interaction):
    if locked(interaction):
        return await interaction.response.send_message("🔒 Bot is locked.", ephemeral=True)
    await interaction.response.send_message("Starting trivia...", ephemeral=True)
    await start_trivia(interaction)

# ---------- QUOTES ----------
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

@tree.command(name="quote", guild=discord.Object(id=GUILD_ID))
async def quote(interaction):
    if locked(interaction):
        return await interaction.response.send_message("🔒 Bot is locked.", ephemeral=True)
    await interaction.response.send_message(random.choice(quotes))

# ---------- HELP ----------
@tree.command(name="help", guild=discord.Object(id=GUILD_ID))
async def help_cmd(interaction):
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
        "/unlock – Unlock bot (staffs only)\n"
        "/shop - Buy items from the shop by using mom bucks!"
    )

# ---------- MOM BUCKS ----------
@tree.command(name="earn", guild=discord.Object(id=GUILD_ID))
async def earn(interaction):
    uid = str(interaction.user.id)
    now = time.time()

    if uid in earn_cooldowns and now - earn_cooldowns[uid] < 3600:
        return await interaction.response.send_message("⏳ 1 hour cooldown.", ephemeral=True)

    data = load_data()
    amount = random.randint(50, 67)
    data[uid] = data.get(uid, 0) + amount
    save_data(data)

    earn_cooldowns[uid] = now
    await interaction.response.send_message(f"💰 You earned **{amount} Mom Bucks**!")

@tree.command(name="balance", guild=discord.Object(id=GUILD_ID))
async def balance(interaction, user: discord.Member = None):
    data = load_data()
    if user and is_staff(interaction.user):
        await interaction.response.send_message(f"{user.mention} has **{data.get(str(user.id),0)} Mom Bucks**")
    else:
        await interaction.response.send_message(f"You have **{data.get(str(interaction.user.id),0)} Mom Bucks**")

@tree.command(name="addbucks", guild=discord.Object(id=GUILD_ID))
async def addbucks(interaction, user: discord.Member, amount: int):
    if not is_staff(interaction.user):
        return await interaction.response.send_message("❌ Staffs only.", ephemeral=True)
    data = load_data()
    data[str(user.id)] = data.get(str(user.id), 0) + amount
    save_data(data)
    await interaction.response.send_message("✅ Updated.")

# ---------- LOCK ----------
@tree.command(name="lock", guild=discord.Object(id=GUILD_ID))
async def lock(interaction):
    global locked_channel_id
    if not is_staff(interaction.user):
        return await interaction.response.send_message("❌ Staffs only.", ephemeral=True)
    locked_channel_id = interaction.channel_id
    await interaction.response.send_message("🔒 Bot locked here.")

@tree.command(name="unlock", guild=discord.Object(id=GUILD_ID))
async def unlock(interaction):
    global locked_channel_id
    if not is_staff(interaction.user):
        return await interaction.response.send_message("❌ Staffs only.", ephemeral=True)
    locked_channel_id = None
    await interaction.response.send_message("🔓 Bot unlocked.")

# ---------- SHOP ----------
def load_shop():
    items = []
    with open(SHOP_FILE) as f:
        for line in f:
            name, price = line.strip().split("|")
            items.append((name, int(price)))
    return items

class ShopSelect(discord.ui.Select):
    def __init__(self, items):
        super().__init__(
            placeholder="Buy items here!",
            options=[discord.SelectOption(label=n, description=f"{p} Mom Bucks") for n,p in items]
        )
        self.items = dict(items)

    async def callback(self, interaction):
        item = self.values[0]
        price = self.items[item]
        data = load_data()
        uid = str(interaction.user.id)

        if data.get(uid,0) < price:
            return await interaction.response.send_message("❌ Not enough Mom Bucks.", ephemeral=True)

        role = discord.utils.get(interaction.guild.roles, name=item)
        if not role:
            return await interaction.response.send_message("❌ Role missing.", ephemeral=True)

        data[uid] -= price
        save_data(data)
        await interaction.user.add_roles(role)
        await interaction.response.send_message(f"✅ Bought **{item}**!", ephemeral=True)

class ShopView(discord.ui.View):
    def __init__(self, items):
        super().__init__(timeout=None)
        self.add_item(ShopSelect(items))

@tree.command(name="shop", guild=discord.Object(id=GUILD_ID))
async def shop(interaction):
    items = load_shop()
    bal = load_data().get(str(interaction.user.id),0)
    desc = "\n".join(f"{i+1}. **{n}** – {p}" for i,(n,p) in enumerate(items))
    embed = discord.Embed(title="🛒 Wimpy Shop", description=desc)
    embed.set_footer(text=f"Your balance: {bal} Mom Bucks")
    await interaction.response.send_message(embed=embed, view=ShopView(items))

# ---------- READY ----------
@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print("Bot ready")

client.run(TOKEN)
