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

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.content.startswith(f'{self.bot.command_prefix}') or message.channel.id in const.NoXpchannels_id: return


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

        await self.bot.process_commands(message)

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

    @commands.command(name="remove-xp", hidden=True, description="إزالة نسبة محددة من ال XP لعضو معين.\n\n يجب ان "
                                                                 "تكون من المشرفين "
                                                                 "لإستخدامها.")
    @commands.has_role(const.moderator_role_name)
    async def removeXP_async(self, ctx, member: discord.Member, amount: int):
        pass

    @removeXP_async.error
    async def removeXP_async_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="لا يمكنك إستخدام هذا الأمر!")
            await ctx.channel.send(embed=embed)
        else:
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="يجب ذكر العضو والقيمة الذي يجب إزالتها!")
            await ctx.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Levels(bot))
