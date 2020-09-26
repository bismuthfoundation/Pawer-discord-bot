# Pawer bot config

Pawer bot config is a config.json file, to place in the same directory as pawer.py.

## Example config
(fake infos)

```
{
 "token": "NTE2NTEENTT2NTT2NTE2NTT2.DEY1vw.8rPXlQ_q7hbi717KqiJISETNn1o",
 "bot_channel": [5018800027999000000, 516000000998268000],
 "broadcast_restart": false, 
 "ban_impersonator": false, 
 "impersonator_info_channel" : 490000000569620000,
 "foundation_members": ["member1_name","member2_name","etc"], 
 "scammer_keywords": ["giveaway", "lucky news"],
 "scammer_avatars": ["253c85fb6f0dd090a13283f0931cbc21", "58766651d855568a66cad92d84fb2380"],
 "admin_ids" : ["3800000000000", "3800000000000"]
}
```
> **Note:** All channels or user ID's need to be stored as Integer not String for discord.py api >= 1.0.0

## token

This is the bot auth token you get from discord.

## bot_channel

This is a list of channels the bot will answer in.  
It will ignore the commands from other ones.  
The first channel of the list is the one it will send non interactive messages (like "I just restarted")

The channel id is the long numeric string you get in Discord: set "developper mode" in your setting, then on right click on a channelm (or user), you now have "copy identifier".  
That is the channel id.

## broadcast_restart

`true` or `false`  
Should the bot publish a message on its channel when it starts?

## ban_impersonator

`true` or `false`  
Activate the impersonator watch.  A user changing its handle to a `foundation_members` one, but not being listed in `admin_ids` will get auto banned.  
A message is also posted in `impersonator_info_channel` (usually, a mod reserved channel) for verification.

## scammer_keywords

A list of strings.  
Any user whose name contains any of these strings will be banned.

## scammer_avatars

A list of avatar hash, as reported by Discord image function (see avah bot function to get hash from any user).  
Users having any of these images as avatar will be banned.

## admin_ids

List of protected user id (full Discord ids)

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
