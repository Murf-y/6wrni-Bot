import discord
from discord.ext import commands

import constants as const
import time
import datetime

start_time= time.time()

class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.version = bot.version

    # ----------------------------------Ping Command------------------------------------------------
    @commands.command(name="ping", description=" وقت استجابة البوت", aliases=["latency"])
    async def ping_async(self, ctx):
        if ctx.channel.id != const.botchannel_id and ctx.channel.id != const.private_channel_id and ctx.channel.id != const.private2_channel_id:
            bot_channel = self.bot.get_channel(const.botchannel_id)
            return await ctx.channel.send(f"لا يمكنك إستعملها هنا, إذهب الى {bot_channel.mention}!")
        embed = discord.Embed(color=const.default_color,title=f" وقت الإستجابة الحالي هو :{round((self.bot.latency * 1000))}ms")
        await ctx.channel.send(embed=embed)

    # ----------------------------------Ping Command------------------------------------------------

    # ----------------------------------BOTINFO Command------------------------------------------------
    @commands.command(name="botinfo", description="معلومات عن 6wrni Bot")
    async def b_info_async(self, ctx):
        if ctx.channel.id != const.botchannel_id and ctx.channel.id != const.private_channel_id and ctx.channel.id != const.private2_channel_id:
            bot_channel = self.bot.get_channel(const.botchannel_id)
            return await ctx.channel.send(f"لا يمكنك إستعملها هنا, إذهب الى {bot_channel.mention}!")
        current_time = time.time()
        difference = int(round(current_time - start_time))
        uptime = str(datetime.timedelta(seconds= difference))
        embed = discord.Embed(color=const.default_color)
        embed.add_field(name="الإسم:", value=self.bot.user.display_name, inline=False)
        embed.add_field(name="إصدار البوت:", value=self.version, inline=False)
        embed.add_field(name=""
                             "مدة العمل:", value=uptime, inline=False)
        embed.add_field(name="مصدر الكود:", value="[Github repository](https://github.com/Murf-y/6wrni-Bot)",
                        inline=False)
        embed.add_field(name="تاريخ إنشاء الحساب:",
                        value=f"{self.bot.user.created_at.strftime('%a, %#d %B %Y')}\n", inline=False)
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
