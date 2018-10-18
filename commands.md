# Pawer bot commands

Commands Specs for the Pawer bot.

## Inspiration

When possible, commands will use the same format as fatpanda bot : http://pandabot.fatpanda.club/guide.html#guide

## General syntax

`Pawer command parameter(s)`

# Commands

## Base commands

### info

Base info about Bismuth chain.

Ex: `Pawer info`

### balance

Check your current wallet balance.  
This should work in private chat with the bot as well as in the dedicated Pawer bot channel.

Ex: `Pawer balance`

### deposit

Creates a bismuth address linked to your Discord account and display it.  
Display your current address if already created.

Ex: `Pawer deposit`

**Warning**: It is *not* recommended to use that address as main Bismuth address.  
The team nor the service operator hold no responsability if your wallet or funds are lost.  
This meant to be used for tips, thanks you, quick experiments and other small amount usage.  
The matching wallet private key are stored on a secret online server.

### tip
*user*
*amount*

Tip an amount of coins from wallet to another user.  
Will create the recipient address if it does not exists yet.  

Note: subject to a max tipping constraint to prevent accidental large sum tips.

Ex: `Pawer tip @EggdraSyl 1`

### rain
*user_count*
*amount*

Tip the specified number of online users a total amount of coins.  
BOT accounts are ignored by default.  
Will create the recipient address if it does not exists yet.  

Note: subject to a max tipping constraint to prevent accidental large sum tips.

Ex: `Pawer rain 10 20` will give 10 random online users 0.5 $BIS each.

### withdraw
*bismuth_address*
*amount* or *all*

Send an amount of coins from wallet to a particular address.  
No confirmation is required.  
Tx fees are taken from your wallet.  
When using *all* instead of an amount, yhe total sent will be your balance less the fees.


## Hypernodes commands

WIP
