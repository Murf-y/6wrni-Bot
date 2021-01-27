import discord
from discord.ext import commands

import constants as const


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def syntax(self, command):
        cmd_and_aliases = "|".join([str(command), *command.aliases])
        params = []
        for key, value in command.params.items():
            if key not in ("self", "ctx"):
                params.append(f"[{key}]" if "None" in str(value) else f"<{key}>")
        params = " ".join(params)
        return f"`{cmd_and_aliases} {params}`"

    @commands.command(name="help",description="إظهار جميع الفئات")
    async def show_help(self, ctx, category: str = None):
        if ctx.channel.id != const.botchannel_id:
            bot_channel = self.bot.get_channel(const.botchannel_id)
            return await ctx.channel.send(f"لا يمكنك إستعملها هنا, إذهب الى {bot_channel.mention}!")
        """إظهار جميع الفئات"""
        if category is None:

            embed = discord.Embed(color=const.default_color, title="Help",
                                  description=f"  هذه مجموعة الفئات, لمعلومات عن فئة معينة أكتب: {self.bot.command_prefix}help `إسم الفئة` ")

            for cog in self.bot.cogs:
                if cog == "Help":
                    continue
                else:
                    embed.add_field(name=cog, value="-------------------------",inline=False)
            await ctx.channel.send(embed=embed)
        else:
            _cog = self.bot.get_cog(category)
            if not _cog:
                embed = discord.Embed(color=const.exception_color)
                embed.add_field(name="خطأ:", value="هذه الفئة غير موجودة !")
                return await ctx.send(embed=embed)
            embed = discord.Embed(color=const.default_color, title=category,description="هذه كل الأوامر في هذه الفئة:")
            commands = _cog.get_commands()
            for command in commands:
                embed.add_field(name=f"{self.bot.command_prefix}{command.name}", value=f"{self.syntax(command)}\n"
                                                                                       f"وصف: {command.description}"
                                                                                       f"\n---------------------\n",inline=False)
            await ctx.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
