from revChatGPT.revChatGPT import Chatbot
import discord
import json
import openai
import os

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
  if 'CHATGPT_EMAIL' in os.environ:
    if 'CHATGPT_PASSWORD' in os.environ:
      config = {
        'email': os.environ['CHATGPT_EMAIL'],
        'password': os.environ['CHATGPT_PASSWORD']
      }
    else:
      raise Exception('CHATGPT_EMAIL requires CHATGPT_PASSWORD')
  else:
    raise Exception('ChatGPT requires credentials in environment variables: either CHATGPT_SESSION_TOKEN or a pair of CHATGPT_EMAIL and CHATGPT_PASSWORD')

ai = Chatbot(config, conversation_id=None)
ai.refresh_session()

class ChatBot(discord.Client):
  async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        
        if message.content == 'reset':
          ai.reset_chat()
          await message.channel.send("Reset AI conversation.")
        else:
          input_prompt = message.content
          if input_prompt.startswith('meme'):
            response = openai.Image.create(
              prompt=input_prompt,
              n=1,
              size="256x256"
            )
            image_url = response['data'][0]['url']
            await self.send_discord_message(message, image_url)
          else:
            prompt = message.content
            resp = ai.get_chat_response(prompt, output="text")
            await self.send_discord_message(message, resp['message'])

            response = openai.Image.create(
              prompt=resp['message'],
              n=1,
              size="256x256"
            )
            image_url = response['data'][0]['url']
            await self.send_discord_message(message, image_url)

  async def send_discord_message(self, message, msg):
    import textwrap
    truncated_messages = textwrap.wrap(msg, 2000)
    if (len(truncated_messages) > 1):
      for truncated_msg in truncated_messages:
        await message.channel.send(truncated_msg)
    else:
      await message.channel.send(msg)

intents = discord.Intents.default()
intents.message_content = True
client = ChatBot(intents=intents)
token = os.environ['DISCORD_TOKEN']
client.run(token)
