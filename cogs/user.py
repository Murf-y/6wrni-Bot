import discord
from discord.ext import commands


class User(commands.Cog):

    def __init(self, bot):
        self.bot = bot

    # --------------------------------- UserInfo Command---------------------------------------------
    @commands.command(name="userinfo", description="معلومات عن عضو معين", aliases=["info"])
    async def userinfo_async(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member

        embed = discord.Embed(color=member.color)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f"طلب من قبل : {ctx.author.name}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="الإسم:", value=member)
        embed.add_field(name="Id:", value=f"{member.id}\n")
        embed.add_field(name="تاريخ إنشاء الحساب:",
                        value=f"{member.created_at.strftime('%a, %#d %B %Y')}\n", inline=False)
        embed.add_field(name="تاريخ انضمام العضو:",
                        value=f"{member.joined_at.strftime('%a, %#d %B %Y')}\n", inline=False)
        embed.add_field(name="اعلى رتبة:",
                        value=member.top_role.mention)

        await ctx.channel.send(embed=embed)

    # --------------------------------- UserInfo Command---------------------------------------------


def setup(bot):
    bot.add_cog(User(bot))
