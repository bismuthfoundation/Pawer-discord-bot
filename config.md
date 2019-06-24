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

http://discordapp.com/developers/applications/me  
New application  
Give the bot a name  
In the box marked App Bot User, click on "Token: Click to reveal."  
scroll up to the box marked "App Details" and find your Client ID, a long number.   
Copy the number and add it to this URL, in the place of word CLIENTID.  
https://discordapp.com/oauth2/authorize?&client_id=CLIENTID&scope=bot&permissions=8  
Copy the URL with your client ID number in it into your browser.  
That’ll take you to a website where you can tell Discord where to send your bot. 
