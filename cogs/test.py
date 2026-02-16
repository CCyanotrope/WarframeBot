import discord
from discord import app_commands
from discord.ext import commands

from colorama import Fore
#from main import bot, GUILD_ID

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(Fore.GREEN+f"Cog file loaded.")
        

    @app_commands.command(name="cogslash", description="Test for a cog command.")
    async def cogslash(self, i: discord.Interaction):
        await i.response.send_message("Cog test successful.")

async def setup(bot):
    GUILD_ID = discord.Object(id=440793511588134912)
    await bot.add_cog(Test(bot),guild=GUILD_ID)
    
    
