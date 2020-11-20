from discord.ext import commands
import os
import traceback

import discord
import random
import asyncio
import requests
import mapchip_analyzer as mca

bot = commands.Bot(command_prefix='/')
token = os.environ['DISCORD_BOT_TOKEN']


@bot.event
async def on_command_error(ctx, error):
    orig_error = getattr(error, "original", error)
    error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
    await ctx.send(error_msg)


@bot.command()
async def ping(ctx):
    await ctx.send('pong')

def download_img(url, save_fname):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(save_fname, 'wb') as f:
            f.write(r.content)

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
        fname = msg.attachments[0].filename
        download_img(msg.attachments[0].url, "image.png")
        map_img = mca.crop_area("image.png", mca.xbar_path)
        arr = mca.decide_mapchip(map_img)
        await msg.channel.send(mca.convert_to_sim(arr))


bot.run(token)
