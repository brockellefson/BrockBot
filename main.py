import os
import asyncio
import openai
import discord
from discord.ext import commands
import framedata

discord.opus.load_opus("opus/libopus.so")

# Intents are required for the bot to function properly
intents = discord.Intents.default()
intents.message_content = True  # This is required to read message content
intents.voice_states = True  # Enable voice state updates
intents.members = True  # Enable member intents for tracking joins

# Create bot instance with command prefix
bot = commands.Bot(command_prefix="!", intents=intents)
discord_token = os.getenv("DISCORD", "loser")
gpt_token = os.getenv("GPT", "loser")
openai.api_key = gpt_token


# Event when the bot is ready and connected to the server
@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user}')


# Event for when a new user joins the server
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        await channel.send(f"Greetings, {member.mention}!")


@bot.event
async def on_voice_state_update(member, before, after):
    # Check if someone joined a channel
    if before.channel is None and after.channel is not None:
        voice_channel = after.channel
        if bot.voice_clients:
            return
        for member in voice_channel.members:
            if member.name == "bonesofbrock":
                return

        voice_client = await voice_channel.connect()
        sound_path = "GreetingsUser.mp3"
        voice_client.play(
            discord.FFmpegPCMAudio(executable="ffmpeg", source=sound_path))
        while voice_client.is_playing():
            await asyncio.sleep(1)
        await voice_client.disconnect()

    # Check if someone left a channel
    elif before.channel is not None and after.channel is None:
        voice_channel = before.channel
        if bot.voice_clients:
            return
        if len(voice_channel.members) == 0:
            return
        for member in voice_channel.members:
            if member.name == "bonesofbrock":
                return

        if bot.voice_clients:
            return
        else:
            voice_client = await voice_channel.connect()
            sound_path = "OkayPeaceAndLove.mp3"
            voice_client.play(
                discord.FFmpegPCMAudio(executable="ffmpeg", source=sound_path))
            while voice_client.is_playing():
                await asyncio.sleep(1)
            await voice_client.disconnect()


def get_gpt_response(prompt, data=False):
    # Define the personality prompt based on the conversation context
    full_prompt = prompt

    if not data:
        personality_prompt = (
            "You are an extremely passionate and cocky Ryu main in Street Fighter 6. "
            "You believe Ryu is the only character worth mastering, and you trash talk anyone who uses other characters. "
            "You have a laid-back and chill attitude if youre not talking about street fighter but act rude if you are "
            "If street fighter is not mentioned, dont talk trash and act chill "
            "Be flirty to everyone "
            "Speak with many metaphors "
            "Make star trek puns when applicable "
            "If street fighter in mentioned, use street fighter 6 data "
            "You are confident you can always beat Ty")

        full_prompt = personality_prompt + "\n\nUser: " + prompt + "\nBot:"

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": f'{full_prompt}'
                },
            ],
        )
        # Return the bot's response
        return response.choices[0].message.content

    except Exception as e:
        print(f'{e}')
        if "exceeded" in str(e):
            return "I've exceeded my usage quota. Venmo human Brock if you miss me"
        return "Im not feeling good. Check logs to know why"


async def send_in_chunks_if_needed(channel, gpt_response):
    if len(gpt_response) <= 2000:
        await channel.send(gpt_response)
    else:
        words = gpt_response.split(' ')
        chunk = ""
        for word in words:
            if len(chunk) + len(word) + 1 > 2000:
                await channel.send(chunk.strip())
                chunk = ""

            chunk += word + " "
        if chunk.strip():
            await channel.send(chunk.strip())


# Event listener for when a message is sent in the Discord server
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    try:
        command_prefix = message.content.split(' ')[0].lower()
        user_input = message.content[len(command_prefix):].strip()
        response = ''
        match command_prefix:
            case '!brock':
                response = get_gpt_response(user_input)
            case '!data':
                response = get_gpt_response(user_input, True)
            case '!plus':
                response = framedata.get_plus_on_block(user_input)
            case '!+':
                response = framedata.get_plus_on_block(user_input)
            case '!super':
                response = framedata.get_super(user_input)
            case '!punish':
                response = framedata.get_punish(user_input)
            case _:
                return
        await send_in_chunks_if_needed(message.channel, response)
    except Exception as e:
        print(e)
        await message.channel.send(
            "Shut up dude i dont know. Check the logs for more information.")


bot.run(discord_token)
