# speed-dating-bot
A Discord bot that simulates speed dating.

## Credits
Countdown functionality accredited to <a href="http://github.com/asns2001">Sanindie Silva</a>.

## Setting up
1. `git clone` this repo.
2. `cd` into the local folder.
3. `pip install -r requirements.txt` --> this will download all the required modules; if you are using Python 3 >= 3.4 downloaded from python.org then you should already have pip
4. Log in to the Discord Developer Portal and create an application.
5. Make a bot in the Bot tab and copy the token.
6. Create a `.env` file in your local folder; write `DISCORD_TOKEN=token`, where `token` is your personalized bot token from step 5, and `GUILD=guild`, where `guild` is the name of the server you want to run the bot in.
7. Go to the OAuth2 tab in the Portal and under the URL Generator, set bot as the scope.
8. Under bot permissions, set the appropriate permissions.
9. Copy the link under URL generator and paste into browser, then follow the steps to add the bot to your desired server!
10. Modify the `@commands.has_role` wrapper before each command to have the name of the role that can use the bot (or remove it entirely if you want to allow anyone to use it).
11. If you want, you can modify the status of the bot in the `on_ready` function.
12. To run the bot, simply run `python bot.py` while in the folder.

## Commands 
- !add <USER ID> - adds a guild member to the list of participants if there is a speed dating game currently happening
- !begin <CHANNEL ID> - starts a speed dating game, given the ID of the voice channel the initial participants in (note: must have 4 or more users in order to play a game); will prompt for number of rounds (if any) and the length of each round (if any)
- !end - forces the game to end
- !goodbye - logs bot out
- !help - shows a list of the commands
- !members <CHANNEL ID> - counts the number of users in the given voice channel
- !participants - lists the usernames of the participants currently in the game
- !remove <USER ID> - removes a guild member from the list of participants if there is a speed dating game currently happening
- !shuffle - force-shuffles participants around\
