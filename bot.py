import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from discord.ext.commands import Bot
import random
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD')

class SpeedDatingPool():
    def __init__(self, participants=[]):
        self.participants = participants
        self.ended = True # set to true when speed dating game is ended
        self.channels = []
        self.rounds = None
        self.interval = None
    
    def reset_pool(self):
        self.participants = []
        self.ended = True
        self.channels = []
        self.rounds = None
        self.interval = None
    
    def remove_member(self, user):
        if not user:
            return False
    
        for i in range(len(self.participants)):
            if user == self.participants[i]:
                self.participants.pop(i)
                return True
        
        return False

#IMPORTANT GLOBAL VARIABLES
pool = SpeedDatingPool()

bot = Bot(command_prefix='!')


''' Bot command: Gets the number of members in a given Voice Channel id.
'''
@bot.command(name='members', help='lists number of members in given channel')
#@commands.has_role('TC')
async def get_members(ctx, channel_id=None):
    if not channel_id:
        await ctx.send('Please specify which channel you\'d like to check!')
    else:
        channel = bot.get_channel(int(channel_id))
        if not channel:
            await ctx.send('Channel does not exist!')
            return
        members = channel.members
        await ctx.send('Members in this channel: ' + str(len(members)))

@bot.command(name='participants', help='lists participants in speed dating round')
#@commands.has_role('TC')
async def get_participants(ctx):
    await ctx.send('Participants: ' + str(pool.participants))

''' Bot command: begins a speed dating group shuffle.
'''
@bot.command(name='begin', help='starts a speed dating group')
#@commmands.has_role('TC')
async def begin_shuffle(ctx, channel_id=None):
    # command author + channel
    author = ctx.message.author
    command_channel = ctx.message.channel

    # initialize
    pool.ended = False

    if not channel_id:
        await ctx.send('Please specify which channel you\'d like to start the group in!')
        return
    channel = bot.get_channel(int(channel_id))
    if not channel:
        await ctx.send('Channel does not exist!')
        return
    pool.participants = channel.members
    print(f'Participants: {pool.participants}')

    # check if next message sent was by the author who sent the original command and in the same channel
    def check(m):
        return m.author == author and m.channel == ctx.message.channel
    
    
    rounds = 'g' # if 3 or more invalid inputs, exit speed dating start attempt
    fail_count = 0
    while (not rounds.isdigit() and rounds != 'none') and fail_count < 3:
        await ctx.send('Number of rounds? Type \'none\' if you want to manually end speed dating for an indeterminate number of rounds.') # make an option to have no rounds and just use force shuffle
        msg = await bot.wait_for('message', check=check)
        rounds = msg.content
        fail_count += 1

    if fail_count >= 3:
        await ctx.send('Too many invalid inputs. Please restart :(')
        return
    
    if rounds == 'none':
        rounds_str = 'Unset'
    else:
        rounds_str = rounds
        pool.rounds = int(rounds)

    fail_count = 0 
    time = 'hello'
    while (not time.isdigit() and time != 'none') and fail_count < 3: # while a valid time hasnt been entered
        await ctx.send('Shuffle time (in seconds) type \'none\' if you want to manually shuffle)?')
        msg = await bot.wait_for('message', check=check)
        time = msg.content
        fail_count += 1
    
    if fail_count >= 3:
        await ctx.send('Too many invalid inputs. Please restart :(')
        return
        
    if time == 'none':
        time_str = 'Unset'
    else:
        time_str = time + ' seconds'
        pool.interval = int(time)
    
    await ctx.send(f'Shuffle interval: {time_str}. Number of rounds: {rounds_str}. Let\'s speed date! ;)))') # announcement to start

    if time == 'none':
        await ctx.send('Beginning round #1')
        await shuffle(ctx)
        await ctx.send('To shuffle again, the command author must type \'!shuffle\' in this channel. To end, type \'!end\'.')
    else: # timed shuffles
        if rounds == 'none':
            played = 1 # number of rounds played
            while not pool.ended:#and len(pool.participants > 3):
                await ctx.send(f'Beginning round #{played}')
                await shuffle(ctx) # TODO: set interval somehow
                played += 1
                await asyncio.sleep(pool.interval)
        else:
            total_rounds = pool.rounds
            print(f'{total_rounds} rounds with intervals of {time_str} seconds.')
            while pool.rounds > 0 and not pool.ended: # and len(pool.participants > 3): # idk if this is valid
                await ctx.send(f'Beginning round #{total_rounds - pool.rounds + 1}')
                await shuffle(ctx) # TODO: set interval somehow
                await asyncio.sleep(pool.interval)
            
    
        if not pool.ended: # game wasn't manually ended or # of participants not enough
            await end_game(ctx)
        
        
