import discord
import asyncio
import os, subprocess, sys
import feedparser
import mangatest

import time, threading

class LilyClient(discord.Client):


##    async def periodic(self):
##        while True:
##            self.updateNotify()
##            await asyncio.sleep(5.0)
##
##    task = asyncio.Task(periodic())
##    loop = asyncio.new_event_loop()






    async def on_ready(self):
        """Override the on_ready function on discord.Client"""
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        default_channel = '342970124967346186' ##  '297260933124718593' = chatbotdev, '342970124967346186' = spoilerinotvanimango
        
        
        

        async def speak_periodic(self):
##            count = 0
            async def speak_periodic_internal():
                await self.updateNotify()
##                nonlocal count
##                count += 1
##                await self.send_message(self.get_channel('297260933124718593'), "woof! ({})".format(count))
##                if count < 5:
                await asyncio.sleep(900)
                await speak_periodic_internal()
            await speak_periodic_internal()

        await speak_periodic(self)

        



        

    async def on_message(self, message):
        """Override the on_message function on discord.Client"""
        if message.content.startswith('!speak'):
            await self.send_message(message.channel, 'woof!')
##        elif message.content.startswith('!test'):
##            await self.test(message)
        elif message.content.startswith('!mangacheck') or message.content.startswith('!mcheck'):
            await self.mangacheck(message)
        elif message.content.startswith('!mangasub') or message.content.startswith('!msub'):
            await self.mangasub(message)
        elif message.content.startswith('!mangaunsub') or message.content.startswith('!munsub'):
            await self.mangaunsub(message)
        elif message.content.startswith('!mangamysubs') or message.content.startswith('!mmysubs'):
            await self.mangamysubs(message)
        elif message.content.startswith('!mangaforceupdate'):
            await self.updateNotify()
            await self.send_message(message.channel, "Update complete")
        elif message.content == '!manga' or message.content.startswith('!mhelp') or message.content.startswith('!mangahelp'):
            await self.mangahelp(message)
##        elif message.content.startswith('?reload'):
##            await self.reload_command()
##        elif message.content.startswith('?reload'):
##            await self.reload_command()



    async def test(self, message):
        await self.send_message(self.get_channel(default_channel), '`'+message.author.mention+'`'+message.author.mention+' '+message.author.name+' '+message.author.id)
        await self.send_message(self.get_channel(default_channel), message.channel.id)
        


    async def mangacheck(self, message):
        args = message.content.split()
        if len(args) < 2:
            await self.send_message(message.channel, "Use it like this u dumdum `!mangacheck One Piece` it's case sensitive LOL")
        else:
            search_title = " ".join(args[1:])
            aa = mangatest.checkManga(search_title)

            if not aa:
                await self.send_message(message.channel, "\"{}\" was not found in database.".format(search_title))
            else:
                if aa[0]:
                    await self.send_message(message.channel, "MS {} chapter {}: {} [{}]".format(aa[0]['title'], aa[0]['latest_chap'], aa[0]['chap_desc'], aa[0]['chap_URL']))
                if aa[1]:
                    await self.send_message(message.channel, "JB {} chapter {}: {} [{}]".format(aa[1]['title'], aa[1]['latest_chap'], aa[1]['chap_desc'], aa[1]['chap_URL']))
                

    async def mangasub(self, message):
        args = message.content.split()
        if len(args) < 2:
            await self.send_message(message.channel, "Use it like this u dumdum `!mangasub One Piece` it's case sensitive LOL")
        else:
            search_title = " ".join(args[1:])
            aa = mangatest.checkManga(search_title)
            
            if not aa:
                await self.send_message(message.channel, "\"{}\" was not found in database.".format(search_title))
            else:
                mangatest.createSub(message.author.id, search_title)
                await self.send_message(message.channel, "You were successfully subbed \"{}\".".format(search_title))

    async def mangaunsub(self, message):
        args = message.content.split()
        if len(args) < 2:
            await self.send_message(message.channel, "Use it like this u dumdum `!mangaunsub One Piece` it's case sensitive LOL")
        else:
            search_title = " ".join(args[1:])
            if search_title not in (mangatest.checkSubs(message.author.id)):
                await self.send_message(message.channel, "Error: \"{}\" was not found in your subs".format(search_title))
            else:
                mangatest.delSub(message.author.id, search_title)
                await self.send_message(message.channel, "Successfully you were unsubbed from \"{}\".".format(search_title))

    async def mangamysubs(self, message):
        sub_list = mangatest.checkSubs(message.author.id)
        if not sub_list:
            await self.send_message(message.channel, "Hi {}, you aren't subbed to anything! Use `!mangasub` to subscribe to something.".format(message.author.display_name, sub_list))
        else:
            sub_list = ', '.join(sub_list)
            await self.send_message(message.channel, "Hi {}, you are currently subbed to: {}.".format(message.author.display_name, sub_list))


    async def updateNotify(self):
        updated_manga = mangatest.updatedMangaList()

        for i in updated_manga:
            subber_list = mangatest.checkSubbers(i)
            subber_list2 = []
            for j in subber_list:
                subber_list2.append("<@{}>".format(j))
            
            if subber_list2:
                await self.send_message(self.get_channel(default_channel), "Good news everyone! \"{}\" has been updated! `!mangasub` to subscribe".format(i))
                await self.send_message(self.get_channel(default_channel), ' '.join(subber_list2))
                aa = mangatest.checkManga(i)
                if aa[0]:
                    await self.send_message(self.get_channel(default_channel), "MS {} chapter {}: {} [{}]".format(aa[0]['title'], aa[0]['latest_chap'], aa[0]['chap_desc'], aa[0]['chap_URL']))
                if aa[1]:
                    await self.send_message(self.get_channel(default_channel), "JB {} chapter {}: {} [{}]".format(aa[1]['title'], aa[1]['latest_chap'], aa[1]['chap_desc'], aa[1]['chap_URL']))
        print('Update Complete')

    async def mangahelp(self, message):
        await self.send_message(message.channel, "Yohohoo {}!! I can help you keep up to date with manga releases! My commands are: `!mangacheck`, `!mangasub`, `!mangaunsub`, `!mangamysubs`, `!mangaforceupdate`. m without the manga like `!msub` works too!".format(message.author.name))

                
            
##    async def tictactoe_command(self, context):
##        await self.send_message(context.channel, 'Let\'s play tic-tac-toe!')
##
##        async def input_fn(prompt):
##            await self.send_message(context.channel, "```{}```".format(prompt))
##            user_message = await self.wait_for_message(timeout=60.0, author=context.author)
##            return user_message.content
##
##        async def say_fn(msg):
##            await self.send_message(context.channel, "```{}```".format(msg))
##
##        await tictactoe.main(input_fn, say_fn)
##
##    async def weather_command(self, context):
##        async def say_fn(msg):
##            await self.send_message(context.channel, msg)
##
##        args = context.content.split()
##        if (len(args) < 2):
##            await say_fn("You haven't chosen a city. Try `?weather perth`")
##        else:
##            await weather.fetch_weather(args[1], say_fn)

    async def reload_command(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        subprocess.Popen(["./reload.sh"])
        sys.exit()

default_channel = '342970124967346186' ##  '297260933124718593' = chatbotdev, '342970124967346186' = spoilerinotvanimango
client = LilyClient() # Create our customized client
client.run('NDAxMzc4ODUxMDgwNjM0Mzc5.DTpWXQ.MjHCpXHhhPOvw4jYlbZh53xFHg4')


