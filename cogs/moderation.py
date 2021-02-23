import discord
from discord.ext import commands
import asyncio
import constants as const
from typing import Optional
import datetime
import re

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}
TIME_DURATION_UNITS = (
    ('week',60*60*24*7),
    ('day',60*60*24),
    ('hour',60*60),
    ('min',60),
    ('sec',1)
)

class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k] * float(v)
            except KeyError:
                raise commands.BadArgument()
        return time


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def seconds_to_humandr(seconds):
        if seconds == 0:
            return '0'
        parts=[]
        for unit,div in TIME_DURATION_UNITS:
            amount,seconds = divmod(int(seconds),div)
            if amount>0:
                parts.append('{}{}{}'.format(amount,unit,"" if amount == 1 else "s"))
        return ','.join(parts)
    async def re_preform_mutes(self):
        await self.bot.wait_until_ready()
        mutes = await self.bot.pg_con.fetch("SELECT * FROM mutes")
        if mutes is None:
            return
        for mute in mutes:
            guild = self.bot.get_guild(const.guild_id)
            member_id = mute['user_id']
            role = guild.get_role(mute['mute_role_id'])
            when = mute['expire']
            task = self.bot.loop.create_task(self.perform_unmute(member_id=member_id, role=role, when=when))
            task.add_done_callback(self.unmute_error)

    async def perform_unmute(self, *, member_id: int, role: discord.Role, when: datetime.datetime):
        if when > datetime.datetime.utcnow():
            await discord.utils.sleep_until(when)

        guild = self.bot.get_guild(const.guild_id)
        member = guild.get_member(member_id)

        query = "DELETE FROM mutes WHERE guild_id = $1 AND user_id = $2;"
        if member is not None:
            await member.remove_roles(role)
        await self.bot.pg_con.execute(query, const.guild_id, member_id)

    @staticmethod
    def unmute_error(task: asyncio.Task):
        if task.exception():
            task.print_stack()
        else:
            print(f"A Unmute has been done sucssefully")

    # ----------------------------------MOD EVENTS ------------------------------------------------
    @commands.Cog.listener()
    async def on_ready(self):
        await self.re_preform_mutes()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.bot.wait_until_ready()
        query = "SELECT * FROM mutes WHERE user_id = $1 AND guild_id = $2"
        mute = await self.bot.pg_con.fetchrow(query, member.id, member.guild.id)
        if mute is not None:
            if mute['expire'] > datetime.datetime.utcnow():
                mute_role = member.guild.get_role(const.muted_role_id)
                await member.add_roles(mute_role)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or const.moderator_role_name in [role.name for role in message.author.roles]:
            return

        for role in message.author.roles:
            if role == const.moderator_role_name: return
        deletedmsgs_channel = self.bot.get_channel(const.deletedmsgs_channel_id)
        embed = discord.Embed(color=const.default_color)

        try:
            embed.description = f"[حذف رسالة] - {message.author.mention}"
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
        if before.roles != after.roles:
            for role in after.roles:
                if role not in before.roles:
                    if role.id not in (const.muted_role_id,const.new_member_role_id):
                        embed = discord.Embed(color=const.default_color,
                                              description=f"[اخذ رول] - {before.mention}")
                        embed.add_field(name="رول:", value=role.mention)
                        embed.set_footer(text=datetime.datetime.utcnow().strftime('%a, %#d %B %Y'))
                        return await mod_channel.send(embed=embed)
            for role in before.roles:
                if role not in after.roles:
                    if role.id != const.muted_role_id:
                        embed = discord.Embed(color=const.default_color,
                                              description=f"[ازالة رول] - {before.mention}")
                        embed.add_field(name="رول:", value=role.mention)
                        embed.set_footer(text=datetime.datetime.utcnow().strftime('%a, %#d %B %Y'))
                        return await mod_channel.send(embed=embed)

        if before.nick != after.nick:
            embed = discord.Embed(color=const.default_color,
                                  description=f"[تغيير اللقب] - {before.mention}")
            embed.add_field(name="اصبح اللقب:", value=after.nick)
            embed.set_footer(text=datetime.datetime.utcnow().strftime('%a, %#d %B %Y'))
            return await mod_channel.send(embed=embed)

    # ----------------------------------MOD EVENTS ------------------------------------------------

    # ----------------------------------TEMPMUTE Command------------------------------------------------
    @commands.command(name="tempmute", description="ميوت عضو معين لوقت محدد ولسبب إختياري. الوقت يكون بل صيغة التالية(s/m/h/d)\n\n يجب ان تكون من المشرفين لإستخدامها.")
    @commands.has_role(const.moderator_role_name)
    async def tempmute_async(self, ctx: commands.Context, member: discord.Member, duration: TimeConverter, *,
                             reason: Optional[str] = "غير محدد"):
        if duration > 0:
            mute_role = ctx.guild.get_role(const.muted_role_id)
            await member.add_roles(mute_role)
            when = datetime.datetime.utcnow() + datetime.timedelta(seconds=duration)
            task = self.bot.loop.create_task(self.perform_unmute(member_id=member.id, role=mute_role, when=when))
            task.add_done_callback(self.unmute_error)
            query = "INSERT INTO mutes (guild_id, user_id, mute_role_id, expire) VALUES ($1, $2, $3, $4)"
            await self.bot.pg_con.execute(query, const.guild_id, member.id, mute_role.id, when)

            embed = discord.Embed(color=const.default_color, description=f"[TempMute] - {member.mention}")
            embed.add_field(name="سوف يتم إزالة الميوت بعد:",
                            value=self.seconds_to_humandr(duration))
            embed.add_field(name="reason:", value=reason)
            embed.set_footer(text=f"moderator: {ctx.author.display_name} | Muted till {when.strftime('%a, %#d %B %Y, %H:%M:%S')} UTC")
            await ctx.send(embed=embed)
            mod_channel = self.bot.get_channel(const.mod_Channel_id)
            embed.description = f":no_entry: [TempMute] - {member.mention} :no_entry:"
            await mod_channel.send(embed=embed)
        else:
            raise commands.BadArgument()



    @tempmute_async.error
    async def tempmute_async_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="لا يمكنك إستخدام هذا الأمر!")
            await ctx.channel.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="يجب ذكر العضو!\n والصيغة المعتمدة للوقت هيا s/m/h/d فقط!\example:6s/6m/6h/6d n")
            await ctx.send(embed=embed)
        else:
            raise error

    # ----------------------------------TEMPMUTE Command------------------------------------------------

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
        embed = discord.Embed(color=const.default_color, description=f"[kick] - {member.mention}")
        embed.add_field(name="سبب:", value=reason)
        embed.set_footer(text=f"من قبل: {ctx.author.display_name}")
        await member.kick(reason=reason)
        await ctx.channel.send(embed=embed)
        embed.description = f":no_entry: [kick] - {member.mention} :no_entry:"
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
    async def clear_async(self, ctx, limit: int, user: Optional[discord.Member]):

        if 0 < limit <= 100:
            if user == None:
                await ctx.message.delete()
                deleted = await ctx.channel.purge(limit=limit,
                                                  after=datetime.datetime.utcnow() - datetime.timedelta(days=14))
                embed = discord.Embed(color=const.default_color,
                                      title=f" تم حذف {len(deleted)} رسالة/رسأل{const.checkmark_emoji} ")
                await ctx.channel.send(embed=embed, delete_after=10)

            else:
                await ctx.message.delete()
                deleted = await ctx.channel.purge(limit=limit,
                                                  check=lambda message: message.author.id == user.id,
                                                  after=datetime.datetime.utcnow() - datetime.timedelta(days=14))
                embed = discord.Embed(color=const.default_color,
                                      description=f" تم حذف {len(deleted)} رسالة/رسأل أرسلها {user.mention} {const.checkmark_emoji} ")
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
    @commands.command(name="slowmode", description="وضع slowmode على قناة و يحدد الوقت بل صيغة التالية s/m/h, يمكن ازالته بوضع "
                                                   "القيمة الى صفر.\n\nيجب ان تكون من المشرفين لإستخدامها. ")
    @commands.has_role(const.moderator_role_name)
    async def slowmode_async(self, ctx, channel:Optional[discord.TextChannel],duration:TimeConverter):
        channel = ctx.channel if not channel else channel
        if 0 <= duration <= 21600:
            await channel.edit(slowmode_delay=duration)
            embed = discord.Embed(color=const.default_color,
                                  description=f" تم وضع slowmode قناة: {channel.mention} \nالمدة: {self.seconds_to_humandr(duration)}")
            embed.set_footer(text=f"moderator: {ctx.author.display_name}")
            await ctx.channel.send(embed=embed)

        else:
            embed = discord.Embed(
                title="خطأ:",
                description=f"القيمة المحدد غير مقبولة.\n يجب ان تكون بين صفر و ستة ساعات فقط!",
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
            await ctx.guild.ban(user=user, reason=reason, delete_message_days=7)
            mod_channel = self.bot.get_channel(const.mod_Channel_id)
            embed = discord.Embed(
                description=f"[Ban] - {user.mention}",
                color=const.default_color,

            )
            embed.add_field(name="سبب:", value=reason)
            embed.set_footer(text=f"من قبل: {ctx.author.display_name}")
            await ctx.channel.send(embed=embed)
            embed.description = f":no_entry: [Ban] - {user.mention} :no_entry:"
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
                description=f"[Unban] - {user.mention}",
                color=const.default_color
            )
            embed.add_field(name="سبب:", value=reason)
            embed.set_footer(text=f"من قبل: {ctx.author.display_name}")
            await ctx.channel.send(embed=embed)
            embed.description = f":no_entry: [Unban] - {user.mention} :no_entry:"
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
    @commands.command(name="mute", description="ميوت عضو معين لسبب إختياري,.\n\n يجب ان تكون من المشرفين لإستخدامها.")
    @commands.has_role(const.moderator_role_name)
    async def mute_async(self, ctx, user: discord.User, *, reason: Optional[str] = "غير محدد"):
        member = ctx.guild.get_member(user.id)
        if member != None:
            mutedrole = ctx.guild.get_role(const.muted_role_id)

            if mutedrole not in member.roles:
                await member.add_roles(mutedrole)
                embed = discord.Embed(color=const.default_color, description=f"[Mute] - {member.mention}")
                embed.add_field(name="سبب:", value=reason)
                embed.set_footer(text=f"من قبل: {ctx.author.display_name}")
                mod_channel = self.bot.get_channel(const.mod_Channel_id)
                await ctx.channel.send(embed=embed)
                embed.description = f":no_entry: [Mute] - {member.mention} :no_entry:"
                await mod_channel.send(embed=embed)

            else:
                embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                      description="هذا العضو أخذ Mute سابقا!")
                await ctx.channel.send(embed=embed)
        else:
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="هذا العضو ليس موجود في السيرفير!")
            await ctx.channel.send(embed=embed)

    @mute_async.error
    async def mute_async_error(self, ctx, error):
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
    @commands.command(name="unmute",
                      description="إزالة الميوت عن عضو معين لسبب إختياري,.\n\n يجب ان تكون من المشرفين لإستخدامها.")
    @commands.has_role(const.moderator_role_name)
    async def unmute_async(self, ctx, user: discord.User, *, reason: Optional[str] = "غير محدد"):
        member = ctx.guild.get_member(user.id)
        if member != None:
            mutedrole = ctx.guild.get_role(const.muted_role_id)

            if mutedrole in member.roles:
                query = "DELETE FROM mutes WHERE guild_id = $1 AND user_id = $2;"
                await self.bot.pg_con.execute(query, const.guild_id, member.id)
                await member.remove_roles(mutedrole)
                embed = discord.Embed(color=const.default_color, description=f"[Unmute] - {member.mention}")
                embed.add_field(name="سبب:", value=reason)
                embed.set_footer(text=f"من قبل: {ctx.author.display_name}")
                await ctx.channel.send(embed=embed)
                mod_channel = self.bot.get_channel(const.mod_Channel_id)
                embed.description = f":no_entry: [Unmute] - {member.mention} :no_entry:"
                await mod_channel.send(embed=embed)
            else:
                embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                      description="هذا العضو ما معه Mute أصلا!")
                await ctx.channel.send(embed=embed)
        else:
            embed = discord.Embed(color=const.exception_color, title="خطأ:",
                                  description="هذا العضو ليس موجود في السيرفير!")
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
