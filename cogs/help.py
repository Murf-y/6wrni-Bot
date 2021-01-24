import discord
from discord.ext import commands
from discord.ext.menus import ListPageSource, MenuPages

import constants as const


class HelpMenu(ListPageSource):
    def __init__(self, bot, ctx, data):
        self.ctx = ctx
        self.bot = bot
        super().__init__(data, per_page=6)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page * self.per_page) + 1
        len_data = len(self.entries)

        embed = discord.Embed(
            title="Help",
            description=f"  هذه مجموعة الأوامر, لمعلومات عن أمر معين أكتب: {self.bot.command_prefix}help ```إسم الأمر``` ",
            color=const.default_color
        )
        embed.set_thumbnail(url=self.ctx.guild.me.avatar_url)

        embed.set_footer(text=f" عدد الصفحات : {int(-1 * (len_data / self.per_page) // 1 * -1)}")
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=True)
        return embed

    async def format_page(self, menu, entries):
        fields = []
        for entry in entries:
            if not entry.hidden:
                fields.append((f"{self.bot.command_prefix}{entry.name}", "-------------------"))
        return await self.write_page(menu, fields)


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
        return f"```{cmd_and_aliases} {params}```"

    async def cmd_help(self, ctx, command):
        embed = discord.Embed(
            title=f"{command}",
            description=self.syntax(command),
            color=const.default_color
        )
        embed.add_field(name="وصف:", value=command.description)
        await ctx.channel.send(embed=embed)

    @commands.command(name="help", hidden=True)
    async def show_help(self, ctx, command: str = None):
        """إظهار جميع الأوامر"""
        if command is None:
            menu = MenuPages(source=HelpMenu(self.bot, ctx, list(self.bot.commands)), clear_reactions_after=True,
                             delete_message_after=True, timeout=60.0)
            await menu.start(ctx)
        else:
            try:
                cmd = discord.utils.get(self.bot.commands, name=command)
                await self.cmd_help(ctx, cmd)
            except ValueError:
                pass

    @show_help.error
    async def show_help_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = discord.Embed(color=discord.Color.red())
            embed.add_field(name="خطأ", value="هذا الأمر غير موجود !")
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
