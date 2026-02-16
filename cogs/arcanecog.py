import discord

from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
import requests
from colorama import Fore

import datetime
import time

GUILD_ID = discord.Object(id=440793511588134912)

class ArcaneData:
    def __init__(self):
        self.name = "name"
        self.rarity = "rarity"
        self.type = "type"
        self.drops = []
        self.levelStats = []
        self.img = "image"

arcanes_api = "https://raw.githubusercontent.com/WFCD/warframe-items/refs/heads/master/data/json/Arcanes.json"

typeList : list[Choice] = [Choice(name="Warframe Arcane",value="Warframe Arcane"),
                                        Choice(name="Primary Arcane",value="Primary Arcane"),
                                        Choice(name="Secondary Arcane",value="Secondary Arcane"),
                                        Choice(name="Melee Arcane", value="Melee Arcane"), 
                                        Choice(name="Zaw Arcane", value="Zaw Arcane")]




# retrieve url api using requests.get imported from the requests library
def getRequest(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(Fore.LIGHTGREEN_EX + "Data successfully retrived.")
        return data
    else:
        print("Failed to reach data endpoint.")
        print(response.status_code)

arcaneFile = getRequest(arcanes_api)

def populateArcaneList(arcaneType : str):
    ArcaneDataArray : list[ArcaneData] = [] #holds a list of ArcaneDatas objects
    print(arcaneType)
    for arcane in arcaneFile: #arcaneFile streamed directly from JSON file
        dupeArc = False
        if(arcane["type"] == arcaneType): #check if the arcane is from a warframe
            for item in ArcaneDataArray: #for each arcane in the array
                if(arcane["name"] == item.name or (bool(arcane.get("levelStats")) == False or bool((arcane.get("rarity")) == False))): #if the current arcane in the wider loop matches even one value in the arcane array...
                    dupeArc = True #it determines if it is a duplicate!
                    break
            if(dupeArc==False):
                temp=ArcaneData()
                temp.name = arcane["name"]
                temp.img = arcane["imageName"]
                temp.type = arcane["type"]
                for stats in arcane["levelStats"]:
                    temp.levelStats.append(str(stats["stats"]))

                for dropLocations in arcane["drops"]:
                    temp.drops.append(dropLocations)

                if(bool(arcane.get("rarity")) == False):
                    temp.rarity = "Common"
                else:
                    temp.rarity = arcane["rarity"]
                ArcaneDataArray.append(temp)
    return ArcaneDataArray


def grabArcaneData(name : str, arcaneArray : list[ArcaneData] = []):
    fullArcane = ArcaneData()

    tempName = name.replace(" ", "")
    # print("NAME TEMP: " + tempName)
    for data in arcaneArray:
        # print(len(arcaneArray))
        tempDataName = data.name.replace(" ", "")
        # print("DATA NAME TEMP: " + tempDataName)
        # print(bool(tempName.casefold() == tempDataName.casefold()))
        if(tempName.casefold() == tempDataName.casefold()):
            fullArcane = data
            print(f"FULL ARCANE NAME : {fullArcane.name}")
            return fullArcane
    return None



class ArcaneCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(Fore.GREEN+f"Arcane file loaded.")

    #REMEMBER TO ADD "self" WHEN USING "app_commands" IN A COG!! Remember that a cog is essentially a class. Just like "bot"
    #is inside of the main file. PLEASE do not forget next time to save yourself a headache...
    #TODO: Continue testing for any errors. Otherwise, 
    @app_commands.command(name="arcanesearch", description="Grabs Arcane Data using the name of the Arcane.")
    @app_commands.choices(arcanetypes = typeList)
    async def arcanesearch(self, i:discord.Interaction,arcanetypes:Choice[str], arcanename:str, allranks:bool = False):

        arcaneList = populateArcaneList(arcanetypes.value)
        requestedArcane = grabArcaneData(arcanename, arcaneList)
        print(requestedArcane)
        if(requestedArcane!=None):
            
            arcaneImg = ("https://raw.githubusercontent.com/WFCD/warframe-items/refs/heads/master/data/img/"+requestedArcane.img)
            match requestedArcane.rarity:
                case "Common":
                    embedColour = discord.Color.from_rgb(160, 82, 45)
                case "Uncommon":
                    embedColour = discord.Color.from_rgb(192, 192, 192)
                case "Rare":
                    embedColour = discord.Color.from_rgb(212,175,55)
                case "Legendary":
                    embedColour = discord.Color.from_rgb(230,252,255)
            
            arcaneEmbed = discord.Embed(title=f"Arcane Search - {requestedArcane.name}", color=embedColour)
            arcaneEmbed.set_thumbnail(url=arcaneImg)

            if(allranks==True):
                rankArray = []
                for index,levels in enumerate(requestedArcane.levelStats):
                        tempStr = (f"**Rank {index}**\n- {levels}\n")
                        print(tempStr)
                        rankArray.append(tempStr)
                x = "".join(rankArray)
                arcaneEmbed.description = x   
            else:
                arcaneEmbed.description = str(f"- **Unranked**: {requestedArcane.levelStats[0]} \n- **Max Rank**: {requestedArcane.levelStats[len(requestedArcane.levelStats)-1]}")

            arcaneLink = requestedArcane.name.replace(" ", "_")
            arcaneEmbed.add_field(name="Rarity", value=requestedArcane.rarity, inline=False)
            arcaneEmbed.add_field(name="Arcane Type", value=requestedArcane.type, inline=False)
            arcaneEmbed.add_field(name="Warframe Wiki Link", value=("https://wiki.warframe.com/w/"+arcaneLink), inline=False)
            
            dropEmbed = discord.Embed(title=f"Drop Locations & Chance", color=embedColour)
            dropEmbed.set_thumbnail(url=arcaneImg)

            dropLocationArray = []

            for dropLocations in requestedArcane.drops:
                tempStr = (f"- **{dropLocations["location"]}**\n  * Drop Chance: %{round(100*(dropLocations["chance"]), 1)} \n")
                dropLocationArray.append(tempStr)
                print(f"{dropLocations["location"]} + %{round(100*(dropLocations["chance"]), 1)}")
                
            joinedArray = "".join(dropLocationArray)
            dropEmbed.description = joinedArray
            # arcaneEmbed.timestamp = datetime.datetime.now()
            dropEmbed.timestamp = datetime.datetime.now()
            
            embedArray = discord.embeds = [arcaneEmbed, dropEmbed]
            await i.response.send_message(embeds=embedArray)
            #await i.response.send_message(embed=dropEmbed)
        else:
            await i.response.send_message("Information was not found! Please try again.")
        

async def setup(bot : commands.Bot):
    GUILD_ID = discord.Object(id=440793511588134912)
    await bot.add_cog(ArcaneCog(bot),guild=GUILD_ID)
    
    
