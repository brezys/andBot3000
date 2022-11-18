import discord
import os
import asyncio
import youtube_dl
from dotenv import load_dotenv

from discord.ext import commands

load_dotenv()

token = os.getenv('TOKEN')

# Creates an instance of the client with its intents
client = discord.Client(intents=discord.Intents.all())

# Voice CLient
voice_clients = {}

# Song Queue
song_queue = {}


def check_queue(id):
    if song_queue[id] != []:
        player = song_queue[id].pop(0)
        voice_clients[id].play(player, after=lambda e: check_queue(id))


# Format file for best audio quality
yt_dl_best = {'format': 'bestaudio/best'}
ytdl = youtube_dl.YoutubeDL(yt_dl_best)

# Do not include video option in video search "only audio"
ffmpeg_options = {'options': '-vn'}

# Arr of blocked words
blocked_words = ["penis"]


# Once ran, this will print out the bot's name and # to the console
@client.event
async def on_ready():
    print(f'Logged in {client.user}')


# When member joins the server
@client.event
async def on_member_join(member):
    print(f'Welcome {member} to the server!')


# When member leaves the server
@client.event
async def on_member_remove(member):
    print(f'{member} has left the server.')

# Music


@client.event
async def on_message(message):
    if message.author != client.user:
        for text in blocked_words:
            if "Mod" not in str(message.author.roles) and text in str(message.content.lower()):
                await message.delete()
                return
    if message.content.startswith('!p'):
        voice_channel_joined = message.author.voice
        if voice_channel_joined is not None:
            try:
                voice_client = await message.author.voice.channel.connect()
                voice_clients[voice_client.guild.id] = voice_client
            except Exception as e:
                print(e)

            try:
                print(f"Playing song")
                url = message.content.split(' ')[1]

                # Parse into specific server with asyncio loop
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

                music = data['url']
                playing = discord.FFmpegPCMAudio(
                    music, **ffmpeg_options, executable="C:\\Users\\Nick\\Desktop\\ffmpeg\\bin\\ffmpeg.exe")

                seconds = data['duration']
                minutes, seconds = divmod(seconds, 60)
                hours, minutes = divmod(minutes, 60)

                # CHECK FOR HOURS NOT EVERY SONG HAS HOURS!
                if hours > 0:
                    dur_time = f"{hours}:{minutes}:{seconds}"
                else:
                    dur_time = f"{minutes}:{seconds}"

                await message.channel.send(f"Playing: - [{data['title']}] Duration: - [{dur_time}]")

                voice_clients[message.guild.id].play(
                    playing, after=lambda e: check_queue(message.guild.id))

            except Exception as e:
                print(e)
        else:
            await message.channel.send(f"@{message.author.name} please join a voice channel to play a song")

    if message.content.startswith('!q'):
        voice_channel_joined = message.author.voice
        if voice_channel_joined is not None:
            voice = message.guild.voice_client
            url = message.content.split(' ')[1]
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
            music = data['url']
            playing = discord.FFmpegPCMAudio(
                music, **ffmpeg_options, executable="C:\\Users\\Nick\\Desktop\\ffmpeg\\bin\\ffmpeg.exe")

            guild_id = message.guild.id

            if guild_id in song_queue:
                song_queue[guild_id].append(playing)
            else:
                song_queue[guild_id] = [playing]

            await message.channel.send(f"Added {data['title']} to the queue")

        else:
            await message.channel.send(f"@{message.author.name} please join a voice channel to queue a song")

    if message.content.startswith('!skip'):
        voice_channel_joined = message.author.voice
        if voice_channel_joined is not None:
            voice = message.guild.voice_client

            await message.channel.send(f"Stopping current song")
            voice_clients[message.guild.id].stop()
            await message.channel.send(f"Skipped song")

        else:
            await message.channel.send(f"@{message.author.name} please join a voice channel to skip a song")

    if message.content.startswith('!pau'):
        voice_channel_joined = message.author.voice
        if voice_channel_joined is not None:
            try:
                await message.channel.send(f"Pausing current song")
                await voice_clients[message.guild.id].pause()
            except Exception as e:
                print(e)
        else:
            await message.channel.send(f"@{message.author.name} please join a voice channel to pause the song")

    if message.content.startswith('!res'):
        voice_channel_joined = message.author.voice
        if voice_channel_joined is not None:
            try:
                await message.channel.send(f"Resuming current song")
                await voice_clients[message.guild.id].resume()
            except Exception as e:
                print(e)
        else:
            await message.channel.send(f"@{message.author.name} please join a voice channel to resume the song")

    if message.content.startswith('!sto'):
        voice_channel_joined = message.author.voice
        if voice_channel_joined is not None:
            try:
                song_queue.clear()
                await message.channel.send(f"Queue cleared")
                await voice_clients[message.guild.id].disconnect()
                return 1
            except Exception as e:
                print(e)
        else:
            await message.channel.send(f"@{message.author.name} please join a voice channel to stop the song")


# Runs the bot with the token
client.run(token)
