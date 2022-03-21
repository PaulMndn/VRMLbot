import asyncio

class AdminActions:
    def __init__(self, bot):
        self.bot = bot
    
    async def help(self):
        s = ("Available admin commands:\n"
             "```\n"
             "!help        Show this help\n"
             "!msg_guilds  Message system channel in all servers\n"
             "!msg_owners  Message all server owners\n"
             "!msg_both    Message server owners and system channels in all servers\n"
            #  "!stats       Send bot stats"
             "```")
        return s
    
    async def msg_guilds(self, msg):
        async def msg_guild(g, m):
            if g.system_channel is not None:
                await g.system_channel.send(m)

        t = [msg_guild(g, msg) for g in self.bot.guilds]
        await asyncio.gather(*t)
        count = len([g for g in self.bot.guilds 
                     if g.system_channel is not None])
        return count
    
    async def msg_owners(self, msg):
        async def msg_owner(g, m):
            if g.owner_id is not None:
                owner = await self.bot.fetch_user(g.owner_id)
                await owner.send(m)
        
        t = [msg_owner(g, msg) for g in self.bot.guilds]
        await asyncio.gather(*t)
        count = len([g for g in self.bot.guilds if g.owner_id is not None])
        return count

    async def msg_both(self, msg):
        """Messages system channels (if exist) and owners of all guilds.

        Args:
            msg (str): Message to send

        Returns:
            tuple: Number of system channels and number of owners messaged.
        """
        t = [self.msg_guilds(msg),
             self.msg_owners(msg)]
        counts = await asyncio.gather(*t)
        return tuple(counts)

    async def stats(self):
        pass