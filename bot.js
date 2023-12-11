const { Client, GatewayIntentBits, Events } = require("discord.js");
const { joinVoiceChannel } = require("@discordjs/voice");
const { addSpeechEvent, SpeechEvents } = require("discord-speech-recognition");
const { OpenAI } = require('openai');
const { exec } = require('child_process');
const fetch = require('node-fetch');

const client = new Client({
  intents: [
    GatewayIntentBits.GuildVoiceStates,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.Guilds,
    GatewayIntentBits.MessageContent,
  ],
});
addSpeechEvent(client);

client.on(Events.MessageCreate, (msg) => {
  // Check if the message is a command
  if (!msg.content.startsWith("/")) return;

  const args = msg.content.slice(1).trim().split(/ +/);
  const command = args.shift().toLowerCase();

  if (command === "join_voice") {
    // Join voice channel
    const voiceChannel = msg.member?.voice.channel;
    if (voiceChannel) {
      joinVoiceChannel({
        channelId: voiceChannel.id,
        guildId: voiceChannel.guild.id,
        adapterCreator: voiceChannel.guild.voiceAdapterCreator,
        selfDeaf: false,
      });
      msg.reply("Joined your voice channel!");
    } else {
      msg.reply("You need to be in a voice channel first!");
    }
  } else if (command === "halp") {
    // Send a list of commands
    msg.reply("/join_voice - Join the user's voice channel\n/halp - Display this help message");
  }
});

client.on(SpeechEvents.speech, async (msg) => {
  // If bot didn't recognize speech, content will be empty
  if (!msg.content) return;

  console.log(`Heard: ${msg.content}`);

  // Send the prompt to OpenAI's GPT-3
  // const openai = new OpenAI();
  // const response = await openai.chat.completions.create({
  //   model: "text-davinci-003",
  //   messages: [msg.content],
  //   max_tokens: 150
  // });

  const response = await fetch('https://api.openai.com/v1/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
    },
    body: JSON.stringify({
      model: 'text-davinci-003',
      prompt: msg.content,
      max_tokens: 500,
      temperature: 0
    })
  });

  const data = await response.json();
  const gptResponse = data.choices[0].text.trim();
  console.log(`Response: ${gptResponse}`);

  // Use system 'say' command to vocalize the response
  exec(`say "${gptResponse}"`, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing say command: ${error}`);
      return;
    }
    if (stderr) {
      console.error(`Error in say command: ${stderr}`);
    }
  });

});

client.on(Events.ClientReady, () => {
  console.log("Ready!");
});

client.login(process.env.DISCORD_TOKEN); // Use the environment variable for the token
