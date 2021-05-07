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
        self.main_channel = None
    
    def reset_pool(self):
        self.participants = []
        self.ended = True
        self.channels = []
        self.rounds = None
        self.interval = None
        self.main_channel = None
    
    def remove_member(self, user):
        if not user:
            return False
    
        for i in range(len(self.participants)):
            if user == self.participants[i]:
                self.participants.pop(i)
                return True
        
        return False
    
    def add_member(self, user):
        if not user:
            return False
        elif user in self.participants:
            return False # user was already in pool
        else:
            self.participants.append(user)
            return True

#IMPORTANT GLOBAL VARIABLES
pool = SpeedDatingPool()

bot = Bot(command_prefix='!')

''' Bot command: Gets the number of members in a given Voice Channel id.
'''
@bot.command(name='members', help='Lists number of members in the channel corresponding to the given ID')
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

''' Bot command: Sends a list of the participants registered in the current game.
'''
@bot.command(name='participants', help='Lists the participants in the current speed dating game')
#@commands.has_role('TC')
async def get_participants(ctx):
    if pool.ended:
        await ctx.send('No on-going game.')
        return
    p_string = ''
    for i, p in enumerate(pool.participants):
        if i == len(pool.participants) - 1:
            p_string += p.name
        else:
            p_string += p.name + ', '
    await ctx.send(f'Participants: {p_string}')

''' Bot command: begins a speed dating group shuffle.
'''
@bot.command(name='begin', help='Starts a speed dating game with the users in the specified VC (by ID)')
#@commands.has_role('TC')
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
    pool.main_channel = channel
    pool.participants = channel.members
    print(f'Participants: {pool.participants}')

    
    if not pool_is_valid():
        await ctx.send('Sorry, we need 4 or more people to play :(')
        pool.reset_pool() # just in case
        return

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
            print('number of rounds unset.')
            played = 1 # number of rounds played
            while not pool.ended and len(pool.participants) > 3:
                await ctx.send(f'Beginning round #{played}')
                await shuffle(ctx) # TODO: set interval somehow
                played += 1
                await asyncio.sleep(pool.interval)
        else:
            total_rounds = pool.rounds
            print(f'{total_rounds} rounds with intervals of {time_str} seconds.')
            while not pool.ended and len(pool.participants) > 3 and pool.rounds > 0: # idk if this is valid
                await ctx.send(f'Beginning round #{total_rounds - pool.rounds + 1}')
                await shuffle(ctx) # TODO: set interval somehow
                await asyncio.sleep(pool.interval)
            
    
        if not pool.ended: # game wasn't manually ended or # of participants not enough
            await end_game(ctx)

''' Returns true if there are 4+ participants, false otherwise.
'''    
def pool_is_valid():
    if len(pool.participants) > 3:
        return True
    return False
        
''' Bot command: force end game.
'''
@bot.command(name='end', help='Forces the game to end')
#@commands.has_role('TC')
async def force_end(ctx):
    if pool.ended:
        await ctx.send('No on-going game.')
    else:
        await end_game(ctx)

''' Housekeeping for ending a game.
'''
async def end_game(ctx):
    if len(pool.participants) <= 3:
        await ctx.send('Ended speed dating because we need at least 4 people :\'(')
    else:
        await ctx.send('Speed dating ended! Thanks for participating!') 
    
    for p in pool.participants:
        try:
            await p.move_to(pool.main_channel)
        except:
            await ctx.send(f'Hey <@{p.id}>! I couldn\'t find you :( Please join the main channel again!')
    
    # delete all channels that were created
    for c in pool.channels:
        await c.delete()
    
    pool.reset_pool()
    await ctx.send('Cleanup completed :)')

''' Bot command: forces a shuffle.
'''
@bot.command(name='shuffle', help='Forces a shuffle')
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
        if pool.rounds != None:
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
    #print(f'Number of groups: {number_of_groups}')
    
    pairs = [pool.participants[i:i+2] for i in range(0, num_participants, 2)] # change to +1 for testing purposes; add step of 2 to range
    if random_joiner: # there was an odd number
        try:
            pairs[random.randint(0, int(number_of_groups) - 1)].append(random_joiner)
        except IndexError:
            await ctx.send(f'<@{random_joiner.id}>, you\'ve been selected randomly to join a random group! The world is your oyster :)')
    print(f'Groups: {pairs}')

    for i, p in enumerate(pairs):
        for m in p: # move each pair to respective channel
            channel_name = 'group' + str(i) # name of channel is groupi, where i is the pair number
            existing_channel = discord.utils.get(guild.channels, name=channel_name)
            if not existing_channel: # not created yet
                print(f'Creating a new channel: {channel_name}')
                existing_channel = await guild.create_voice_channel(channel_name)
                pool.channels.append(existing_channel)
            try:
                await m.move_to(existing_channel)
            except:
                await ctx.send(f'<@{m.id}> I couldn\'t find you! Please join {channel_name}!')
    

''' Bot command: removes participant from pool.
''' 
@bot.command(name='remove', help='Removes member from list of participants using that guild member\'s ID')
#@commands.has_role('TC')
async def remove_member(ctx, u_id=None):
    if pool.ended:
        await ctx.send('No on-going game to remove from!')
        return

    print('Removing...')
    if not u_id:
        await ctx.send('Please specify which member to remove!')
        return
    guild = ctx.guild
    removed_user = await guild.fetch_member(u_id)
    if not removed_user:
        await ctx.send('Please send valid user ID (user must be in this guild)!')
        return
    success = pool.remove_member(removed_user)
    if success:
        print(f'Removed {removed_user}!')
        await ctx.send(f'Removed participant <@{u_id}>. I\'ll miss you :(')
    else:
        await ctx.send(f'{removed_user.name} was already out of the pool!')

''' Bot command: adds participant to pool.
'''
@bot.command(name='add', help='Adds a member to the list of participants using that guild member\'s ID')
#@commands.has_role('TC')
async def add_member(ctx, u_id=None):
    if pool.ended:
        await ctx.send('No on-going game to add to.')
        return

    print('Adding...')
    if not u_id:
        await ctx.send('Please specify which member to add!')
        return
    guild = ctx.guild
    added_user = await guild.fetch_member(u_id)
    if not added_user:
        await ctx.send('Please send valid user ID (user must be in this guild)!')
        return
    success = pool.add_member(added_user)
    if success:
        print(f'Added {added_user}!')
        await ctx.send(f'Added participant <@{u_id}>! Welcome to speed dating! ;)))')
    else:
        await ctx.send(f'{added_user.name} was already in the pool!')

''' Bot command: shutdowns bot.
'''
@bot.command(name='goodbye', help='Log bot out')
#@commands.has_role('TC')
async def log_out(ctx):
    await ctx.send('Goodbye, thanks for having me!')
    await bot.close()

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break
    print(f'{bot.user} has connected to guild {guild.name}!')

    # set status
    await bot.change_presence(activity=discord.Game(name="I FEEL SO GOOD OH I FEEL SO GOOD"))

bot.run(TOKEN)