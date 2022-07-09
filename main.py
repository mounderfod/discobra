from discord import Client
from discord.intents import Intents

bot = Client(intents=[Intents.GUILD_MESSAGES])


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user.username}")

bot.run("NzM1MTA3NDc0OTY0ODczMzM3.G6_nDX.Ctozd9eWn3xY_lGFT46uCJjrHQ9fQYRHAAD9Ic")