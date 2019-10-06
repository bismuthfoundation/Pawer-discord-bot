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

### rain
*total_amount*
*user_count*

Tips a total amount of coins to the specified number of random online users.
BOT accounts are ignored by default.  
Will **not** create the recipient address if it does not exists yet.  
Users that could be selected but do not have their wallet activated will get a PM, but no BIS.

Notes:
- subject to a max tipping constraint to prevent accidental large sum tips: total_amount <= 1000
- at minimum 0.1 bis per user
- 1 <= user_count <= 100

By default:
- total_amount = 10
- user_count = 10

Ex: `Pawer rain 10 20` will give 20 random online users 0.5 $BIS each.

> An additionnal alias for that is `Pawer rain 1/20`, meaning "rain 1 $BIS on 20 users".

### withdraw
*bismuth_address*  
*amount* or *all*  
*optional message (data)*

Sends an amount of coins from wallet to a particular address.  
No confirmation is required.  
Tx fees are taken from your wallet.  
When using *all* instead of an amount, the total sent will be your balance less the fees.

Ex: `Pawer withdraw 3b7fc45dfb30a95b0277ed0e5fe0244460827f59f08b8f0b9e7da66e 10`  
Ex: `Pawer withdraw 3b7fc45dfb30a95b0277ed0e5fe0244460827f59f08b8f0b9e7da66e 10 gift`

### terms

Reminds the terms of use

Ex: `Pawer terms`


## Hypernodes commands

### hypernodes

Overview of the main hypernodes metrics.  
(Notice the "s" !)

Ex: `Pawer hypernodes`

## Hypernode commands

Allows you to passively monitor all of your Hypernodes.  
Set your alerts once, and get an alert via PM every time one of your watched HN goes down.
- Sends a DM if a HN you watch is unregistered  
- Sends a DM when a HN you watch gets 3 failures in a row (around 15 min, avoids false positives)  
- Only send a PM once. The alert is then auto-reactivated when the HN goes up again.

All "hypernode" commands can also be called by the short handle "hn".

### hypernode watch
*ip* or *ip1 ip2 ip3*

Adds a hypernode ip (or list of ips, separated by spaces) to watch.  
If any of these hypernodes goes inactive, you'll get a DM (once, until you fix it)

You can watch several hypernodes by issuing several watch commands.  
Hypernode has to be registered and active to be watched.

Ex: `Pawer hypernode watch 1.2.3.4`  
Ex: `Pawer hn watch 1.2.3.4`  
Ex: `Pawer hypernode watch 1.2.3.4 1.2.4.5 1.6.7.8`  


### hypernode unwatch
*ip* or *ip1 ip2 ip3*

Removes a hypernode ip (or list of ips, separated by spaces) from watch. 

Ex: `Pawer hypernode unwatch 1.2.3.4`  
Ex: `Pawer hn unwatch 1.2.3.4`

### hypernode list

Lists all currently watched hypernodes, with their last known height (can be 5 to 10 min late) and their label.  
Failing Hypernodes are displayed in bold.

Ex: `Pawer hypernode list`  
Ex: `Pawer hn list`

### hypernode label

Defines an optional label for a hypernode you're currently watching. That label will show in the "list" command.

Ex: `Pawer hypernode label 1.2.3.4 My first Hypernode rocks!`  
Ex: `Pawer hn label 3.4.5.6 My second Hypernode is awesome`


## Dapp integrated commands

### zirco

*amount*
*bet*

Play ZircoDice from pawer wallet. For more info vist : [ZircoDice](http://bismuth.live:1212/)

Note:

- *amount* is limited to 100 $bis per bet as per [ZircoDice](http://bismuth.live:1212/) spec
- *bet* can either be `odd` or `even`

Ex: `Pawer zirco 10 odd`

### freebismuth

*tweet_url*

Register your #Bismuth tweet and get free $bis from [@freebismuth](https://twitter.com/freebismuth) twitter bot.

Note:

- *tweet_url* must use #Bismuth and \$bis and get minimum likes and retweets as per [@freebismuth](https://twitter.com/freebismuth) spec.

Ex: `Pawer freebsimuth https://twitter.com/freebismuth/status/1000356670151766016`