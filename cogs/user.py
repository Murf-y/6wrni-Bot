import discord
from discord.ext import commands

import constants as const


class User(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # --------------------------------- BOT EVENTS---------------------------------------------
    @commands.Cog.listener()
    async def on_raw_reaction_add(self,payload:discord.RawReactionActionEvent):
        if payload.message_id == 805480651532795975:
            if payload.emoji.id == const.UnityEmoji:
                role = payload.member.guild.get_role(const.users_giveable_roles_id[0])
                await payload.member.add_roles(role)
            elif payload.emoji.id == const.UnrealEmoji:
                role = payload.member.guild.get_role(const.users_giveable_roles_id[1])
                await payload.member.add_roles(role)
            elif payload.emoji.id == const.GodotEmoji:
                role = payload.member.guild.get_role(const.users_giveable_roles_id[2])
                await payload.member.add_roles(role)
            elif payload.emoji.id == const.GamemakerEmoji:
                role = payload.member.guild.get_role(const.users_giveable_roles_id[4])
                await payload.member.add_roles(role)
            elif payload.emoji.id == const.BlenderEmoji:
                role = payload.member.guild.get_role(const.users_giveable_roles_id[3])
                await payload.member.add_roles(role)
            elif payload.emoji.id == const._3dEmoji:
                role = payload.member.guild.get_role(const.users_giveable_roles_id[6])
                await payload.member.add_roles(role)
            elif payload.emoji.id ==const._2dEmoji:
                role = payload.member.guild.get_role(const.users_giveable_roles_id[5])
                await payload.member.add_roles(role)
            elif str(payload.emoji) == const.SoundEmoji:
                role = payload.member.guild.get_role(const.users_giveable_roles_id[7])
                await payload.member.add_roles(role)
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.message_id == 805480651532795975:
            if payload.emoji.id == const.UnityEmoji:
                guild = self.bot.get_guild(const.guild_id)
                role = guild.get_role(const.users_giveable_roles_id[0])
                member = guild.get_member(payload.user_id)
                await member.remove_roles(role)
            elif payload.emoji.id == const.UnrealEmoji:
                guild = self.bot.get_guild(const.guild_id)
                role = guild.get_role(const.users_giveable_roles_id[1])
                member = guild.get_member(payload.user_id)
                await member.remove_roles(role)
            elif payload.emoji.id == const.GodotEmoji:
                guild = self.bot.get_guild(const.guild_id)
                role = guild.get_role(const.users_giveable_roles_id[2])
                member = guild.get_member(payload.user_id)
                await member.remove_roles(role)
            elif payload.emoji.id == const.GamemakerEmoji:
                guild = self.bot.get_guild(const.guild_id)
                role = guild.get_role(const.users_giveable_roles_id[4])
                member = guild.get_member(payload.user_id)
                await member.remove_roles(role)
            elif payload.emoji.id == const.BlenderEmoji:
                guild = self.bot.get_guild(const.guild_id)
                role = guild.get_role(const.users_giveable_roles_id[3])
                member = guild.get_member(payload.user_id)
                await member.remove_roles(role)
            elif payload.emoji.id == const._3dEmoji:
                guild = self.bot.get_guild(const.guild_id)
                role = guild.get_role(const.users_giveable_roles_id[6])
                member = guild.get_member(payload.user_id)
                await member.remove_roles(role)
            elif payload.emoji.id == const._2dEmoji:
                guild = self.bot.get_guild(const.guild_id)
                role = guild.get_role(const.users_giveable_roles_id[5])
                member = guild.get_member(payload.user_id)
                await member.remove_roles(role)
            elif str(payload.emoji) == const.SoundEmoji:
                guild = self.bot.get_guild(const.guild_id)
                role = guild.get_role(const.users_giveable_roles_id[7])
                member = guild.get_member(payload.user_id)
                await member.remove_roles(role)
    # --------------------------------- BOT EVENTS---------------------------------------------

    # --------------------------------- UserInfo Command---------------------------------------------
    @commands.command(name="userinfo", description="معلومات عن عضو معين", aliases=["info"])
    async def userinfo_async(self, ctx, member: discord.Member = None):
        if ctx.channel.id != const.botchannel_id and ctx.channel.id != const.private_channel_id and ctx.channel.id != const.private2_channel_id and ctx.channel.id != const.mod_Channel_id:
            bot_channel = self.bot.get_channel(const.botchannel_id)
            return await ctx.channel.send(f"لا يمكنك إستعملها هنا, إذهب الى {bot_channel.mention}!")
        member = ctx.author if not member else member

        embed = discord.Embed(color=member.color)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f"طلب من قبل : {ctx.author.name}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="الإسم:", value=member)
        embed.add_field(name="Id:", value=f"{member.id}\n")
        embed.add_field(name="تاريخ إنشاء الحساب:",
                        value=f"{member.created_at.strftime('%a, %#d %B %Y, %H:%M:%S')}\n", inline=False)
        embed.add_field(name="تاريخ انضمام العضو:",
                        value=f"{member.joined_at.strftime('%a, %#d %B %Y, %H:%M:%S')}\n", inline=False)
        embed.add_field(name="اعلى رتبة:",
                        value=member.top_role.mention)

        await ctx.channel.send(embed=embed)

    # --------------------------------- UserInfo Command---------------------------------------------


    # --------------------------------- GIVEROLE Command---------------------------------------------
    @commands.command(name="giverole", description="يحصل مستخدمها على الرول المحدد!")
    async def giverole_async(self, ctx, *, role: discord.Role):
        if ctx.channel.id != const.botchannel_id and ctx.channel.id != const.private_channel_id and ctx.channel.id != const.private2_channel_id and ctx.channel.id != const.mod_Channel_id:
            bot_channel = self.bot.get_channel(const.botchannel_id)
            return await ctx.channel.send(f"لا يمكنك إستعملها هنا, إذهب الى {bot_channel.mention}!")
        if role.id in const.users_giveable_roles_id:
            if role.id not in [role.id for role in ctx.author.roles]:
                embed = discord.Embed(color=const.default_color, title=f"[Give-role] - {ctx.author}",
                                      description=F"حصلت على رول {role.name} !")
                await ctx.author.add_roles(role)
                await ctx.channel.send(embed=embed)
            else:
                embed = discord.Embed(color=const.exception_color,
                                      title="لديك هذا الرول,لا يمكنك الحصول عليه مرة أخرى!")
                await ctx.channel.send(embed=embed)
        else:
            embed = discord.Embed(color=const.exception_color, title="لا يمكنك الحصول على هذا الرول!")
            await ctx.channel.send(embed=embed)
    @giverole_async.error
    async def giverole_async_error(self,ctx,error):
        embed=discord.Embed(color=const.exception_color,title="خطأ:",description="هذا الرول غير موجود!")
        await ctx.channel.send(embed=embed)

    # --------------------------------- GIVEROLE Command---------------------------------------------

    # --------------------------------- REMOVEROLE Command---------------------------------------------
    @commands.command(name="removerole", description="إزالة الرول المحدد!")
    async def removerole_async(self, ctx, *, role: discord.Role):
        if ctx.channel.id != const.botchannel_id and ctx.channel.id != const.private_channel_id and ctx.channel.id != const.private2_channel_id and ctx.channel.id != const.mod_Channel_id:
            bot_channel = self.bot.get_channel(const.botchannel_id)
            return await ctx.channel.send(f"لا يمكنك إستعملها هنا, إذهب الى {bot_channel.mention}!")
        if role.id in const.users_giveable_roles_id:
            if role.id in [role.id for role in ctx.author.roles]:
                embed = discord.Embed(color=const.default_color, title=f"[Remove-role] - {ctx.author}",
                                      description=F"تم إزالة رول {role.name} !")
                await ctx.author.remove_roles(role)
                await ctx.channel.send(embed=embed)
            else:
                embed = discord.Embed(color=const.exception_color,
                                      title="لا تملك هذا الرول!")
                await ctx.channel.send(embed=embed)
        else:
            embed = discord.Embed(color=const.exception_color, title="لا يمكنك إزالة هذا الرول!")
            await ctx.channel.send(embed=embed)

    @removerole_async.error
    async def removerole_async_error(self, ctx, error):
        embed = discord.Embed(color=const.exception_color, title="خطأ:", description="هذا الرول غير موجود!")
        await ctx.channel.send(embed=embed)
    # --------------------------------- REMOVEROLE Command---------------------------------------------

    # --------------------------------- ROLES Command---------------------------------------------
    @commands.command(name="roles", description="إظهار كل الرتب الذي يمكن ان يأخذها العضو يدويا!")
    async def roles_async(self, ctx):
        if ctx.channel.id != const.botchannel_id and ctx.channel.id != const.private_channel_id and ctx.channel.id != const.private2_channel_id and ctx.channel.id != const.mod_Channel_id:
            bot_channel = self.bot.get_channel(const.botchannel_id)
            return await ctx.channel.send(f"لا يمكنك إستعملها هنا, إذهب الى {bot_channel.mention}!")
        roles = ""
        for role_id in const.users_giveable_roles_id:
            role = ctx.guild.get_role(role_id)
            roles += f"• {role.name}\n"
        embed = discord.Embed(color=const.default_color, title="User Roles:", description=roles)
        await ctx.channel.send(embed=embed)

    # --------------------------------- ROLES Command---------------------------------------------



def setup(bot):
    bot.add_cog(User(bot))
