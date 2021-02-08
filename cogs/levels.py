import discord
from discord.ext import commands

import constants as const
import time


class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ----------------------------------BOT EVENTS------------------------------------------------
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.content.startswith(
                f'{self.bot.command_prefix}') or message.channel.id in const.NoXpchannels_id or const.moderator_role_id in [
            role.id for role in message.author.roles]: return

        user_id = message.author.id
        guild_id = message.guild.id

        query = "SELECT * FROM users WHERE user_id = $1 AND guild_id = $2"
        user = await self.bot.pg_con.fetch(query, user_id, guild_id)

        if not user:
            query = "INSERT INTO users (user_id, guild_id, xp, time) VALUES ($1,$2,$3,$4)"
            await self.bot.pg_con.execute(query, user_id, guild_id, 0, time.time())

        query = "SELECT * FROM users WHERE user_id = $1 AND guild_id = $2"
        user = await self.bot.pg_con.fetchrow(query, user_id, guild_id)
        if time.time() - user['time'] > 60:
            if message.mentions:
                for goodword in const.goodwords:
                    if goodword in message.content:
                        for mention in message.mentions:
                            if mention.id != message.author.id:
                                if const.moderator_role_id not in [role.id for role in mention.roles]:
                                    await message.channel.send(f"أخذ {mention.mention} زائد خمسة نقاط!")
                                    xp = user['xp'] + 5
                                    query = "UPDATE users SET xp = $1 , time = $2 WHERE user_id = $3 AND guild_id = $4"
                                    await self.bot.pg_con.execute(query, xp, time.time(), user_id, guild_id)

            xp = user['xp'] + 5
            query = "UPDATE users SET xp = $1 , time = $2 WHERE user_id = $3 AND guild_id = $4"
            await self.bot.pg_con.execute(query, xp, time.time(), user_id, guild_id)
            lvl = 0

            while True:
                if xp < ((50 * (lvl ** 2)) + (50 * (lvl - 1))):
                    break
                lvl += 1
            xp -= ((50 * ((lvl - 1) ** 2)) + (50 * (lvl - 1)))
            if xp == 0:
                await message.channel.send(f"مبروك {message.author.mention}, لقد وصلت الى المستوى {lvl} !")
                for key in const.rewarded_roles.keys():
                    if key <= lvl:
                        role = message.guild.get_role(const.rewarded_roles[key])
                        await message.author.add_roles(role)

        await self.bot.process_commands(message)

    # ----------------------------------BOT EVENTS------------------------------------------------

    # ----------------------------------RANK Command------------------------------------------------
    @commands.command(name="rank", description="إظهار XP و level للمستخدم")
    async def show_rank(self, ctx, member: discord.Member = None):
        if ctx.channel.id != const.botchannel_id and ctx.channel.id != const.private_channel_id and ctx.channel.id != const.private2_channel_id:
            bot_channel = self.bot.get_channel(const.botchannel_id)
            return await ctx.channel.send(f"لا يمكنك إستعملها هنا, إذهب الى {bot_channel.mention}!")
        member = ctx.author if not member else member
        user_id = member.id
        guild_id = ctx.guild.id

        query = "SELECT * FROM users WHERE user_id = $1 AND guild_id = $2"

        user = await self.bot.pg_con.fetch(query, user_id, guild_id)

        if not user:
            await ctx.send(f"ليس لديك XP, إرسل بعد الرسائل أولا!")

        else:
            xp = user[0]['xp']
            lvl = 0
            while True:
                if xp < ((50 * (lvl ** 2)) + (50 * (lvl - 1))):
                    break
                lvl += 1
            xp -= ((50 * ((lvl - 1) ** 2)) + (50 * (lvl - 1)))
            query = "SELECT count(*) FROM users"
            counts = await self.bot.pg_con.fetchrow(query)
            count = counts['count']
            query = "SELECT 1 + COUNT(*) AS rank FROM users WHERE xp > (SELECT xp FROM users WHERE user_id = $1 AND guild_id = $2)"
            user = await self.bot.pg_con.fetchrow(query, user_id, guild_id)
            rank = user['rank']
            if xp >= 0:
                nb_of_purple_boxes = int(xp * 20 / int(200 * ((1 / 2) * lvl)))
                nb_of_white_boxes = 20 - nb_of_purple_boxes
                embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
                embed.set_author(name=f"[Rank] - {member.display_name}")
                embed.set_thumbnail(url=member.avatar_url)
                embed.add_field(name="XP:", value=f"{xp}/{int(200 * ((1 / 2) * lvl))}", inline=True)
                embed.add_field(name='Rank:', value=f"# {rank}/{count}", inline=True)
                embed.add_field(name='Level:', value=lvl, inline=True)

                embed.add_field(name='Progress Bar:',
                                value=nb_of_purple_boxes * ":purple_square:" + nb_of_white_boxes * ":white_large_square:",
                                inline=True)
                await ctx.send(embed=embed)
            else:
                realxp = int(200 * ((1 / 2) * (lvl - 1))) + xp
                nb_of_purple_boxes = int(realxp * 20 / int(200 * ((1 / 2) * (lvl - 1))))
                nb_of_white_boxes = 20 - nb_of_purple_boxes
                embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
                embed.set_author(name=f"[Rank] - {member.display_name}")
                embed.set_thumbnail(url=member.avatar_url)
                embed.add_field(name="XP:", value=f"{realxp}/{int(200 * ((1 / 2) * (lvl - 1)))}", inline=True)
                embed.add_field(name='Rank:', value=f"# {rank}/{count}", inline=True)
                embed.add_field(name='Level:', value=lvl - 1, inline=True)
                embed.add_field(name='Progress Bar:',
                                value=nb_of_purple_boxes * ":purple_square:" + nb_of_white_boxes * ":white_large_square:",
                                inline=True)
                await ctx.send(embed=embed)

    # ----------------------------------RANK Command------------------------------------------------

    # ----------------------------------LEADERBOARD Command------------------------------------------------
    @commands.command(name="leaderboard", description="إظهار اول عشر اعضاء في السيرفير", aliases=["leadb"])
    async def leaderboard_async(self, ctx):
        if ctx.channel.id != const.botchannel_id and ctx.channel.id != const.private_channel_id and ctx.channel.id != const.private2_channel_id:
            bot_channel = self.bot.get_channel(const.botchannel_id)
            return await ctx.channel.send(f"لا يمكنك إستعملها هنا, إذهب الى {bot_channel.mention}!")
        users = await self.bot.pg_con.fetch("SELECT * FROM users ORDER BY xp desc limit 10")
        embed = discord.Embed(color=discord.Color.dark_purple(), title="**6wrni LeaderBoard**")
        rank = 1
        for user in users:
            member = ctx.guild.get_member(user['user_id'])
            xp = user['xp']
            lvl = 0
            while True:
                if xp < ((50 * (lvl ** 2)) + (50 * (lvl - 1))):
                    break
                lvl += 1
            embed.add_field(name=f"{rank}-{member.display_name}", value=f"XP: {xp} ---- Level: {lvl} \n")
            rank += 1
        await ctx.channel.send(embed=embed)

    # ----------------------------------LEADERBOARD Command------------------------------------------------

    # ----------------------------------GIVEXP Command------------------------------------------------
    @commands.command(name="give-xp", description="إضافة نسبة محددة من ال XP لعضو معين.\n\n يجب ان "
                                                  "تكون من المشرفين "
                                                  "لإستخدامها.")
    @commands.has_role(const.moderator_role_name)
    async def givexp_async(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            embed = discord.Embed(color=const.exception_color,title="خطأ:",description="القيمة المحددة يجب ان تكون اكبر من صفر!")
            return await ctx.channel.send(embed=embed)
        if amount % 5 == 0:
            user_id = member.id
            guild_id = ctx.guild.id
            query = "SELECT * FROM users WHERE user_id = $1 AND guild_id = $2"
            user = await self.bot.pg_con.fetch(query, user_id, guild_id)

            if not user:
                query = "INSERT INTO users (user_id, guild_id, xp, time) VALUES ($1,$2,$3,$4)"
                await self.bot.pg_con.execute(query, user_id, guild_id, 0, time.time())

            query = "SELECT * FROM users WHERE user_id = $1 AND guild_id = $2"
            user = await self.bot.pg_con.fetchrow(query, user_id, guild_id)

            xp = user['xp'] + amount

            query = "UPDATE users SET xp = $1 , time = $2 WHERE user_id = $3 AND guild_id = $4"
            await self.bot.pg_con.execute(query, xp, time.time(), user_id, guild_id)
            lvl = 0

            while True:
                if xp < ((50 * (lvl ** 2)) + (50 * (lvl - 1))):
                    break
                lvl += 1
            xp -= ((50 * ((lvl - 1) ** 2)) + (50 * (lvl - 1)))
            if xp == 0:
                await ctx.channel.send(f"مبروك {member.mention}, لقد وصلت الى المستوى {lvl} !")
            if xp >= 0:
                for key in const.rewarded_roles.keys():
                    if key <= lvl:
                        role = ctx.guild.get_role(const.rewarded_roles[key])
                        await member.add_roles(role)
            else:
                for key in const.rewarded_roles.keys():
                    if key <= (lvl - 1):
                        role = ctx.guild.get_role(const.rewarded_roles[key])
                        await member.add_roles(role)
            embed = discord.Embed(color=const.default_color, title=f"[Give-xp] - {member}")
            await ctx.channel.send(embed=embed)
        else:
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="القيمة المحددة يجب ان تكون من مضاعفات العدد خمسة!")
            await ctx.channel.send(embed=embed)

    @givexp_async.error
    async def givexp_async_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="لا يمكنك إستخدام هذا الأمر!")
            await ctx.channel.send(embed=embed)
        else:
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="يجب ذكر العضو والقيمة الذي يجب إضافتها!")
            await ctx.channel.send(embed=embed)

    # ----------------------------------GIVEXP Command------------------------------------------------

    # ----------------------------------DELETEXP Command------------------------------------------------
    @commands.command(name="delete-xp", description="إزالة كل ال XP لعضو معين.\n\n يجب ان "
                                                    "تكون من المشرفين "
                                                    "لإستخدامها.")
    @commands.has_role(const.moderator_role_name)
    async def deletexp_async(self, ctx, member: discord.Member):
        user_id = member.id
        guild_id = ctx.guild.id

        query = "DELETE FROM users WHERE user_id = $1 AND guild_id = $2"
        await self.bot.pg_con.execute(query, user_id, guild_id)

        for role_id in [role.id for role in member.roles]:
            if role_id in const.rewarded_roles.values():
                role = ctx.guild.get_role(role_id)
                await member.remove_roles(role)

        embed = discord.Embed(color=const.default_color, title=f"[delete-xp] - {member}")
        await ctx.channel.send(embed=embed)

    @deletexp_async.error
    async def deletexp_async_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="لا يمكنك إستخدام هذا الأمر!")
            await ctx.channel.send(embed=embed)

        else:
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="يجب ذكر العضو !")
            await ctx.channel.send(embed=embed)


# ----------------------------------DELETEXP Command------------------------------------------------

def setup(bot):
    bot.add_cog(Levels(bot))
