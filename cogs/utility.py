import discord
from discord.ext import commands

import constants as const


class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.version = bot.version

    # ----------------------------------Ping Command------------------------------------------------
    @commands.command(name="ping", description=" وقت استجابة البوت", aliases=["latency"])
    async def ping_async(self, ctx):
        embed = discord.Embed(color=const.default_color,title=f" وقت الإستجابة الحالي هو :{round((self.bot.latency * 1000))}ms")
        await ctx.channel.send(embed=embed)

    # ----------------------------------Ping Command------------------------------------------------

    # ----------------------------------BOTINFO Command------------------------------------------------
    @commands.command(name="botinfo", description="معلومات عن 6wrni Bot")
    async def b_info_async(self, ctx):
        embed = discord.Embed(color=const.default_color)
        embed.add_field(name="الإسم:", value=self.bot.user.display_name, inline=False)
        embed.add_field(name="إصدار البوت:", value=self.version, inline=False)
        embed.add_field(name="مصدر الكود:", value="[Github repository](https://github.com/Murf-y/6wrni_Bot)",
                        inline=False)
        embed.add_field(name="صنع باستخدام:", value="Discord.py", inline=False)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.channel.send(embed=embed)

    # ----------------------------------BOTINFO Command------------------------------------------------

    # ----------------------------------CHANGE STATUS Command------------------------------------------------
    @commands.command(name="change-status", description="تغير الحالة الخاصة بل بوت.\n\n يجب ان تكون من المشرفين لإستخدامها. ")
    @commands.has_role(const.moderator_role_name)
    async def change_status_async(self, ctx, *, status):
        await self.bot.change_presence(status=discord.Status.online,
                                       activity=discord.Activity(type=discord.ActivityType.watching, name=status))
        await ctx.message.add_reaction(const.checkmark_emoji)

    @change_status_async.error
    async def change_status_async_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="لا يمكنك إستخدام هذا الأمر!")
            await ctx.channel.send(embed=embed)
    # ----------------------------------CHANGE STATUS Command------------------------------------------------


def setup(bot):
    bot.add_cog(cog=Utility(bot))
