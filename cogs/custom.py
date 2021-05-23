from discord.ext import commands
import discord

import constants as const

import urllib.parse,urllib.request
import re

def is_mod_or_owner(ctx):
    return const.moderator_role_id in [role.id for role in ctx.author.roles] or ctx.author.id == ctx.guild.owner_id


class Custom(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="codeblock", description="لا وصف", aliases=["cb"])
    async def codeblock_async(self, ctx):
        codeblock = "استخدم الكود بلوك لارسال الكود في رسالة!\n"
        codeblock += " لكتابة كود بلوك c# انظر الى المثل التالي:\n"
        codeblock += "\`\`\`cs\n"
        codeblock += "//أكتب الكود هنا\n"
        codeblock += "\`\`\`\n"
        await ctx.message.delete()
        await ctx.channel.send(codeblock)

    @commands.command(name="google", description="بحث عن موضوع معين في جوجل")
    async def google_async(self, ctx, *, sentence):

        mainurl = "<http://letmegooglethat.com/?q="
        part = ""
        for word in sentence.split():
            part += f"{word}+"
        result = f"{mainurl + part[:-1]}>"
        await ctx.channel.send(result)

    @commands.command(name="youtube",description="بحث عن موضوع معين في يوتيوب",aliases=["ytb"])
    async def youtube_async(self,ctx,*,search):

        query_search = urllib.parse.urlencode({'search_query': search})
        content = urllib.request.urlopen('http://www.youtube.com/results?'+ query_search)
        search_results = re.findall(r'/watch\?v=(.{11})', content.read().decode())
        stringbuilder =""
        stringbuilder +=f" هذا فيديو يوتيوب عن: {search}\n"
        try:
            stringbuilder +=f"<http://www.youtube.com/watch?v={search_results[0]}>"
            await ctx.channel.send(stringbuilder)
        except IndexError:
            await ctx.channel.send(f"اسف, لم اتمكن من ايجاد اي فيديو يتعلق بي {search}")

    @commands.command(name="nullrefrence", description="لا وصف", aliases=["nullref"])
    async def nullrefrence_async(self, ctx):
        nulltext = "NullRefrenceException\n"
        nulltext += "يعني أنك إما لم تقم بتعيين الوبجيكت إلى متغير مطلقًا، أو قمت بتعيينه على قيمة فارغة, قم بتنفيذ: \n"
        nulltext += "```cs\n"
        nulltext += "Debug.Log(YourVariable == null)\n"
        nulltext += "```\n"
        nulltext += " قبل السطر الذي يحتوي على الخطأ لاختبار ما إذا كان الأمر كذلك.\n"
        await ctx.message.delete()
        await ctx.channel.send(nulltext)

    @commands.command(name="nointellisense", description="لا وصف", aliases=["noint"])
    async def nointellisense_async(self, ctx):
        noint = "حل مشكلة عدم الإكمال التلقائي في Visual Studio Community :\n"
        noint += "<https://youtu.be/kT9M22nPkaA>\n"
        noint += "حل مشكلة عدم عمل Visual Studio Code مع Unity :\n"
        noint += "<https://youtu.be/J_jXkS_oUsg>\n"
        await ctx.message.delete()
        await ctx.channel.send(noint)

    @commands.command(name="pleasewait", description="لا وصف", aliases=["plsw"])
    async def pleasewait_async(self, ctx):
        waittxt = "طرح السوأل اكثر من مرة او في كل القنوات لن يسرع وصول الإجابة لك!\n"
        waittxt += "حاول ان تحل المشكلة بنفسك, تحلا بل صبر, عندما يستطيع شخص مساعدتك سوف يساعد!"
        await ctx.message.delete()
        await ctx.channel.send(waittxt)

    @commands.command(name="rules", description="لا وصف")
    async def rules_async(self, ctx):
        rules_channel = self.bot.get_channel(const.rules_channel_id)
        waittxt = f"الرجاء التقيد بالشروط والقوانين الخاصة بالمنصة لعدم التعرض للتنبيه، يمكن مراجعتها هنا: {rules_channel.mention}"
        await ctx.message.delete()
        await ctx.channel.send(waittxt)

    @commands.command(name="rule",description="إظهار القانون المحدد")
    async def rule_async(self, ctx, number:int):
        if number in const.rules.keys():
            embed = discord.Embed(color=const.default_color,title=f"قانون رقم {number}:",description=const.rules[number])
            await ctx.channel.send(embed=embed)
        else:
            embed = discord.Embed(color=const.exception_color,title="خطأ:",description="هذا القانون غير موجود!")
            await ctx.channel.send(embed=embed)
    @commands.command(name="pixelperunit",description="لا وصف",aliases=["ppu"])
    async def pixelperunit_async(self,ctx):
        ppu_text="إذا الصورة صغيرة الحل ان تغير قيمة Pixels Per Unit للصورة الأصلية, يمكنك إختيار الملف الأساسي وتغييرها كما في الصورة:\n"
        ppu_text+= "https://cdn-images-1.medium.com/max/1600/1*8MR8PhIlwG3xZR9dU4Cq2A.png"
        await ctx.message.delete()
        await ctx.channel.send(ppu_text)

    @commands.command(name="test")
    @commands.check(is_mod_or_owner)
    async def test(self,ctx):
        await ctx.send("test works")
    @test.error
    async def test_error(self,ctx,error):
        if isinstance(error,commands.CheckFailure):
            await ctx.send("u cannot use this test")
def setup(bot):
    bot.add_cog(Custom(bot))
