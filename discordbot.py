from discord.ext import commands
import os
import traceback

import discord
import random
import asyncio
import requests
import mapchip_analyzer as mca

client = discord.Client()
TOKEN = os.environ['DISCORD_BOT_TOKEN']

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(msg):
    if not client.user in msg.mentions: # respond only when mentioned
        return
    if msg.author.bot: # don't respond to bots
        return

    if msg.attachments:
        try:
            attachment = msg.attachments[0]
            print(attachment.filename)
            await attachment.save("image.png")
            map_img = mca.crop_area("image.png", mca.xbar_path)
            arr = mca.decide_mapchip(map_img)
            await msg.channel.send(mca.convert_to_sim(arr))
        except:
            await msg.channel.send("error")
        


client.run(TOKEN)
