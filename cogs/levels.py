import discord
from discord.ext import commands

import constants as const
import random
import time


class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def threshold(self, n):
        level_threshold = 5 * (n ** 2) + 50 * n + 100
        return level_threshold

    async def rewardlevel(self, member: discord.Member, cur_level):
        if (cur_level == 5 or cur_level == 10 or cur_level == 20 or cur_level == 100):
            lvl5_role = member.guild.get_role(const.lvl5_role_id)
            lvl10_role = member.guild.get_role(const.lvl10_role_id)
            lvl20_role = member.guild.get_role(const.lvl20_role_id)
            lvl100_role = member.guild.get_role(const.lvl100_role_id)
            if (cur_level == 5):
                await member.remove_roles(lvl10_role, lvl20_role, lvl100_role)
                await member.add_roles(lvl5_role)
            elif (cur_level == 10):
                await member.remove_roles(lvl5_role, lvl100_role, lvl20_role)
                await member.add_roles(lvl10_role)
            elif (cur_level == 20):
                await member.remove_roles(lvl5_role, lvl10_role, lvl100_role)
                await member.add_roles(lvl20_role)
            elif (cur_level == 100):
                await member.remove_roles(lvl5_role, lvl10_role, lvl20_role)
                await member.add_roles(lvl100_role)
        else:
            return

    async def delete_rewarded_roles(self, member: discord.Member):
        for role_id in [role.id for role in member.roles]:
            if role_id in const.rewarded_roles_id:
                role = member.guild.get_role(role_id)
                await member.remove_roles(role)

    # ----------------------------------BOT EVENTS------------------------------------------------
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.content.startswith(
                f'{self.bot.command_prefix}') or message.channel.id in const.NoXpchannels_id: return

        author_id = str(message.author.id)
        guild_id = str(message.guild.id)
        query = "SELECT * FROM users WHERE user_id = $1 AND guild_id = $2"
        user = await self.bot.pg_con.fetch(query, author_id, guild_id)

        if not user:
            query = "INSERT INTO users (user_id, guild_id, lvl, xp,rawxp, time) VALUES ($1,$2,$3,$4,$5,$6)"
            await self.bot.pg_con.execute(query, author_id, guild_id, 1, 0, 0, time.time())

        query = "SELECT * FROM users WHERE user_id = $1 AND guild_id = $2"
        user = await self.bot.pg_con.fetchrow(query, author_id, guild_id)

        if time.time() - user['time'] > 60:
            addexp = random.randint(10, 25)
            exp = user['xp'] + addexp
            rawxp = user['rawxp'] + addexp
            query = "UPDATE users SET xp = $1 ,rawxp = $2 , time = $3 WHERE user_id = $4 AND guild_id = $5"
            await self.bot.pg_con.execute(query, exp, rawxp, time.time(), author_id, guild_id)

            if exp > self.threshold(user['lvl']):
                level = user['lvl'] + 1
                query = "UPDATE users SET xp = $1, lvl = $2 WHERE user_id= $3 AND guild_id = $4"
                await self.bot.pg_con.execute(query, 0, level, author_id, guild_id)
                await message.channel.send(f"مبروك {message.author.mention}, لقد وصلت الى المستوى {user['lvl'] + 1}.")
                await self.rewardlevel(member=message.author, cur_level=level)

        await self.bot.process_commands(message)

    # ----------------------------------BOT EVENTS------------------------------------------------

    # ----------------------------------RANK Command------------------------------------------------
    @commands.command(name="rank", description="إظهار XP و level للمستخدم")
    async def show_rank(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        member_id = str(member.id)
        guild_id = str(ctx.guild.id)

        query = "SELECT * FROM users WHERE user_id = $1 AND guild_id = $2"

        user = await self.bot.pg_con.fetch(query, member_id, guild_id)

        if not user:
            await ctx.send(f"ليس لديك XP, إرسل بعد الرسأل أولا!")

        else:
            embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
            embed.set_author(name=f"[Rank] -{member.display_name}")
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name="XP:", value=user[0]['rawxp'])
            embed.add_field(name='Level:', value=user[0]['lvl'])
            await ctx.send(embed=embed)

    # ----------------------------------RANK Command------------------------------------------------

    # ----------------------------------GIVEXP Command------------------------------------------------
    @commands.command(name="give-xp", description="إضافة نسبة محددة من ال XP لعضو معين.\n\n يجب ان "
                                                  "تكون من المشرفين "
                                                  "لإستخدامها.")
    @commands.has_role(const.moderator_role_name)
    async def givexp_async(self, ctx, member: discord.Member, amount: int):
        user_id = str(member.id)
        guild_id = str(ctx.guild.id)

        query = "SELECT * FROM users WHERE user_id = $1 AND guild_id = $2"
        user = await self.bot.pg_con.fetch(query, user_id, guild_id)

        if not user:
            query = "INSERT INTO users (user_id, guild_id, lvl, xp,rawxp, time) VALUES ($1,$2,$3,$4,$5,$6)"
            await self.bot.pg_con.execute(query, user_id, guild_id, 1, 0, 0, time.time())

        query = "SELECT * FROM users WHERE user_id = $1 AND guild_id = $2"
        user = await self.bot.pg_con.fetchrow(query, user_id, guild_id)

        user_xp = user['xp']
        user_lvl = user['lvl']
        user_rawxp = user['rawxp']

        while user_xp + amount > self.threshold(user_lvl):
            user_lvl += 1
            query = "UPDATE users SET xp = $1, lvl = $2 WHERE user_id= $3 AND guild_id = $4"
            await self.bot.pg_con.execute(query, 0, user_lvl, user_id, guild_id)
        query = "UPDATE users SET rawxp = $1 WHERE user_id= $2 AND guild_id = $3"
        await self.bot.pg_con.execute(query, user_rawxp + amount, user_id, guild_id)
        embed = discord.Embed(color=const.default_color, title=f"[give-xp] - {member}")
        embed.add_field(name="XP:", value=user_rawxp + amount)
        embed.add_field(name="Level:", value=user_lvl)
        embed.set_thumbnail(url=member.avatar_url)
        await self.rewardlevel(member=member, cur_level=user_lvl)
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

    @commands.command(name="delete-xp", description="إزالة كل ال XP لعضو معين.\n\n يجب ان "
                                                    "تكون من المشرفين "
                                                    "لإستخدامها.")
    @commands.has_role(const.moderator_role_name)
    async def deletexp_async(self, ctx, member: discord.Member):
        user_id = str(member.id)
        guild_id = str(ctx.guild.id)

        query = "DELETE FROM users WHERE user_id = $1 AND guild_id = $2"
        await self.bot.pg_con.execute(query, user_id, guild_id)
        embed = discord.Embed(color=const.default_color, title=f"[delete-xp] - {member}")
        embed.set_thumbnail(url=member.avatar_url)
        await self.delete_rewarded_roles(member=member)
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


def setup(bot):
    bot.add_cog(Levels(bot))
