import datetime
import json
import os
import platform
import sys

import discord
import pycoingecko
import requests
from discord import Activity, ActivityType
from discord.ext import tasks
from discord.ext.commands import Bot
from discord.utils import get
from pytz import timezone
from bs4 import BeautifulSoup


if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

intents = discord.Intents.default()
bot = Bot(command_prefix=config["bot_prefix"], intents=intents)
coin_api = pycoingecko.CoinGeckoAPI()
header = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36" ,
    'referer':'https://www.google.com/'
}


@bot.event
async def on_ready():
    if not status_task.is_running():
        status_task.start()
    if not send_stats.is_running():
        send_stats.start()
    print(f"Logged in as {bot.user.name}")
    print(f"Discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")


@bot.event
async def on_member_join(member):
    pass


@bot.event
async def on_message(message):
    pass


@bot.event
async def on_message_edit(message):
    pass


@bot.event
async def on_message_delete(message):
    pass


# @tasks.loop(seconds=200)
# async def send_price():
#     channel = get(bot.get_all_channels(), id=config['stats_channel'])
#     stats = coin_api.get_coin_by_id(config['coin_id'])['market_data']
#     messages = ['The current price of **CrypterToken(CRYPT)** is ', '**CrypterToken(CRYPT)** is worth ', '**CrypterToken(CRYPT)** is at ']
#     embed = discord.Embed(color=0xcafcbe, description=f"📢**Attention**\n\n{random.choice(messages)}**{'{:.12f}'.format(float(stats['current_price']['usd']))} USD**!")
#     tz = timezone('EST')
#     current_time = datetime.datetime.now(tz=tz)
#     embed.timestamp = current_time
#     await channel.send(embed=embed)


@tasks.loop(seconds=300)
async def send_stats():
#     response = requests.get('https://bscscan.com/token/0xDa6802BbEC06Ab447A68294A63DE47eD4506ACAA#balances',
#                             headers=header)
#     soup = BeautifulSoup(response.content, 'html.parser')
#     holders = (soup.find(class_='mr-3').get_text()).split(' ')[0].strip()
    channel = get(bot.get_all_channels(), id=config['stats_channel'])
    stats = coin_api.get_coin_by_id(config['coin_id'])['market_data']
    embed = discord.Embed(color=0xcafcbe, description="**🔥All Stats🔥**")
    embed.add_field(name="💵 Price", value=f"${'{:.12f}'.format(float(stats['current_price']['usd']))}")
    embed.add_field(name="📢 Volume", value=f"${'{:,}'.format(round(stats['total_volume']['usd'], 2))}")
    embed.add_field(name="🏛️ Market Cap", value=f"${round(float(stats['current_price']['usd'])*float(stats['total_supply']),1)}",
                    inline=False)
    embed.add_field(name="🧱 Supply", value=f"{stats['total_supply']} tokens")
    embed.add_field(name="📈️ 24HR Percent Change", value=f"{round(stats['price_change_percentage_24h'], 2)}%",
                    inline=False)
#     embed.add_field(name="💰 Holders", value=f'{holders} addresses')
    tz = timezone('EST')
    current_time = datetime.datetime.now(tz=tz)
    embed.timestamp = current_time
    await channel.send(embed=embed)


# @tasks.loop(minutes=1)
# async def send_chart():
#     # stats = coin_api.get_coin_market_chart_by_id(config['coin_id'], "usd", "1")['prices']
#     options = webdriver.ChromeOptions()
#     options.headless = True
#     driver = webdriver.Chrome(options=options)
#     URL = 'https://www.coingecko.com/en/coins/cryptertoken'
#
#     driver.get(URL)
#
#     S = lambda X: driver.execute_script('return document.body.parentNode.scroll' + X)
#     driver.set_window_size(S(1600), S(1600))  # May need manual adjustment
#     driver.find_element('body').screenshot('web_screenshot.png')
#     driver.quit()
#     print('screenshot saved')


@tasks.loop(seconds=30)
async def status_task():  # to set a game's status
    coin_data = coin_api.get_coin_by_id(config['coin_id'])['market_data']
    price = f"${'{:.12f}'.format(float(coin_data['current_price']['usd']))}"
    for guild in bot.guilds:
        await guild.me.edit(nick=price)
    if coin_data['price_change_percentage_24h'] < 0:
        name = f"daily {round(coin_data['price_change_percentage_24h'], 2)}% 📉"
    elif coin_data['price_change_percentage_24h'] == 0:
        name = f"daily {round(coin_data['price_change_percentage_24h'], 2)}% ↔"
    else:
        name = f"daily {round(coin_data['price_change_percentage_24h'], 2)}% 📈️"
    await bot.change_presence(activity=Activity(
        name=name, type=ActivityType.watching))

# keep_alive()
bot.run(config["bot_token"])
