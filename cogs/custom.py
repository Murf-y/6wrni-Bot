from discord.ext import commands

import constants as const

import urllib.parse,urllib.request
import re

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
        await ctx.message.delete()
        mainurl = "<http://letmegooglethat.com/?q="
        part = ""
        for word in sentence.split():
            part += f"{word}+"
        result = f"{mainurl + part[:-1]}>"
        await ctx.channel.send(result)

    @commands.command(name="youtube",description="بحث عن موضوع معين في يوتيوب")
    async def youtube_async(self,ctx,*,search):
        await ctx.message.delete()
        query_search = urllib.parse.urlencode({'search_query': search})
        content = urllib.request.urlopen('http://www.youtube.com/results?'+ query_search)
        search_results = re.findall(r'/watch\?v=(.{11})', content.read().decode())
        stringbuilder =""
        stringbuilder +=f" هذا فيديو يوتيوب عن: {search}\n"
        try:
            stringbuilder +=f"<http://www.youtube.com/watch?v=+{search_results[0]}>"
            await ctx.channel.send(stringbuilder)
        except IndexError:
            await ctx.channel.send(f"اسف, لم اتمكن من ايجاد اي فيديو يتعلق بي {search}")

    @commands.command(name="nullrefrence", description="لا وصف", aliases=["nullref", ])
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


def setup(bot):
    bot.add_cog(Custom(bot))
