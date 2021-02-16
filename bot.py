# ---------------------------------------IMPORTS------------------------------------------------------
import discord
from discord.ext import commands

import asyncpg
import os

import datetime
import constants as const

# ---------------------------------------IMPORTS------------------------------------------------------


# ---------------------------------------INITIALIZING THE BOT AND THE DATABASE------------------------------


DATABASE_URL = os.environ['DATABASE_URL']
TOKEN = os.environ['TOKEN']
PREFIX = os.environ['PREFIX']
VERSION = os.environ['VERSION']

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.dm_messages = False

bot = commands.Bot(command_prefix=PREFIX,
                   description="بوت لمنصة طورني التعليمية",
                   intents=intents,
                   case_insensitive=True,
                   help_command=None)

bot.version = VERSION


async def create_db_pool():
    bot.pg_con = await asyncpg.create_pool(DATABASE_URL)


async def init_db():
    init_users_query = "CREATE TABLE IF NOT EXISTS users ( user_id numeric NOT NULL, guild_id numeric , xp integer, time REAL)"
    init_mutes_query = "CREATE TABLE IF NOT EXISTS mutes (user_id numeric,guild_id numeric,mute_role_id numeric,expire timestamp without time zone);"
    await bot.pg_con.execute(init_users_query)
    await bot.pg_con.execute(init_mutes_query)


# ---------------------------------------INITIALIZING THE BOT AND THE DATABASE------------------------------

# ----------------------------------------LOADING COGS-------------------------------------------------
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')
        print(f"loaded cog {filename[:-3]} \n")

    else:
        print(f"Unable to load {filename[:-3]} \n")


# ----------------------------------------LOADING COGS-------------------------------------------------


# ---------------------------------------EVENTS------------------------------------------------------

@bot.event
async def on_connect():
    print(
        f"\n--------------------\n connected {bot.user.display_name}(id:{bot.user.id}) connected time:{datetime.datetime.now()}\n -------------------- \n")
    await init_db()
    print(
        f"\n--------------------\nInitialized DB {bot.user.display_name}(id:{bot.user.id}) initialized DB time:{datetime.datetime.now()}\n -------------------- \n")


@bot.event
async def on_ready():
    game = discord.Activity(type=discord.ActivityType.watching, name="6wrni.com")
    await bot.change_presence(status=discord.Status.online,
                              activity=game)
    print(
        f"\n--------------------\nLogged in as {bot.user.display_name}(id:{bot.user.id}) time:{datetime.datetime.now()}\n -------------------- \n")


@bot.event
async def on_command_error(ctx, error: Exception):
    await ctx.message.add_reaction(const.crossmark_emoji)
    print(f"Exception {error} executed in {ctx.channel}")


@bot.event
async def on_command_completion(ctx):
    print(f"Executed command {ctx.message.content} in {ctx.channel}")


@bot.event
async def on_member_join(member):
    welcome_channel = bot.get_channel(const.welcome_channel_id)
    channels_channel = bot.get_channel(const.channels_channel_id)
    mod_channel = bot.get_channel(const.mod_Channel_id)
    await welcome_channel.send(
        f" اهلا بك {member.mention} ! الرجاء زيارة {channels_channel.mention} لتتعرف على وظائف الغرف !")
    guild = bot.get_guild(const.guild_id)
    role = guild.get_role(const.new_member_role_id)
    await member.add_roles(role)
    embed = discord.Embed(color=const.default_color,desciption=f"[دخول عضو] - {member.mention}")
    embed.add_field(name="تاريخ إنشاء الحساب:",
                    value=f"{member.created_at.strftime('%a, %#d %B %Y')}\n", inline=False)
    embed.set_footer(text=f"ID:{member.id}")
    embed.set_thumbnail(url=member.avatar_url)
    await mod_channel.send(embed=embed)

@bot.event
async def on_member_remove(member: discord.Member):
    mod_channel = bot.get_channel(const.mod_Channel_id)

    embed = discord.Embed(color=const.default_color, description=f"[خروج عضو] - {member.mention}")
    embed.set_footer(text=f"ID:{member.id}")
    embed.set_thumbnail(url=member.avatar_url)
    await mod_channel.send(embed=embed)


@bot.listen('on_message')
async def on_message(message):
    if message.author.id == bot.user.id:
        return
    if message.channel.id == const.introduce_channel_id:
        if const.new_member_role_id in [role.id for role in message.author.roles]:
            role = message.guild.get_role(const.new_member_role_id)
            await message.author.remove_roles(role)


# ---------------------------------------EVENTS------------------------------------------------------


# ---------------------------------------RUN------------------------------------------------------
bot.loop.run_until_complete(create_db_pool())
bot.run(TOKEN)
# ---------------------------------------RUN------------------------------------------------------
