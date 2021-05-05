# speed-dating-bot
A Discord bot that simulates speed dating.

## Setting up
1. `git clone` this repo
2. `cd` into the local folder
3. `pip install -r requirements.txt` --> this will download all the required modules; if you are using Python 3 >= 3.4 downloaded from python.org then you should already have pip
4. log in to the Discord Developer Portal and create an application
5. make a bot in the Bot tab and copy the token
6. create a .env file in your local folder; write `DISCORD_TOKEN=token`, where `token` is your personalized bot token from step 5
7. go to the OAuth2 tab in the Portal and under the URL Generator, set bot as the scope
8. under bot permissions, set the appropriate permissions
9. copy the link under URL generator and paste into browser; add bot to desired server!