''' Bot command: force end game.
'''
@bot.command(name='end', help='forces the game to end')
#@commands.has_role('TC')
async def force_end(ctx):
    if pool.ended:
        await ctx.send('No on-going game.')
    else:
        await end_game(ctx)

async def end_game(ctx):
    if len(pool.participants) <= 3:
        await ctx.send('Ended speed dating because we need at least 4 people :\'(')
    else:
        await ctx.send('Speed dating ended! Thanks for participating!')

    # delete all channels that were created
    for c in pool.channels:
        await c.delete() # doesn't work TODO
    
    pool.reset_pool()
    await ctx.send('Cleanup completed :)')

''' Bot command: forces a shuffle.
'''
@bot.command(name='shuffle', help='forces a shuffle')
#@commands.has_role('TC')
async def force_shuffle(ctx):
    print(pool.ended)
    if pool.ended:
        await ctx.send('No on-going game.')
    else:
        if pool.rounds != None and pool.rounds == 0:
            await ctx.send('No more rounds left!')
            await end_game(ctx)
            return
        await ctx.send('Forcing shuffle...')
        await ctx.send(f'Remaining rounds: {pool.rounds - 1}')
        await shuffle(ctx)

''' Shuffles participants into random groups.
'''
async def shuffle(ctx):
    if pool.rounds:
        pool.rounds -= 1
    guild = ctx.guild # get current server
    random.shuffle(pool.participants)
    random_joiner = None # member who gets to pick a group to join; if numbers are odd
    num_participants = len(pool.participants) # even number of ppl get shuffled; if odd, last person can pick group
    if num_participants % 2 != 0:
        random_joiner = pool.participants[-1]
        num_participants -= 1
    number_of_groups = num_participants / 2
    print(f'Number of groups: {number_of_groups}')
        
    pairs = [pool.participants[i:i+2] for i in range(0, num_participants, 2)] # change to +1 for testing purposes; add step of 2 to range
    if random_joiner: # there was an odd number
        pairs[random.randint(0, number_of_groups)].append(random_joiner)
    print(f'Groups: {pairs}')

    for i, p in enumerate(pairs):
        for m in p: # move each pair to respective channel
            channel_name = 'group' + str(i) # name of channel is groupi, where i is the pair number
            existing_channel = discord.utils.get(guild.channels, name=channel_name)
            if not existing_channel:
                print(f'Creating a new channel: {channel_name}')
                existing_channel = await guild.create_voice_channel(channel_name)
                pool.channels.append(existing_channel)
            await m.move_to(existing_channel)
    

''' Bot command: removes participant from pool.
''' 
@bot.command(name='remove', help='Removes member from list of participants.')
#@commands.has_role('TC')
async def remove_member(ctx, u_id=None):
    print('Removing...')
    if not u_id:
        await ctx.send('Please specify which member to remove!')
        return
    guild = ctx.guild
    removed_user = await guild.fetch_member(u_id)
    print(removed_user)
    if not removed_user:
        await ctx.send('Please send valid user ID!')
        return
    success = pool.remove_member(removed_user)
    if success:
        print(f'Removed {removed_user}')
        await ctx.send(f'Removed participant {removed_user.name}')
    else:
        await ctx.send(f'{removed_user.name} was already out of the pool!')

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break
    print(f'{bot.user} has connected to guild {guild.name}!')

    # set status
    await bot.change_presence(activity=discord.Game(name="I FEEL SO GOOD OH I FEEL SO GOOD"))

bot.run(TOKEN)