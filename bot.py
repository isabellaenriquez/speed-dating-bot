import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from discord.ext.commands import Bot
import random

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD')

class SpeedDatingPool():
    def __init__(self, participants=[]):
        self.participants = participants
    
    def remove_member(self, user):
        if not user:
            return False
    
        for i in range(len(self.participants)):
            if user == self.participants[i]:
                self.participants.pop(i)
                return True
        
        return False

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
@bot.command(name='begin_shuffle', help='starts a speed dating group')
#@commmands.has_role('TC')
async def begin_shuffle(ctx, channel_id=None):
    # command author + channel
    author = ctx.message.author
    command_channel = ctx.message.channel

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

    time = 'hello'
    while not time.isdigit(): # while a valid time hasnt been entered
        await ctx.send('Shuffle time (in seconds)?')
        msg = await bot.wait_for('message', check=check)
        time = msg.content
    await ctx.send(f'Shuffle interval: {time} seconds. Let\'s speed date! ;)))')
    # TODO: actually set the interval somehow
    
    await shuffle(ctx)

''' Bot command: forces a shuffle.
'''
@bot.command(name='force_shuffle', help='forces a shuffle')
#@commands.has_role('TC')
async def force_shuffle(ctx):
    await ctx.send('Forcing shuffle...')
    await shuffle(ctx)

''' Shuffles participants into random groups.
'''
async def shuffle(ctx):
    if len(pool.participants) <= 3:
        await ctx.send('Need at least 4 people to speed date :(((')
        return
    guild = ctx.guild # get current server
    random.shuffle(pool.participants)
    random_joiner = None # member who gets to pick a group to join; if numbers are odd
    num_participants = len(pool.participants) # even number of ppl get shuffled; if odd, last person can pick group
    if num_participants % 2 != 0:
        random_joiner = pool.participants[-1]
        num_participants -= 1
    number_of_groups = num_participants / 2
    print(f'Number of groups: {number_of_groups}')

    """ # test purposes bc i am one person lol i just needed to see if it would move me
    if number_of_groups == 0:
        # only one person being shuffled
        channel_name = 'group0'
        existing_channel = discord.utils.get(guild.channels, name=channel_name)
        if not existing_channel:
            existing_channel = await guild.create_voice_channel(channel_name)
        await group[0].move_to(existing_channel)
        return"""
        
    pairs = [pool.participants[i:i+2] for i in range(0, num_participants, 2)]
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