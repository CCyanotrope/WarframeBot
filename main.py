import discord
from discord import app_commands
from discord.ext import commands  # importing commands from "discord extension"

import requests
import logging  # logging the content from what is running

# module allows us to load environment variable files
from dotenv import load_dotenv

from colorama import Fore

import json

#from cogs import arcanecog 

import os
import asyncio
import datetime
import time

class ArcaneData:
    def __init__(self):
        self.name = "name"
        self.rarity = "rarity"
        self.type = "type"
        self.drops = []
        self.levelStats = []
        self.img = "image"


load_dotenv()
token = os.getenv("BOT_TOKEN")
GUILD_ID = discord.Object(id=440793511588134912)

handler = logging.FileHandler(filename="WarframeBot.log", encoding="utf-8", mode="w")
# allows a bot to subscribe to specific buckets of events.
intents = discord.Intents.default()

arcanes_api = "https://raw.githubusercontent.com/WFCD/warframe-items/refs/heads/master/data/json/Arcanes.json"
worldState_api = "https://api.warframe.com/cdn/worldState.php"



def attachLocalFile(imageFile : str):
    return ("attachment://" + imageFile)

#print(attachLocalFile(thumbnailLotus.filename))

# allows the bots to function without triggering frequent events like presence and "is typing..."
def permissions():
    intents.typing = False
    intents.presences = False
    intents.message_content = True
    intents.members = True
    intents.message_content = True
    return intents

bot = commands.Bot(command_prefix="!", intents=permissions())


# for fileName in os.listdir("./image"):
#     print(fileName)


async def LoadCog():
    # for loop actually grabs file name and is able to be loaded.
    for fileName in os.listdir("./cogs"):
        if fileName.endswith(".py"):
            await bot.load_extension(f"cogs.{fileName[:-3]}")
            print(Fore.CYAN + f"{fileName} loaded.")
    cog = bot.get_cog("ArcaneCog")
    commands = cog.get_app_commands()
    print([c.name for c in commands])

