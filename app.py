from discord.ext import commands
from discord.voice_client import VoiceClient
import discord
import json
import openai
import os
from revChatGPT.revChatGPT import Chatbot
import speech_recognition as sr


if not 'DISCORD_TOKEN' in os.environ:
  raise Exception('Environment variable DISCORD_TOKEN is required')

if not 'OPENAI_API_KEY' in os.environ:
  raise Exception('Environment variable OPENAI_API_KEY is required')

if 'CHATGPT_SESSION_TOKEN' in os.environ:
  config = {
    'Authorization': '<API-KEY>',
    'session_token': os.environ['CHATGPT_SESSION_TOKEN']
  }
else:
  if not ('CHATGPT_EMAIL' in os.environ) and ('CHATGPT_PASSWORD' in os.environ):
    raise Exception('ChatGPT requires credentials in environment variables: either CHATGPT_SESSION_TOKEN or a pair of CHATGPT_EMAIL and CHATGPT_PASSWORD')
  else:
    config = {
      'email': os.environ['CHATGPT_EMAIL'],
      'password': os.environ['CHATGPT_PASSWORD']
    }

ai = Chatbot(config, conversation_id=None)
ai.refresh_session()

intents = discord.Intents.default()
# intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='/', description="AI", intents=intents)

bot.event
async def on_ready():
  print(f'Logged in as {bot.user} (ID: {bot.user.id})')
  print('------')

  @bot.command(name='halp', description='Lists available commands')
  async def halp(ctx):
    commands = bot.commands
    msg = 'Available commands:\n'
    for name, command in commands.items():
      msg += f'{name}: {command.description}\n'
    await ctx.message.channel.send(msg)

  @bot.command(name='reset_ai', description='Resets chatbot state')
  async def reset_ai(ctx):
    ai.reset_chat()
    await ctx.message.channel.send("Reset AI conversation.")

  @bot.command(description='Sends a DALL-E image to a channel')
  async def image(ctx):
    await ctx.message.author.send(f"Sending image to channel {ctx.message.channel}")
    await send_image(ctx.message)

  @bot.command(description='Joins a voice channel')
  async def join_voice(ctx):
    await ctx.message.author.send(f"Joining channel {ctx.message.channel}.")
    vc = await ctx.message.author.voice.channel.connect()
    await receive_audio(ctx.message)

  @bot.command(description='Leaves a voice channel')
  async def leave_voice(ctx):
    await ctx.message.author.send(f"Leaving channel {ctx.message.channel}")
    await ctx.message.author.voice.channel.disconnect()

async def send_discord_message(message, msg):
  import textwrap
  truncated_messages = textwrap.wrap(msg, 2000)
  if (len(truncated_messages) > 1):
    for truncated_msg in truncated_messages:
      await message.channel.send(truncated_msg)
  else:
    await message.channel.send(msg)

async def send_image(message):
  input_prompt = message.content
  if input_prompt.startswith('image'):
    prompt = input_prompt.split('image')[1]
  else:
    prompt = input_prompt

  response = openai.Image.create(
    prompt=prompt[:350],
    n=1,
    size="256x256"
  )
  image_url = response['data'][0]['url']
  await send_discord_message(message, image_url)

# this method will handle connecting to a voice channel and sending audio
async def send_audio(message):
  # get the voice channel the user is in
  voice_channel = message.author.voice.channel
  
  # connect to the voice channel
  vc = await voice_channel.connect()
  
  # create an AudioSource object using a file on disk
  audio_source = discord.FFmpegPCMAudio("path/to/audio/file.mp3")
  
  # send the audio
  vc.play(audio_source)
  
  # disconnect from the voice channel when finished
  await vc.disconnect()
  
# this method will handle receiving and processing audio from the voice channel
async def receive_audio(message):
  # get the voice channel the user is in
  voice_channel = message.author.voice.channel
  
  # connect to the voice channel
  vc = await voice_channel.connect()
  
  # create a Recognizer object
  recognizer = sr.Recognizer()
  
  # create an AudioData object from the audio in the voice channel
  audio_data = await vc.recorder.read()
  
  # use the recognizer to convert the audio data to text
  text = recognizer.recognize_google(audio_data)
  
  # use the text to get a response from the AI
  resp = ai.get_chat_response(text, output="text")
  
  # send the response to the text channel
  await send_discord_message(message, resp['message'])
  
  # disconnect from the voice channel
  await vc.disconnect()


@bot.event
async def on_message(message):
  if not message.author.id == bot.user.id:
    print(f'Received message: {message.content}')
    prompt = message.content
    resp = ai.get_chat_response(prompt, output="text")
    await send_discord_message(message, resp['message'])
  
bot.run(os.environ['DISCORD_TOKEN'])
