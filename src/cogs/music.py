from discord.ext import commands
from discord import utils
from discord import Embed
import discord
import lavalink

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.bot.music = lavalink.Client(self.bot.user.id)
        self.bot.music.add_node('localhost', 7000, 'testing', 'na', 'music-node')
        self.bot.add_listener(self.bot.music.voice_update_handler, 'on_socket_response')
        self.bot.music.add_event_hook(self.track_hook)


    @commands.command(name='join')
    async def join(self, ctx):
        print('IT WORKED')
        member = ctx.guild.get_member(int(ctx.author.id)) # utils.find(lambda m: m.id==ctx.author.id, ctx.channel.members)
        if member.voice is not None:
            vc = member.voice.channel
            player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
            if not player.is_connected:
                player.store('channel', ctx.channel.id)
                await self.connect_to(ctx.guild.id, str(vc.id))

    @commands.command(name='leave')
    async def disconnect(self, ctx):
        await self.connect_to(ctx.guild.id, None)

    @commands.command(name='play')
    async def play(self, ctx, *, query):
        try:
            # player = self.bot.music.player_manager.get(ctx.guild.id)
            player = self.bot.music.player_manager.get(ctx.guild.id)

            player.queue.clear()
            await player.stop()
            
            query = f'ytsearch:{query}'
            results = await player.node.get_tracks(query)

            if not results or not results['tracks']:
                return await ctx.send('No se encontró nada')

            track = results['tracks'][0]
            embed = Embed(color=discord.Color.blurple())
            embed.title = 'Track añadido'
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'

            track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True)
            player.add(requester=ctx.author.id, track=track)

            await ctx.send(embed=embed)

            if not player.is_playing:
                await player.play()

            # tracks = results['tracks'][0:10]
            # track = results['tracks'][0]
            # player.add(requester=ctx.author.id, track=track)
            # await player.play()
            '''
            i = 0
            query_result = ''
            for track in tracks:
                i += 1
                query_result += f'{i} {track["info"]["title"]} - {track["info"]["uri"]}\n'
            embed = Embed(color=discord.Color.blurple())
            embed.description = query_result
            print(query_result)
            await ctx.channel.send(embed=embed) 

            response = await self.bot.wait_for('message')
            
            track = results['tracks'][int(response.content)-1]
            player.add(requester=ctx.author.id, track=track)
            if not player.is_playing:
                await player.play()
            '''
        except Exception as e:
            print(str(e))
    
    @commands.command(name='stop')
    async def stop(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if player.is_playing:
            await player.stop()
        
    @commands.command(name='resume')
    async def resume(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            await player.play()

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)
    
    async def connect_to(self, guild_id: int, channel_id: str):
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)

def setup(bot):
    bot.add_cog(MusicCog(bot))