# retrieve url api using requests.get imported from the requests library
def getRequest(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
        print(Fore.LIGHTGREEN_EX + "Data successfully retrived.")
    else:
        print("Failed to reach data endpoint.")
        print(response.status_code)

worldStateData = getRequest(worldState_api)
voidTrader = worldStateData["VoidTraders"]
primeTrader = worldStateData["PrimeVaultTraders"]

def timeConversion(time):
    days = int(time // 86400)
    hours = int((time // 3600)) % 24
    minutes = int((time // 60)) % 60
    seconds = int(time) % 60
    return f"{days} days, {hours} hours, {minutes} minutes, and {seconds} seconds."

@bot.tree.command(name="barowhen", description="When and where does Baro Ki Teer come back?", guild=GUILD_ID)
async def barowhen(i: discord.Interaction):
    # Baro's Unix Time is stored in miliseconds.
    baroArrivalDate = int(voidTrader[0]["Activation"]["$date"]["$numberLong"])/ 1000
    baroLeaveDate = int(voidTrader[0]["Expiry"]["$date"]["$numberLong"])/ 1000
    currentUnixTime = int(time.time())
    # Time is calculated in seconds. Do the usual mathematics to convert time into specific formats.

    #TODO: make code easier to read - make code more modular for fixes. IMPLEMENT - When Baro Ki Teer is present at a relay.

    baroArrivalFromNow = baroArrivalDate - currentUnixTime

    print(baroArrivalFromNow)

    timeStr = timeConversion(baroArrivalFromNow)


    if voidTrader[0]["Node"] == "EarthHUB":
        relay = "Strata Relay (Earth)"
    elif voidTrader[0]["Node"] == "MercuryHUB":
        relay = "Larunda Relay (Mercury)"
    elif voidTrader[0]["Node"] == "PlutoHUB":
        relay = "Orcus Relay (Pluto)"
    
        
   
    baroImg = discord.File("./image/Baro1.png", filename="baro.png")
    thumbnailLotus = discord.File("./image/LotusFlower.png", filename="thumbnailLotus.png")
    #mrFooter = discord.File("./image/HDmrfrog.webp", filename="HDmrfrog.webp")
    #print(thumbnail.filename)
    embedBaro = discord.Embed(title="Where's Baro?", color=discord.Color.blue())
    embedBaro.timestamp = datetime.datetime.now()
    embedBaro.set_thumbnail(url=attachLocalFile(thumbnailLotus.filename))
    embedBaro.set_image(url='attachment://'+baroImg.filename)
    #embedBaro.set_footer(text="hello im mr frog", icon_url="attachment://HDmrfrog.webp")
    if(baroArrivalFromNow <= 0):
        baroLeaveDateTime = datetime.datetime.fromtimestamp(baroLeaveDate)
        baroLeaveFromNow =  baroLeaveDate - currentUnixTime
        baroExpireStr = timeConversion(baroLeaveFromNow)
        embedBaro.description = f"### Baro Ki Teer is at the __{relay}__ until {baroLeaveDateTime} (UTC+00)\n **({baroExpireStr})**"

    else:
        baroDateTime = datetime.datetime.fromtimestamp(baroArrivalDate)
        embedBaro.description = f"### Baro Ki Teer will return to the __{relay}__ on {baroDateTime} (UTC+00)\n **({timeStr})**"



    # files[] need to be used as file only uses a single file for the entirety of the embed
    # await i.response.defer(thinking=True)
    # asyncio.sleep(5)
    # await i.followup.send(embed=embedBaro, files=[baroImg, thumbnailLotus])


    await i.response.send_message(embed=embedBaro, files=[baroImg, thumbnailLotus])


@bot.tree.command(name="bingbong", description="what does this button do? :0", guild=GUILD_ID)
async def bingbong(interaction: discord.Interaction):
    await interaction.response.send_message(f"ITS HIM", file=discord.File("./image/bingbong.jpg", spoiler=True))


# SYNC MAIN BOT TO ALLOW SLASH COMMANDS TO WORK AT CURRENT STATE


@bot.tree.command(name="sync", description="Syncs the bot to the local server.", guild=GUILD_ID)
async def sync(i: discord.Interaction):
    await i.response.defer(thinking=True)

    # please note that it takes time to synced bot trees
    synced = await bot.tree.sync(guild=GUILD_ID)
    print(Fore.LIGHTBLUE_EX + f"Synced {len(synced)} commands to guild {GUILD_ID.id}.")

    # followups can be used while the bot is defered?
    await i.followup.send("Process complete!")
    # guild = discord.Object(id=440793511588134912)


@bot.tree.command(name="assign", description="assign yourself a role", guild=GUILD_ID)
async def assign(i: discord.Interaction, role: discord.Role):

    isAdmin = False
    hasRole = False
    userList = i.user.roles
    userListLength = len(i.user.roles)

    #    for a in range(userListLength):
    #       if (userList[a]._permissions == 0x8):
    #          print(f"Role {userList[a].name}, is an admin")
    #         isAdmin = True
    #        break

    for r in userList:

        if (r == role):
            hasRole = True
            print(f"Do you already have {role}? {hasRole}")
            break
        else:
            if r._permissions == 0x8:
                print(f"Role {r.name}, is an admin")
                isAdmin = True
            else:
                print(f"Role {r.name} is not an admin role.")

    if isAdmin == True:
        await i.user.add_roles(role)
        await i.response.send_message(f"{i.user.mention}, you have been granted the role of {role}.")
    elif(isAdmin | hasRole):
        await i.response.send_message(f"{i.user.mention}, you already have the role of {role}.")

    else:
        await i.response.send_message(f"{i.user.mention}, you do not have the permissions for this command.")


@bot.command()
async def sync(ctx):
    synced = await bot.tree.sync(guild=GUILD_ID)
    print(Fore.LIGHTBLUE_EX + f"Synced {len(synced)} commands to guild {GUILD_ID.id}.")
    # followups can be used while the bot is defered?
    await ctx.send("Process complete!")
    # guild = discord.Object(id=440793511588134912)


@bot.command()
async def hello(ctx):
    await ctx.send("Hello!")


"""@bot.tree.command(name="bingbong2", description="what does this button do? :0", guild=GUILD_ID)
    async def bingbong2(interaction: discord.Interaction):
    await interaction.response.send_message(f"ITS NOT HIM", file=discord.File("./image/HDmrfrog.webp", spoiler=True))"""


async def main():
    async with bot:
        await LoadCog()
       # await bot.start(token)

#LoadCog()
#asyncio.run(main())
asyncio.run(LoadCog())
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
