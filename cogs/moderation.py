import discord
from discord.ext import commands

import constants as const
from typing import Optional
import datetime


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ----------------------------------MOD EVENTS ------------------------------------------------

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or const.moderator_role_name in [role.name for role in message.author.roles]:
            return

        for role in message.author.roles:
            if role == const.moderator_role_name: return
        deletedmsgs_channel = self.bot.get_channel(const.deletedmsgs_channel_id)
        embed = discord.Embed(color=const.default_color)

        try:
            embed.title = f"[حذف رسالة] - {message.author}"
            embed.add_field(name="في قناة:", value=message.channel.mention, inline=True)
            embed.add_field(name="محتوى الرسالة:", value=message.content, inline=True)
            embed.set_footer(text=datetime.datetime.utcnow().strftime('%a, %#d %B %Y'))
            await deletedmsgs_channel.send(embed=embed)
        except AttributeError:
            embed.title = f"[حذف رسالة] - خطأ "
            embed.description = "حصل خطاء ما في استرجاع الرسالة المحذوفة"
            await deletedmsgs_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        mod_channel = self.bot.get_channel(const.mod_Channel_id)
        mutedrole = after.guild.get_role(const.muted_role_id)
        if before.roles != after.roles:
            for role in after.roles:
                if role not in before.roles:
                    if role != mutedrole:
                        embed = discord.Embed(color=const.default_color,
                                              title=f"[اخذ رول] - {before}")
                        embed.add_field(name="رول:", value=role.mention)
                        embed.set_footer(text=datetime.datetime.utcnow().strftime('%a, %#d %B %Y'))
                        return await mod_channel.send(embed=embed)
            for role in before.roles:
                if role not in after.roles:
                    if role != mutedrole:
                        embed = discord.Embed(color=const.default_color,
                                              title=f"[ازالة رول] - {before}")
                        embed.add_field(name="رول:", value=role.mention)
                        embed.set_footer(text=datetime.datetime.utcnow().strftime('%a, %#d %B %Y'))
                        return await mod_channel.send(embed=embed)

        if before.nick != after.nick:
            embed = discord.Embed(color=const.default_color,
                                  title=f"[تغيير اللقب] - {before}")
            embed.add_field(name="اصبح اللقب:", value=after.nick)
            embed.set_footer(text=datetime.datetime.utcnow().strftime('%a, %#d %B %Y'))
            return await mod_channel.send(embed=embed)

    # ----------------------------------MOD EVENTS ------------------------------------------------

    # ----------------------------------KICK Command------------------------------------------------
    @commands.command(name="kick", description="إخراج عضو من السيرفير لي سبب اختياري.\n\n يجب ان تكون من المشرفين "
                                               "لإستخدامها.")
    @commands.has_role(const.moderator_role_name)
    async def kick_async(self, ctx, member: discord.Member, *, reason: Optional[str] = "غير محدد"):
        for role in member.roles:
            if role.name == const.moderator_role_name:
                embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                      description="لا يمكنك إستخدام هذا الأمر!")
                return await ctx.channel.send(embed=embed)
        embed = discord.Embed(color=const.default_color, title=f"[kick] - {member}")
        embed.add_field(name="سبب:", value=reason)
        embed.set_footer(text=f"من قبل: {ctx.author.display_name}")
        await member.kick(reason=reason)
        await ctx.channel.send(embed=embed)
        embed.title = f":no_entry: [kick] - {member} :no_entry:"
        mod_channel = self.bot.get_channel(const.mod_Channel_id)
        await mod_channel.send(embed=embed)

    @kick_async.error
    async def kick_async_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="لا يمكنك إستخدام هذا الأمر!")
            await ctx.channel.send(embed=embed)
        elif isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="لم اتمكن من إيجاد العضو المحدد!")
            await ctx.channel.send(embed=embed)
        else:
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="يجب ذكر العضو الذي يجب إخراجه!")
            await ctx.channel.send(embed=embed)

    # ----------------------------------KICK Command------------------------------------------------

    # ----------------------------------CLEAR Command------------------------------------------------
    @commands.command(name="clear", description="مسح عدد معين من الرسأل.\n\nيجب ان تكون من المشرفين لإستخدامها.")
    @commands.has_role(const.moderator_role_name)
    async def clear_async(self, ctx,user=Optional[discord.User], *, limit: int):

        if 0 < limit <= 100:
            if user == None:
                await ctx.message.delete()
                deleted = await ctx.channel.purge(limit=limit,
                                                  after=datetime.datetime.utcnow() - datetime.timedelta(days=14))
                embed = discord.Embed(color=const.default_color,
                                      title=f" تم حذف {len(deleted)} رسالة/رسأل{const.checkmark_emoji} ")
                await ctx.channel.send(embed=embed,delete_after=10)

            else:
                await ctx.message.delete()
                deleted = await ctx.channel.purge(limit=limit,
                                                  check=lambda message: message.author.id == user.id,
                                                  after=datetime.datetime.utcnow() - datetime.timedelta(days=14))
                embed = discord.Embed(color=const.default_color,
                                      title=f" تم حذف {len(deleted)} رسالة/رسأل أرسلها {user} {const.checkmark_emoji} ")
                await ctx.channel.send(embed=embed, delete_after=10)

        else:
            embed = discord.Embed(
                title="خطأ:",
                description=f"القيمة المحدد غير مقبولة.\n يجب ان تكون بين 1 و 100 فقط!",
                color=const.exception_color,
            )
            await ctx.channel.send(embed=embed)

    @clear_async.error
    async def clear_async_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="لا يمكنك إستخدام هذا الأمر!")
            await ctx.channel.send(embed=embed)
        else:
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="يجب ذكر القيمة الذي يجب حذفها!")
            await ctx.channel.send(embed=embed)

    # ----------------------------------CLEAR Command------------------------------------------------

    # ----------------------------------SLOWMODE Command------------------------------------------------
    @commands.command(name="slowmode", description="وضع slowmode على قناة و يحدد الوقت بل ثواني فقط, يمكن ازالته بوضع "
                                                   "القيمة الى صفر.\n\nيجب ان تكون من المشرفين لإستخدامها. ")
    @commands.has_role(const.moderator_role_name)
    async def slowmode_async(self, ctx, duration: int):
        if 0 <= duration <= 21600:
            await ctx.channel.edit(slowmode_delay=duration)
            embed = discord.Embed(color=const.default_color,
                                  title=f" تم وضع slowmode قناة: {ctx.channel} \nالمدة: {str(datetime.timedelta(seconds=duration))}")
            embed.set_footer(text=f"من قبل: {ctx.author.display_name}")
            await ctx.channel.send(embed=embed)

        else:
            embed = discord.Embed(
                title="خطأ:",
                description=f"القيمة المحدد غير مقبولة.\n يجب ان تكون بين 0 و 21600 فقط!",
                color=const.exception_color,
            )
            await ctx.channel.send(embed=embed)

    @slowmode_async.error
    async def slowmode_async_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="لا يمكنك إستخدام هذا الأمر!")
            await ctx.channel.send(embed=embed)
        else:
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="يجب ذكر القيمة الذي يجب وضعها!")
            await ctx.channel.send(embed=embed)

    # ----------------------------------SLOWMODE Command------------------------------------------------

    # ----------------------------------BAN Command------------------------------------------------
    @commands.command(name="ban", description="حظر عضو من السيرفير لي سبب اختياري, يمكن طرد العضو حتى لو لم يكن في "
                                              "السيرفير.\n\n يجب ان تكون من المشرفين لإستخدامها. ")
    @commands.has_role(const.moderator_role_name)
    async def ban_async(self, ctx, user: discord.User, *, reason: Optional[str] = "غير محدد"):

        if user.id == self.bot.user.id:
            embed = discord.Embed(
                title="خطأ:",
                description=f"لا يمكنك حظري!",
                color=const.exception_color,
            )
            return await ctx.channel.send(embed=embed)

        if user.id == ctx.author.id:
            embed = discord.Embed(
                title="خطأ:",
                description=f"لا يمكنك حظر نفسك!",
                color=const.exception_color,
            )
            return await ctx.channel.send(embed=embed)
        try:
            await ctx.guild.fetch_ban(user)
            embed = discord.Embed(
                title="خطأ:",
                description=f"هذا العضو محظور سابقا!",
                color=const.exception_color,
            )
            await ctx.channel.send(embed=embed)
        except discord.NotFound:
            await ctx.guild.ban(user=user, reason=reason, delete_message_days=0)
            mod_channel = self.bot.get_channel(const.mod_Channel_id)
            embed = discord.Embed(
                title=f"[Ban] - {user}",
                description=f"تم طرد {user}",
                color=const.default_color,

            )
            embed.add_field(name="سبب:", value=reason)
            embed.set_footer(text=f"من قبل: {ctx.author.display_name}")
            await ctx.channel.send(embed=embed)
            embed.title = f":no_entry: [Ban] - {user.display_name} :no_entry:"
            await mod_channel.send(embed=embed)

    @ban_async.error
    async def ban_async_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="لا يمكنك إستخدام هذا الأمر!")
            await ctx.channel.send(embed=embed)
        else:
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="يجب ذكر المستخدم الذي يجب حظره!")
            await ctx.channel.send(embed=embed)

    # ----------------------------------BAN Command------------------------------------------------

    # ----------------------------------UNBAN Command------------------------------------------------
    @commands.command(name="unban", description="ازالة الحظر عن عضو لسبب اختياري.\n\n يجب ان تكون من المشرفين "
                                                "لإستخدامها.")
    @commands.has_role(const.moderator_role_name)
    async def unban_async(self, ctx, user: discord.User, *, reason: Optional[str] = "غير محدد"):
        try:
            await ctx.guild.fetch_ban(user)
            await ctx.guild.unban(user=user, reason=reason)
            mod_channel = self.bot.get_channel(const.mod_Channel_id)
            embed = discord.Embed(
                title=f"[Unban] - {user.display_name}",
                description=f"تم ازالة الحظر عن {user}",
                color=const.default_color
            )
            embed.add_field(name="سبب:", value=reason)
            embed.set_footer(text=f"من قبل: {ctx.author.display_name}")
            await ctx.channel.send(embed=embed)
            embed.title = f":no_entry: [Unban] - {user.display_name} :no_entry:"
            await mod_channel.send(embed=embed)
        except discord.NotFound:
            embed = discord.Embed(
                title=f"خطأ",
                description="العضو ليس محظور سابقا!",
                color=const.exception_color
            )
            await ctx.channel.send(embed=embed)

    @unban_async.error
    async def unban_async_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="لا يمكنك إستخدام هذا الأمر!")
            await ctx.channel.send(embed=embed)
        else:
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="يجب ذكر المستخدم الذي يجب زالة الحظر عنه!")
            await ctx.channel.send(embed=embed)
    # ----------------------------------UNBAN Command------------------------------------------------

    # ----------------------------------MUTE Command------------------------------------------------
    @commands.command(name="mute",description="ميوت عضو معين لسبب إختياري,.\n\n يجب ان تكون من المشرفين لإستخدامها.")
    @commands.has_role(const.moderator_role_name)
    async def mute_async(self,ctx , user:discord.User, *, reason:Optional[str] = "غير محدد"):
        member = ctx.guild.get_member(user.id)
        if member!= None:
            mutedrole = ctx.guild.get_role(const.muted_role_id)

            if mutedrole not in member.roles:
                await member.add_roles(mutedrole)
                embed = discord.Embed(color=const.default_color, title=f"[Mute] - {member.display_name}")
                embed.add_field(name="سبب:",value=reason)
                embed.set_footer(text=f"من قبل: {ctx.author.display_name}")
                mod_channel = self.bot.get_channel(const.mod_Channel_id)
                await ctx.channel.send(embed=embed)
                embed.title = f":no_entry: [Mute] - {member.display_name} :no_entry:"
                await mod_channel.send(embed=embed)

            else:
                embed= discord.Embed(color=const.exception_color,title="خطأ:",description="هذا العضو أخذ Mute سابقا!")
                await ctx.channel.send(embed=embed)
        else:
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="هذا العضو ليس موجود في السيرفير!")
            await ctx.channel.send(embed=embed)
    @mute_async.error
    async def mute_async_error(self,ctx,error):
        if isinstance(error, commands.MissingRole):
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="لا يمكنك إستخدام هذا الأمر!")
            await ctx.channel.send(embed=embed)
        else:
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="يجب ذكر المستخدم!")
            await ctx.channel.send(embed=embed)
    # ----------------------------------MUTE Command------------------------------------------------

    # ----------------------------------UNMUTE Command------------------------------------------------
    @commands.command(name="unmute", description="إزالة الميوت عن عضو معين لسبب إختياري,.\n\n يجب ان تكون من المشرفين لإستخدامها.")
    @commands.has_role(const.moderator_role_name)
    async def unmute_async(self, ctx, user: discord.User,*,reason:Optional[str]="غير محدد"):
        member = ctx.guild.get_member(user.id)
        if member != None:
            mutedrole = ctx.guild.get_role(const.muted_role_id)

            if mutedrole in member.roles:
                await member.remove_roles(mutedrole)
                embed = discord.Embed(color=const.default_color, title=f"[Unmute] - {member.display_name}")
                embed.add_field(name="سبب:", value=reason)
                embed.set_footer(text=f"من قبل: {ctx.author.display_name}")
                await ctx.channel.send(embed=embed)
                mod_channel = self.bot.get_channel(const.mod_Channel_id)
                embed.title = f":no_entry: [Unmute] - {member.display_name} :no_entry:"
                await mod_channel.send(embed=embed)
            else:
                embed = discord.Embed(color=const.exception_color, title="خطأ:", description="هذا العضو ما معه Mute أصلا!")
                await ctx.channel.send(embed=embed)
        else:
            embed = discord.Embed(color=const.exception_color, title="خطأ:", description="هذا العضو ليس موجود في السيرفير!")
            await ctx.channel.send(embed=embed)

    @unmute_async.error
    async def unmute_async_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="لا يمكنك إستخدام هذا الأمر!")
            await ctx.channel.send(embed=embed)
        else:
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="يجب ذكر المستخدم!")
            await ctx.channel.send(embed=embed)
    # ----------------------------------UNMUTE Command------------------------------------------------

def setup(bot):
    bot.add_cog(Moderation(bot))
