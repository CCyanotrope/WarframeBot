import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from colorama import Fore

import requests
import datetime


class WeaponData():
    def __init__(self):
        self.name = "Name"
        self.description = "description"
        self.category = "Category"
        self.damage = []
        self.drops = []
        self.img = "img"


weaponTypes : list[Choice] = [Choice(name="Primary", value="Primary"), Choice(name="Secondary", value="Secondary"), 
                              Choice(name="Melee", value="Melee")]

# thumbnailLotus = discord.File("./image/LotusFlower.png", filename="thumbnailLotus.png")

primaryWeapon_api = "https://raw.githubusercontent.com/WFCD/warframe-items/refs/heads/master/data/json/Primary.json"
secondaryWeapon_api = "https://raw.githubusercontent.com/WFCD/warframe-items/refs/heads/master/data/json/Secondary.json"
meleeWeapon_api = "https://raw.githubusercontent.com/WFCD/warframe-items/refs/heads/master/data/json/Melee.json"

def attachLocalFile(imageFile : str):
    return ("attachment://" + imageFile)

def getRequest(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(Fore.LIGHTGREEN_EX + "Data successfully retrived.")
        return data
    else:
        print("Failed to reach data endpoint.")
        print(response.status_code)

def makeEmbed(weapon : WeaponData):
    weaponImg = ("https://raw.githubusercontent.com/WFCD/warframe-items/refs/heads/master/data/img/"+weapon.img)
    embedContent = discord.Embed(title=f"Weapon Search - {weapon.name}")
    # embedContent.set_thumbnail(url=attachLocalFile(thumbnailLotus.filename))
    # print(attachLocalFile(thumbnailLotus.filename))
    embedContent.set_image(url=weaponImg)
    embedContent.description = weapon.description
    return embedContent


def populateWeaponList(type : str, file):
    WeaponDataArray : list[WeaponData] = [] #holds a list of ArcaneDatas objects
   # dropLocations = list[file["components"]["drops"]]
    for weapon in file: #arcaneFile streamed directly from JSON file
        isDuplicate = False 
        # for item in WeaponDataArray: #for each weapon in the array
        #     if(weapon["name"] == item.name or (bool(weapon.get("consumeOnBuild")) == False or bool((weapon.get("category")) == False))): #if the current weapon in the wider loop matches even one value in the weapon array...
        #         isDuplicate = True #it determines if it is a duplicate!
        #         break
        if(isDuplicate==False):
            print(Fore.BLUE+f"{weapon["name"]} - {weapon["category"]}")
            temp=WeaponData()
            temp.name = weapon["name"]
            temp.img = weapon["imageName"]
            temp.category = weapon["category"]
            temp.damage = weapon["damage"]
            temp.description = weapon["description"]
            # print(weapon.keys())
            try:
                print(weapon["components"][0]["drops"])
            except:
                print("No components found!")

            # temp.drops = weapon["components"][0]["drops"]
            # for damageTypes in weapon["damage"]:
            #     temp.damage.append(damageTypes)
            # print(weapon["components"][0]["drops"])
            # for dropData in weapon["components"]["drops"]:
            #     temp.drops.append(dropData)

            WeaponDataArray.append(temp)

    # for dupeWeapons in WeaponDataArray:
    #     if(dupeWeapons)
    return WeaponDataArray

def grabWeaponData(name : str, weaponArray : list[WeaponData] = []):
    weaponRequest = WeaponData()
    requestTempName = name.replace(" ", "")
    # print("NAME TEMP: " + requestTempName)
    for data in weaponArray:
        # print(len(weaponArray))
        tempDataName = data.name.replace(" ", "")
        # print("DATA NAME TEMP: " + tempDataName)
        # print(bool(requestTempName.casefold() == tempDataName.casefold()))
        if(requestTempName.casefold() == tempDataName.casefold()):
            #print(Fore.LIGHTMAGENTA_EX + tempDataName)
            weaponRequest = data
            print(f"FULL WEAPON NAME : {weaponRequest.name}")
            return weaponRequest
    return None


primaryWeaponFile = getRequest(primaryWeapon_api)
secondaryWeaponFile = getRequest(secondaryWeapon_api)
meleeWeaponFile = getRequest(meleeWeapon_api)

# weaponList = populateWeaponList("Primary", primaryWeaponFile)




# wepTest = grabWeaponData("Acceltra", weaponList)


class WeaponCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(Fore.GREEN+f"Arcane file loaded.")


    @app_commands.command(name="weaponsearch",description="Grabs weapon data that was requested.")
    @app_commands.choices(weapontype = weaponTypes)
    async def weaponsearch(self, i:discord.Interaction, weapontype:Choice[str], weaponname:str):
        print(weapontype.value)
        match weapontype.value:
            case "Primary":
                weaponList = populateWeaponList(weapontype.value, primaryWeaponFile)
            case "Secondary":
                weaponList = populateWeaponList(weapontype.value, secondaryWeaponFile)
            case "Melee":
                weaponList = populateWeaponList(weapontype.value, meleeWeaponFile)

        requestedWeapon = grabWeaponData(weaponname, weaponList)
        weaponImg = ("https://raw.githubusercontent.com/WFCD/warframe-items/refs/heads/master/data/img/"+requestedWeapon.img)
        
        # embedContent = discord.Embed(title=f"Weapon Search - {requestedWeapon.name}")
        # # embedContent.set_thumbnail(url=attachLocalFile(thumbnailLotus.filename))
        # # print(attachLocalFile(thumbnailLotus.filename))
        # embedContent.set_image(url=weaponImg)
        # embedContent.description = requestedWeapon.description
        weaponEmbed = makeEmbed(requestedWeapon)
        thumbnailLotus = discord.File("./image/LotusFlower.png", filename="thumbnailLotus.png")
        weaponEmbed.set_thumbnail(url=attachLocalFile(thumbnailLotus.filename))
        print(requestedWeapon.drops)
        # test.set_thumbnail(url=attachLocalFile(thumbnailLotus.filename))
        await i.response.send_message(embed=weaponEmbed, file=thumbnailLotus)



async def setup(bot : commands.Bot):
    GUILD_ID = discord.Object(id=440793511588134912)
    await bot.add_cog(WeaponCog(bot),guild=GUILD_ID)