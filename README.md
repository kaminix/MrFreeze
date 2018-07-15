# MrFreeze
This is a discord bot only meant for use on the The Penposium discord server, a discord server for fountain pens. It's made available here mainly for backup and versioning, but feel free to use this code or parts of it for your own bot if you find it useful. The reason for making this is simply that we couldn't find a pre-made bot that filled our needs.

If you have an interest in fountain pens and want to chat with likeminded people you're welcome to check our server out, it's available via this URL: [The Penposium discord server](https://discord.gg/khY7JYs). However as of writing this the bot is not yet deployed as it's still under construction. If you'd like to chat about the bot, you may join the discord server where all the testing is made instead. [Invite to MrFreezes Cave discord server](https://discord.gg/wcwshah)

## Instructions
This bot was tested in Python 3.5.5, but should also work in 3.6. It will not work in the latest Python version due to being dependent on discord.py (rewrite version), which isn't compatible with Python 3.7. The discord.py package is available through pip. The best way I've found of running an older version of Python is to set it up as a virtual environment in pyenv.

Not wanting to upload the token of my bot to github this is read from a separate text file called 'token' which you place in the same directory as the bot. If you don't do this however, it will produce an error message with instructions on how to set this up.

## Available commands
### Fully implemented
* **!banish**   Mod-only. Assigns the tag 'Antarctica' to a user for five minutes.\n
* **!temp**     Converts a temperature from fahrenheit to celcius and vice versa.

### Almost implemented
* **!rules**    Prints a select number of rules.

### Planned but not yet implemented
* **!ban**      Mod-only. Bans the user from the server.
* **!kick**     Mod-only. Kicks the user from the server.
* **!mute**     Mod-only. Mutes the user.
* **!rps**      Play rock, paper, scissors with the bot.
* **!dice**     Roll a select number of dice. Intend to also implement option to select type of dice.
* **!region**   Allows a user to assign a regional role such as continent (could also be used for countries).
* **!vote**     Creates a vote where users vote by reacting with specified emoji.
* **!source**   Posts a link to this github page.