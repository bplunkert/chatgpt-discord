from revChatGPT.revChatGPT import Chatbot
import discord
import json
import openai
import os

if not 'DISCORD_TOKEN' in os.environ:
  raise Exception('Environment variable DISCORD_TOKEN is required')

if not 'OPENAI_API_KEY' in os.environ:
  raise Exception('Environment variable OPENAI_API_KEY is required')
else:
  openai.api_key = os.getenv("OPENAI_API_KEY")

class ChatBot(discord.Client):
  async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        
        # if message.content == 'reset':
        #   ai.reset_chat()
        #   await message.channel.send("Reset AI conversation.")

        else:
          prompt = message.content
          response = openai.Completion.create(
            model="code-davinci-002",
            prompt="You: How do I combine arrays?\nJavaScript chatbot: You can use the concat() method.\nYou: How do you make an alert appear after 10 seconds?\nJavaScript chatbot",
            temperature=0,
            max_tokens=60,
            top_p=1.0,
            frequency_penalty=0.5,
            presence_penalty=0.0,
            stop=["You:"]
          ).choices[0].text
          await self.send_discord_message(message, response)

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
