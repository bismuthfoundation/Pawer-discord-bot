# Pawer bot config

Pawer bot config is a config.json file, to place in the same directpry as pawer.py.

## Example config
(fake infos)

```
{
 "token": "NTE2NTEENTT2NTT2NTE2NTT2.DEY1vw.8rPXlQ_q7hbi717KqiJISETNn1o",
 "bot_channel": ["518800027999000000", "516000000998268000"]
}
```

## token

This is the bot auth token you get from discord.

## bot_channel

This is a list of channels the bot will answer in.  
It will ignore the commands from other ones.  
The first channel of the list is the one it will send non interactive messages (like "I just restarted")

The channel id is the long numeric string you get in doscord: set "developper mode" in your setting, then on right click on a channelm (or user), you now have "copy identifier".  
That is the channel id.

# How to get a token
(standard procedure whatever the discord bot is, there are online resources on this)

1. Open link [http://discordapp.com/developers/applications/me](http://discordapp.com/developers/applications/me)  
2. Click on `New application`  
3. Give the app a name  
4. Create a new bot by clicking on `Bot` and then `Create bot`  
5. On the bot page, click on `Click to Reveal Token` to get you bot token
6. Back on `General Information` copy the `Client ID`  
7. Add the Client ID to this URL (replace word CLIENTID)  
[https://discordapp.com/oauth2/authorize?&client_id=CLIENTID&scope=bot&permissions=8](https://discordapp.com/oauth2/authorize?&client_id=CLIENTID&scope=bot&permissions=8)  
8. Open the adjusted URL in your browser  
9. That’ll take you to a website where you can add the bot to a Discord server
