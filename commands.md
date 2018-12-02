# Pawer bot commands

Commands Specs for the Pawer bot.

## Inspiration

When possible, commands will use the same format as fatpanda bot : http://pandabot.fatpanda.club/guide.html#guide

## General syntax

`Pawer command parameter(s)`

Pawer commands **have** to be issued in the dedicated #pawer-bot channel or in PM with @pawer.  
They will **not** work in any other channel and you'll get into trouble for spamming!

The only exception is the tip command.

# Commands

## Base commands

### info

Base info about Bismuth chain.

Ex: `Pawer info`

### bismuth

Returns the Bismuth price on exchanges

Ex: `Pawer bismuth`

### bitcoin

Returns the average Bitcoin price

Ex: `Pawer bitcoin`

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
*optional amount (default 1)*

Tip an amount of coins from wallet to another user.  
Will not create the recipient address if it does not exists yet, the tip is not sent in that case.

Note: subject to a max tipping constraint to prevent accidental large sum tips.

Ex: `Pawer tip @EggdraSyl 1`

### rain - WIP
*user_count*
*amount*

Tip the specified number of online users a total amount of coins.  
BOT accounts are ignored by default.  
Will create the recipient address if it does not exists yet.  

Note: subject to a max tipping constraint to prevent accidental large sum tips.

Ex: `Pawer rain 10 20` will give 10 random online users 0.5 $BIS each.

> **Not functional yet**

### withdraw
*bismuth_address*
*amount* or *all*
*optional message (data)*

> all does **not** work yet

Send an amount of coins from wallet to a particular address.  
No confirmation is required.  
Tx fees are taken from your wallet.  
When using *all* instead of an amount, yhe total sent will be your balance less the fees.

Ex: `Pawer withdraw 3b7fc45dfb30a95b0277ed0e5fe0244460827f59f08b8f0b9e7da66e 10`
Ex: `Pawer withdraw 3b7fc45dfb30a95b0277ed0e5fe0244460827f59f08b8f0b9e7da66e 10 gift`

### terms

Reminds the terms of use

Ex: `Pawer terms`


## Hypernodes commands

WIP
