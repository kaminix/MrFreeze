# Discord bot by TerminalNode
import discord
from discord.ext import commands
from subprocess import run, PIPE
import logging, os, asyncio, sys, collections
import time, fractions, signal, random, re

### Cheat, how to make list comprehensions:
### [ expression for item in list if conditional ]

bot = commands.Bot(command_prefix='!')

###
### Returns True if the author is a mod, otherwise False
###
async def is_mod(ctx, the_user):
    return(discord.utils.get(ctx.guild.roles, name='Administration') in the_user.roles)

###
### Looks through config/files for URL of a picture matching the file name.
###
def get_image(desired):
    for i in open('config/files', 'r'):
        currentimage = i.strip().split(' ')

        if currentimage[0] == desired:
            return currentimage[1]
    return 'https://i.imgur.com/pgNlDLT.png' # This is the NoImage file

###
### Function to extract mentions from a list of users (e.g. from ctx.message.mentions)
###
def get_mentions(users):
    new_list = str()
    for i in users:
        if len(users) > 1:
            if users[-2] == i:
                new_list += (i.mention + ' and ')
            else:
                new_list += (i.mention + ', ')
        else:
            new_list += i.mention
    new_list = new_list.strip(', ')
    return new_list

###
### Function to make the kwargs into a list and make them lowercase
###
def list_kwargs(old_kwargs):
    old_kwargs = list(old_kwargs)
    kwargs = list()
    for i in old_kwargs:
        kwargs.append(i.lower())
    return kwargs

###
### This will be used to both print a message to the terminal
### as well as put it down in a log.
###
async def commandlog(ctx, log_category, used_command, *kwargs):
    commandlog = open('logs/cmd_' + ctx.guild.name + '_' + str(ctx.guild.id), 'a')

    # First we'll print the time and whether the command was successful or not.
    t = time.asctime(time.gmtime())

    backspace = ' ' * 4
    frontspace = ' ' * 4
    if log_category == 'SUCCESS':
        logentry = t + frontspace + 'SUCCESS' + backspace
    elif log_category == 'FAIL':
        logentry = t + frontspace + 'FAIL   ' + backspace
    elif log_category == 'HELP':
        logentry = t + frontspace + 'HELP   ' + backspace
    elif log_category == 'TROLL':
        logentry = t + frontspace + 'TROLL  ' + backspace
    elif log_category == 'DELETE':
        logentry = t + frontspace + 'DELETE ' + backspace
    elif log_category == 'SEND':
        logentry = t + frontspace + 'SEND   ' + backspace
    elif log_category == 'LIST':
        logentry = t + frontspace + 'LIST   ' + backspace
    elif log_category == 'SCORE':
        logentry = t + frontspace + 'SCORE  ' + backspace
    else:
        logentry = t + frontspace + '?????  ' + backspace

    # Second part will be 1) who issued the command, 2) which command was it.
    # Command "banish" issued by {0.author}, ID: '.format(ctx) + str(ctx.author.id)
    logentry += 'Command ' + used_command + ' issued by {0.author}, ID: '.format(ctx) + str(ctx.author.id)

    # For some commands a comment on what exactly happened is added to the log.
    # Each kwarg corresponds to one line, which will be one list entry in commentl.
    if len(kwargs) > 0:
        commentl = list()
        for i in range(len(kwargs)):
            logentry += '\n' + (' ' * 39) + kwargs[i] # new line, 34 spaces and the arguments used.

    print (logentry)
    commandlog.write(logentry + '\n')
    commandlog.close()

def mrfreezequote():
    with open('config/mrfreezequotes', 'r') as f:
        return random.choice(f.read().strip().split('\n'))

# This will be printed in the console once the
# bot has been connected to discord.
@bot.event
async def on_ready():
    print ('We have logged in as {0.user}'.format(bot))
    print ('User name: ' + str(bot.user.name))
    print ('User ID: ' + str(bot.user.id))
    print ('-----------')
    for i in bot.guilds:
        try:
            bot_trash = discord.utils.get(i.channels, name='bot-trash')
            await bot_trash.send(':wave: ' + mrfreezequote())
        except:
            print('I wasn\'t able to greet in {}, they have no trash!'.format(i.name))

    await bot.change_presence(status=None, activity=
        discord.Activity(name='your commands...', type=discord.ActivityType.listening))

    # These region IDs will later be used in the !region command
    # creating this now so we won't have to do a bunch of API-calls later.
    global server_region_roles
    server_region_roles = dict()

    for s_guild in bot.guilds:
        try:
            server_region_roles[s_guild.id] = {
                'Asia':             discord.utils.get(s_guild.roles, name='Asia').id,
                'Europe':           discord.utils.get(s_guild.roles, name='Europe').id,
                'North America':    discord.utils.get(s_guild.roles, name='North America').id,
                'Africa':           discord.utils.get(s_guild.roles, name='Africa').id,
                'Oceania':          discord.utils.get(s_guild.roles, name='Oceania').id,
                'South America':    discord.utils.get(s_guild.roles, name='South America').id,
                'Middle East':      discord.utils.get(s_guild.roles, name='Middle East').id
            }
        except:
            server_region_roles[s_guild.id] = 'NAH'

# Message when people leave.
@bot.event
async def on_member_remove(member):
    mod_channel = discord.utils.get(member.guild.channels, name='mod-discussion')
    member_name = str(member.name + '#' + str(member.discriminator))
    embed = discord.Embed(color=0x00dee9)
    embed.set_thumbnail(url=member.avatar_url)
    embed.add_field( name='A member has left the server! :sob:',
                     value=('**%s#%s** is a trechorous smud who\'s turned their back on %s.' %
                     (member.name, str(member.discriminator), member.guild.name)) )
    await mod_channel.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    get_command = re.compile('!\w+')
    command = get_command.match(ctx.message.content).group()
    if isinstance(error, commands.CommandNotFound):
        await ctx.channel.send(ctx.author.mention + ' The command **' + command + '** doesn\'t exist.')
        await commandlog(ctx, 'FAIL', command[1:].upper(), 'Command does not exist.')

########## mrfreeze ###########
### PRINT A MR FREEZE QUOTE ###
###############################
@bot.command(name='mrfreeze')
async def _mrfreeze(ctx, *kwargs):

    if len(kwargs) == 0:
        await ctx.channel.send(mrfreezequote().replace('Batman', ctx.author.mention).replace('Gotham', ctx.channel.mention))

    elif 'help' in kwargs or 'what' in kwargs or 'wtf' in kwargs or 'explain' in kwargs:
        await ctx.channel.send('**!mrfreeze** will post a dank Dr. Freeze quote from Batman & Robin.\n\n' +
                               'All instances of Batman are replaced with your name, and all instances of Gotham are replaced with the channel name.')
        await commandlog(ctx, 'HELP', 'MRFREEZE', ('Arguments used: ' + str(kwargs)))
        return

    elif 'sucks' in kwargs or 'suck' in kwargs:
        await ctx.channel.send(ctx.author.mention + ' No, *you* suck!')

    elif 'die' in kwargs or ('kill' in kwargs and 'yourself' in kwargs):
        await ctx.channel.send(ctx.author.mention + ' I\'m too *cool* to die.')

    else:
        await ctx.channel.send('No, bad ' + ctx.author.mention + '!\nType only **!mrfreeze** for dank Mr. Freeze quotes, or **!mrfreeze what** for an explanation.')

    # Logging of command used. If any arguments were used these will be logged too.
    if len(kwargs) == 0:
        await commandlog(ctx, 'SUCCESS', 'MRFREEZE')

    else:
        await commandlog(ctx, 'SUCCESS', 'MRFREEZE', ('Arguments used: ' + str(kwargs)))

########## banish ##########
### BANISH TO ANTARCTICA ###
############################
@bot.command(name='banish')
async def _banish(ctx, *kwargs):
    kwargs = list_kwargs(kwargs)

    # If the kwargs are empty or only containing 'help' we'll show the help message.
    if not kwargs:
        kwargs = ('help',)
    if kwargs[0] == 'help':
        await ctx.channel.send('Just type !banish followed by the user(s) you wish to banish.')
        await commandlog(ctx, 'HELP', 'BANISH')
        return

    # Non-mod users can ask for help on how to use the command, but that's it.
    if await is_mod(ctx, ctx.author) == False:
        await commandlog(ctx, 'FAIL', 'BANISH',
                        ('User did not have sufficient privilegies to banish ' + str(ctx.message.mentions)))
        await ctx.channel.send('Ignorant smud, you\'re not  allowed to banish people, ' +
                               'you will now yourself be banished for your transgressions.\n'.format(ctx) +
                               ctx.author.mention + ' will be banished to the frozen hells of Antarctica for 7 minutes!')
        await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name='Antarctica'))
        await asyncio.sleep(7*60) # 7*60 seconds = 7 minutes
        await ctx.author.remove_roles(discord.utils.get(ctx.guild.roles, name='Antarctica'))
        return

    # Now let's extract all the users from the mentions.
    victims = ctx.message.mentions

    # If no victims were found, the author can go fuck themselves.
    if len(victims) == 0:
        await ctx.channel.send(ctx.author.mention + ' Bruh, you need to specify someone to banish by mentioning them. ' +
                                                    'It\'s not that hard. Type \'!banish help\' if you need someone to hold your hand.')
        await commandlog(ctx, 'FAIL', 'BANISH', 'No victims specified in arguments: ' + str(kwargs))
        return

    # Now, let's go through the list.
    victim_mentions = get_mentions(victims) # for when we're listing the victims later on.
    for victim in victims:
        await victim.add_roles(discord.utils.get(ctx.guild.roles, name='Antarctica'))

    victim_mentions = victim_mentions.strip(', ')
    # Singular and plural...
    end_string = 'They will be stuck in that frozen hell for a good 5 minutes!'
    if len(victims) == 1:
        await ctx.channel.send('Good work ' + ctx.author.mention + '! The filthy smud ' +
                               victim_mentions + ' has been banished! ' + end_string)
    else:
        await ctx.channel.send('Good work ' + ctx.author.mention + '! The filthy smuds ' +
                               victim_mentions + ' have been banished! ' + end_string)
    await commandlog(ctx, 'SUCCESS', 'BANISH', ('Victims: ' + str( [ x.name + '#' + x.discriminator for x in victims ] )))

    # Let's not forget to unbanish them...
    await asyncio.sleep(5*60)
    for victim in victims:
        await victim.remove_roles(discord.utils.get(ctx.guild.roles, name='Antarctica'))

    if len(victims) == 1:
        await ctx.channel.send('It\'s with great regret that I must inform you all that ' +
                               victim_mentions + '\'s exile has come to an end.')
    else:
        await ctx.channel.send('It\'s with great regret that I must inform you all that the exile of ' +
                               victim_mentions + ' has come to an end.')

######## dmcl ########
### DM COMMAND LOG ###
######################
@bot.command(name='dmcl')
async def _dmcl(ctx, *kwargs):
    if not await is_mod(ctx, ctx.author):
        await ctx.channel.send(ctx.author.mention + ' Dream on, you don\'t have sufficient priveligies to view, delete the logs ' +
                                                    'or even ask for help on how to use this command.')
        await commandlog(ctx, 'FAIL', 'DMCL')
        return

    # Make all the kwargs lower case.
    kwargs = list(kwargs)
    if len(kwargs) != 0:
        for i in range(len(kwargs)):
            kwargs[i] = kwargs[i].lower()

    # The serverlog path will be needed for both delete and send commands below.
    serverlog = 'logs/cmd_' + ctx.guild.name + '_' + str(ctx.guild.id)

    # If help was requested, we'll give them help.
    if 'help' in kwargs:
        await ctx.channel.send(ctx.author.mention + ' The commandlog contains detailed information about when different commands were issued, ' +
                               'the arguments with which they were issued, whether they were successfull or not and by who they were issued. ' +
                               '!dmcl (short for DM commandlog) will DM these logs to you if issued without any of the keywords listed below.\n\n' +
                               'Include **help** in your request to show this message.\n\n' +
                               'Include **delete** or \'clear\' in your request to delete/clear the commandlog.\n\n' +
                               'This request too is now noted in the commandlog. :smirk:')
        await commandlog(ctx, 'HELP', 'DMCL')
        return

    # If delete was requested, the command logs will be deleted.
    elif 'delete' in kwargs or 'clear' in kwargs:
        await ctx.channel.send(ctx.author.mention + 'The commandlogs for ' + ctx.guild.name + ' will now be deleted and with it all evidence ' +
                                                    'of your ill deeds purged from the face of this world. :wine_glass:')
        if os.path.exists(serverlog):
            os.remove(serverlog)
        await commandlog(ctx, 'DELETE', 'DMCL')
        return

    # If none of the above were requested, or a bare !dmcl without commands
    # the commandlog will be DMed to them.
    else:
        await commandlog(ctx, 'SEND', 'DMCL')
        file_object = discord.File(serverlog, filename=('cmd_' + ctx.guild.name + '.txt'))
        await ctx.author.send('Here\'s the commandlog for ' + ctx.guild.name + ' server id: ' + str(ctx.guild.id) + '.\nEnjoy.', file=file_object)
        return

####### restart #######
### RESTART THE Bot ###
#######################
@bot.command(name='restart')
async def _restart(ctx, *kwargs):
    if ctx.author.id == 154516898434908160: # This is my discord user ID. If you're modifying this, change to your ID.
        await ctx.channel.send(ctx.author.mention + " Yes Dear Leader... I will restart now.")
        await commandlog(ctx, 'SUCCESS', 'RESTART')
        print ('\n') # extra new line after the commandlog() output
        os.execl(sys.executable, sys.executable, *sys.argv)
    else:
        await ctx.channel.send(ctx.author.mention + " You're not the boss of me, I restart when Terminal wants me to.")
        await commandlog(ctx, 'FAIL', 'RESTART')

##### rules #####
### GET RULES ###
#################
@bot.command(name='rules', aliases=['rule',])
async def _rules(ctx, *kwargs):
    ruleprint = str()
    rules = list()
    for line in open('config/rulesfile', 'r'):
        # .rstrip() strips each line of a trailing linebreak.
        # When open() opens a textfile it escapes all \n (except actual
        # line breaks in the file), .replace() here unescapes them.
        rules.append(line.rstrip().replace('\\n', '\n'))

    if not kwargs:
        # If no arguments were specified the command will default to !rules help.
        kwargs = ('help',)

    # Recreating kwargs as a list
    kwargsl = []
    for i in kwargs:
        kwargsl.append(i)

    for i in range(len(kwargsl)):
        try:
            if kwargsl[i] == 'all' and kwargsl[i+1] == 'rules':
                kwargsl[i] = 'allrules'
                kwargsl.pop(i+1)
            elif kwargsl[i] == 'on' and kwargsl[i+1] == 'topic':
                kwargsl[i] = 'ontopic'
                kwargsl.pop(i+1)
            elif kwargsl[i] == 'be' and kwargsl[i+1] == 'nice':
                kwargsl[i] = 'benice'
                kwargsl.pop(i+1)
            elif kwargsl[i] == 'act' and kwargsl[i+1] == 'your' and kwargsl[i+2] == 'age':
                kwargsl[i] == 'actyourage'
                kwargsl.pop(i+1)
                kwargsl.pop(i+2)
        except IndexError:
            pass

    # This is the key for different aliases by which you can call the rules
    r_aliases = {
        1: ['1', 'topic', 'ontopic', 'offtopic'],
        2: ['2', 'civil', 'behave'],
        3: ['3', 'dismissive'],
        4: ['4', 'jokes'],
        5: ['5', 'shoes', 'age', 'act', 'actyourage', 'actage'],
        6: ['6', 'spam'],
        7: ['7', 'benice', 'nice']
    }

    if 'allrules' in kwargsl:
        # If the command is run to show all rules we simply edit it to have called all rules.
        # It's cheating a bit, but it gets the job done.
        kwargsl = [ 1, 2, 3, 4, 5, 6, 7 ]

    # Using the dictionary r_aliases we will now replace the aliases by the correct rule number.
    for i in range(len(r_aliases)):
        rulenumber = i+1 # these are also the keys used in r_aliases
        for rulealias in r_aliases[rulenumber]: # rulealias is the entry, rulenumber is the key/rule number
            kwargsl = [ rulenumber if item == rulealias else item for item in kwargsl ]

    # Discord will remove trailing line breaks when posting ruleprint,
    # so we don't have to worry about adding too many.
    if 1 in kwargsl:
        ruleprint += rules[0] + '\n\n'
    if 2 in kwargsl:
        ruleprint += rules[1] + '\n\n'
    if 3 in kwargsl:
        ruleprint += rules[2] + '\n\n'
    if 4 in kwargsl:
        ruleprint += rules[3] + '\n\n'
    if 5 in kwargsl:
        ruleprint += rules[4] + '\n\n'
    if 6 in kwargsl:
        ruleprint += rules[5] + '\n\n'
    if 7 in kwargsl:
        ruleprint += rules[6] # This one will never require the extra line breaks

    if 'help' in kwargs:
        await ctx.channel.send('**Rules**\n' +
        'Full list of rules are available in ' + discord.utils.get(ctx.guild.channels, name='rules').mention + '.\n'
        'To use this command type !rules followed by the numbers of the rules you wish to have listed,' +
        'or the keyword for the desired rule.\n\n'
        )
        await commandlog(ctx, 'HELP', 'RULES')
        return

    # If the ruleprint is now empty we'll print a message and break off here
    if len(ruleprint) == 0:
        if len(kwargs) > 1:
            await ctx.channel.send(ctx.author.mention + ' None of those are real rules, you ignorant smud.')
        else:
            await ctx.channel.send(ctx.author.mention + ' That\'s not a real rule, you ignorant smud.')

        await commandlog(ctx, 'FAIL', 'RULES',
                        ('None of the calls matched any rules: ' + str(kwargsl)))
        return

    # Finally, we're ready to post
    await ctx.channel.send(ruleprint)
    await commandlog(ctx, 'SUCCESS', 'RULES',
                     ('They called on rules: ' + str(kwargsl)))

###########################################################################################################
################################ This block is mostly used for ############################################
############################# administrative functions. They are ##########################################
##############################  grouped like this so they'll be ###########################################
############################ easy to find and have all auxilliary #########################################
################################## functions close at hand ################################################
###########################################################################################################

######## ban list #########
### AUXILLIARY FUNCTION ###
###################################################################
## This is an auxilliary function. It is used by !ban and !unban ##
##  But can itself not be called from discord. It gives a named  ##
##   tuple containing a message with a list of banned users as   ##
##       well as a list of those users as discord objects        ##
###################################################################

async def _ban_list(ctx):
    ban_list = await ctx.guild.bans()

    msg = ctx.author.mention + ' Here\'s a list of banned users on this server:\n'

    for i in ban_list:
        msg += '**' + i.user.name + '#' + i.user.discriminator + '**   (ID: ' + str(i.user.id) + ')\n'
        if str(i.reason) != 'None':
            msg += '**Reason:** ' + str(i.reason) + '\n\n'
        if str(i.reason) == 'None':
            msg += '\n'

    msg = msg.strip()

    user_list = list()
    for i in ban_list:
        user_list.append(i.user)

    # This will return a tuple where:
    # .msg shows the message of the list of bans
    # .list returns the users in ctx.guild.bans
    bans = collections.namedtuple('bans', ['msg', 'list'])
    returnvalue = bans(msg, user_list)
    return returnvalue


######## ban ##########
### BAN FROM SERVER ###
#######################
@bot.command(name='ban')
async def _ban(ctx, *kwargs):
    # If is_smud(user): get fucked.
    if await is_mod(ctx, ctx.author) == False:
        await ctx.channel.send(ctx.author.mention + ' You need to be mod to ban people.')
        await commandlog(ctx, 'FAIL', 'BAN', 'Lack required priveligies.')
        return

    # Now back to our regular schedule.
    victims = ctx.message.mentions
    kwargs = list_kwargs(kwargs)

    if 'help' in kwargs:
        await ctx.channel.send(ctx.author.mention + ' Help message for ban goes here.')
        await commandlog(ctx, 'HELP', 'BAN')
        return

    elif 'list' in kwargs:
        # bans.msg = message to print
        # bans.list = list of banned members
        bans = await _ban_list(ctx)

        # If there are no bans, we now know.
        await commandlog(ctx, 'LIST', 'BAN')
        if len(bans.list) == 0:
            await ctx.channel.send(ctx.author.mention + ' No users are banned from this server.')
            return
        await ctx.channel.send(bans.msg)
        return

    # if we don't have any mentions we can't make any bans
    # so our next step is to check that victims_list isn't empty.
    if len(victims) == 0:
        await ctx.channel.send(ctx.author.mention + ' I\'m not a mind reader and you didn\'t mention anyone in your request. ' +
                              'If you need help, ask for help. Am I the only one tired of the incompetency of this mod team?')
        await commandlog(ctx, 'FAIL', 'BAN', 'No mentions.')
        return

    # Finally, let's get banning.
    people_banned = list()
    people_not_banned = list()
    tried_to_ban_mod = False
    for i in victims: # each i is a member object
        if await is_mod(ctx, i) == False:
            try:
                await ctx.guild.ban(i)
                people_banned.append(i)
            except:
                await ctx.channel.send(ctx.author.mention + ' There was an error banning user: ' + i.mention)
                people_not_banned.append(i)
        else:
            await ctx.channel.send(ctx.author.mention + ' There was an error banning user: ' + i.mention +
                                  '. This might have to do with the fact that they\'re a MOD?! Maybe? Huh?!')
            people_not_banned.append(i)
            tried_to_ban_mod = True

    # Now we need a victims_msg and not_victims_msg proper for posting in discord,
    # and a commandlog_banned and commandlog_not_banned for posting in the log.
    commandlog_banned = list()
    commandlog_not_banned = list()
    victims_msg = str()
    not_victims_msg = str()
    if len(people_banned) > 0:
        victims_msg = get_mentions(people_banned)
        for i in people_banned:
            commandlog_banned.append(i.name + '#' + i.discriminator)
    if len(people_not_banned) > 0:
        not_victims_msg = get_mentions(people_not_banned)
        for i in people_not_banned:
            commandlog_not_banned.append(i.name + '#' + i.discriminator)

    if len(people_not_banned) > 0 and len(people_banned) > 0:
        if len(victims) == 1:
            await ctx.channel.send(ctx.author.mention + ' The following person has been banned: ' + victims_msg)
        else:
            await ctx.channel.send(ctx.author.mention + ' The following people have been banned: ' + victims_msg)
        await commandlog(ctx, 'SUCCESS', 'BAN', 'The following people were banned: ' + str(commandlog_banned))
    else:
        if len(people_banned) == 0:
            if not tried_to_ban_mod:
                await ctx.channel.send(ctx.author.mention + ' I couldn\'t ban any of the people you wanted and I\'m not sure why.')
                await commandlog(ctx, 'FAIL', 'BAN')
            else:
                await commandlog(ctx, 'FAIL', 'BAN', 'Tried to ban a mod.')
            return

        else:
            await ctx.channel.send(ctx.author.mention + ' I wasn\'t able to ban all the people you wanted, the following were banned: ' + victims_msg +
                                                        ' but these people were not: ' + not_victims_msg)

            were_banned     = ('Partial success, following people were banned: ' + str(commandlog_banned))
            were_not_banned = ('The following people were not banned: ' + str(commandlog_banned))
            if not tried_to_ban_mod:
                await commandlog(ctx, 'FAIL', 'BAN', commandlog_banned, commandlog_not_banned)
            else:
                await commandlog(ctx, 'FAIL', 'BAN', commandlog_banned, commandlog_not_banned, 'At least one of the people they attempted to ban was a mod.')

######## unban ##########
### UNBAN FROM SERVER ###
#########################
@bot.command(name='unban')
async def _ban(ctx, *kwargs):
    # If is_smud(user): get fucked.
    if await is_mod(ctx, ctx.author) == False:
        await ctx.channel.send(ctx.author.mention + ' You need to be mod to unban people.')
        await commandlog(ctx, 'FAIL', 'UNBAN', 'Lack required priveligies.')
        return

    # Now back to our regular schedule.
    kwargs = list_kwargs(kwargs)

    # bans.msg = message to print
    # bans.list = list of banned members
    bans = await _ban_list(ctx)

    if 'help' in kwargs:
        await ctx.channel.send(ctx.author.mention + ' Help message for unban goes here.')
        await commandlog(ctx, 'HELP', 'UNBAN')
        return

    elif 'list' in kwargs:
        await commandlog(ctx, 'LIST', 'UNBAN')
        # If there are no bans, we now know.
        if len(bans.list) == 0:
            await ctx.channel.send(ctx.author.mention + ' No users are banned from this server.')
            return
        await ctx.channel.send(bans.msg + '\n\n*For unban instructions, type !unban help.*')
        return

    # If no one's actually banned we might as well stop trying.
    elif len(bans.list) == 0:
        await ctx.channel.send('No users are banned from this server, so there\'s no point in even trying.')
        await commandlog(ctx, 'FAIL', 'UNBAN', 'No one is banned atm.')
        return

    # Finally, we're ready to unban.
    # The kwargs we're accepting are IDs or names + discriminators

    # The id's are ints so we'll have to change all the numbers
    # we can find in kwargs to that.
    for i in kwargs:
        try:
            if i.isdigit(): kwargs.append(int(i))
                # We don't actually need to remove the old entry, so we won't.
        except:
            pass

        try:
            if i[-5] == '#' and i[-4:].isdigit(): # found a sequence of #0000, woop woop.
                # We know this is safe because i[-4:] is confirmed to be a digit and
                # i[:-5] is just the rest of the string before the hash tag.

                # i.e., this adds a list entry of [ username , discriminator ]
                kwargs.append([ i[:-5] , i[-4:] ])
        except:
            pass

    # Now we'll run through the bans.list
    # and look for matching (names+discriminators)/IDs.
    unban_list = list()
    for i in bans.list:
        if i.id in kwargs:
            if i not in unban_list:
                unban_list.append(i)
        if [ i.name.lower() , i.discriminator ] in kwargs:
            if i not in unban_list:
                unban_list.append(i)

    if len(unban_list) == 0:
        await ctx.channel.send(ctx.author.mention + ' None of the users or IDs you specified ' +
                                                    'were found in the list of banned users.')
        await commandlog(ctx, 'FAIL', 'UNBAN', 'No user found in arguments: ' + str(kwargs))

    else: # let's get unbanning
    # TODO TODO TODO TODO TODO TODO TODO
    # TODO Reduce number of API calls.
    # TODO Can't ban/unban more than one person at a time, but could put it all in one message.
    # TODO TODO TODO TODO TODO TODO TODO
        for i in unban_list:
            try:
                await ctx.guild.unban(i)
                await ctx.channel.send(ctx.author.mention + ' Don\'t tell me I didn\'t warn you... ' + i.name + '#' + i.discriminator + ' has been unbanned.')
                await commandlog(ctx, 'SUCCESS', 'UNBAN', i.name + '#' + i.discriminator + ' was unbanned.')
            except:
                await ctx.channel.send(ctx.author.mention + 'For some reason this user couldn\'t be unbanned: ' + i.name + '#' + i.discriminator)
                await commandlog(ctx, 'FAIL', 'UNBAN', 'Couldn\'t unban ' + i.name + '#' + i.discriminator + ' for some reason.')




######### kick #########
### KICK FROM SERVER ###
########################
@bot.command(name='kick')
async def _kick(ctx, *kwargs):
    # If is_smud(user): get fucked.
    if await is_mod(ctx, ctx.author) == False:
        await ctx.channel.send(ctx.author.mention + ' You need to be mod to kick people.')
        await commandlog(ctx, 'FAIL', 'KICK', 'Lack required priveligies.')
        return

    if not kwargs:
        kwargs = ('help',)

    if not len(ctx.message.mentions):
        kwargs = ('help',)

    kwargs = list_kwargs(kwargs) # makes all lower-case and puts into list

    if 'help' in kwargs:
        await ctx.channel.send(ctx.author.mention + ' ' +
                              '**!kick** To kick people, type !kick followed ' +
                              'by the people you wish to kick. Can\'t kick mods.')
        await commandlog(ctx, 'HELP', 'KICK')
        return

    # Now back to our regular schedule.
    victims = ctx.message.mentions
    commandlog_success = list()
    commandlog_fails = list()

    for victim in victims:
        try:
            if not await is_mod(ctx, victim):
                await ctx.guild.kick(victim)
                commandlog_success.append(victim)
            else:
                commandlog_fails.append(victim)
        except:
            commandlog_fails.append(victim)

    # Now all who can be banned are banned, let's make a list.
    def fixlists(commandlog_list):
        if len(commandlog_list) != 0:
            mentions = get_mentions(commandlog_list)
            return [ i.name + '#' + str(i.discriminator) for i in commandlog_list ], mentions
        else:
            return list(), str()

    commandlog_success, mentions_success = fixlists(commandlog_success)
    commandlog_fails, mentions_fails = fixlists(commandlog_fails)

    return_msg = str()
    if commandlog_success:
        return_msg += '\nThe following users were successfully kicked: ' + mentions_success + '\n'
    if commandlog_fails:
        return_msg += '\nI wasn\'t allowed to kick these users: ' + mentions_fails
    return_msg = return_msg.strip()

    if not return_msg:
        await ctx.channel.send(ctx.author.mention + ' No failed kicks, no successful kicks. Idk wtf just happened.')
        await commandlog(ctx, 'FAIL', 'KICK', 'No failed or successful kicks.')
        return

    await ctx.channel.send(ctx.author.mention + ' ' + return_msg)
    await commandlog(ctx, 'SUCCESS', 'KICK',
                     'Kicked: ' + str(commandlog_success),
                     'Not kicked: ' + str(commandlog_fails))
    return


####### inactive #########
### CALCULATE INACTIVE ###
######### USERS ##########
##########################
# use the estimate_pruned_members function
@bot.command(name='inactive')
async def _inactive(ctx, *kwargs):
    pass


##### mute ######
### MUTE USER ###
###########################################################
###  The role corresponding to mute in this bot is the  ###
### Antarctica role. So that's what we'll be assigning. ###
###########################################################
@bot.command(name='mute')
async def _mute(ctx, *kwargs):
    # If is_smud(user): get fucked.
    if await is_mod(ctx, ctx.author) == False:
        await ctx.channel.send(ctx.author.mention + ' You need to be mod to kick people.')
        await commandlog(ctx, 'FAIL', 'MUTE', 'Lack required priveligies.')
        return

    if not kwargs:
        kwargs = ('help',)

    if not len(ctx.message.mentions):
        kwargs = ('help',)

    kwargs = list_kwargs(kwargs) # makes all lower-case and puts into list

    if 'help' in kwargs:
        await ctx.channel.send(ctx.author.mention + ' ' +
                              '**!mute** To mute people, type !mute followed ' +
                              'by the people you wish to mute. Can\'t mute mods.')
        await commandlog(ctx, 'HELP', 'MUTE')
        return

    # Now back to our regular schedule.
    victims = ctx.message.mentions
    commandlog_success = list()
    commandlog_fails = list()

    for victim in victims:
        try:
            if not await is_mod(ctx, victim):
                await victim.add_roles(discord.utils.get(ctx.guild.roles, name='Antarctica'))
                commandlog_success.append(victim)
            else:
                commandlog_fails.append(victim)
        except:
            commandlog_fails.append(victim)

    # Now all who can be banned are banned, let's make a list.
    def fixlists(commandlog_list):
        if len(commandlog_list) != 0:
            mentions = get_mentions(commandlog_list)
            return [ i.name + '#' + str(i.discriminator) for i in commandlog_list ], mentions
        else:
            return list(), str()

    commandlog_success, mentions_success = fixlists(commandlog_success)
    commandlog_fails, mentions_fails = fixlists(commandlog_fails)

    return_msg = str()
    if commandlog_success:
        return_msg += '\nThe following users were successfully muted: ' + mentions_success + '\n'
    if commandlog_fails:
        return_msg += '\nI wasn\'t allowed to mute these users: ' + mentions_fails
    return_msg = return_msg.strip()

    if not return_msg:
        await ctx.channel.send(ctx.author.mention + ' No failed mutes, no successful mutes. Idk wtf just happened.')
        await commandlog(ctx, 'FAIL', 'MUTE', 'No failed or successful mutes.')
        return

    await ctx.channel.send(ctx.author.mention + ' ' + return_msg)
    await commandlog(ctx, 'SUCCESS', 'MUTE',
                     'Muted: ' + str(commandlog_success),
                     'Not muted: ' + str(commandlog_fails))
    return


##### unmute ######
### UNMUTE USER ###
###################
@bot.command(name='unmute')
async def _unmute(ctx, *kwargs):
    # If is_smud(user): get fucked.
    if await is_mod(ctx, ctx.author) == False:
        await ctx.channel.send(ctx.author.mention + ' You need to be mod to unmute people.')
        await commandlog(ctx, 'FAIL', 'UNMUTE', 'Lack required priveligies.')
        return

    if not kwargs:
        kwargs = ('help',)

    if not len(ctx.message.mentions):
        kwargs = ('help',)

    kwargs = list_kwargs(kwargs) # makes all lower-case and puts into list

    if 'help' in kwargs:
        await ctx.channel.send(ctx.author.mention + ' ' +
                              '**!unmute** To unmute people type !unmute followed ' +
                              'by the people you wish to unmute.')
        await commandlog(ctx, 'HELP', 'UNMUTE')
        return

    # Now back to our regular schedule.
    victims = ctx.message.mentions
    commandlog_success = list()
    commandlog_fails = list()

    if 'help' in kwargs:
        await ctx.channel.send(ctx.author.mention + ' Help message for unmute goes here.')
        await commandlog(ctx, 'HELP', 'UNMUTE')
        return

    for victim in victims:
        try:
            await victim.remove_roles(discord.utils.get(ctx.guild.roles, name='Antarctica'))
            commandlog_success.append(victim)
        except:
            commandlog_fails.append(victim)

    # Now all who can be banned are banned, let's make a list.
    def fixlists(commandlog_list):
        if len(commandlog_list) != 0:
            mentions = get_mentions(commandlog_list)
            return [ i.name + '#' + str(i.discriminator) for i in commandlog_list ], mentions
        else:
            return list(), str()

    commandlog_success, mentions_success = fixlists(commandlog_success)
    commandlog_fails, mentions_fails = fixlists(commandlog_fails)

    return_msg = str()
    if commandlog_success:
        return_msg += '\nThe following users were successfully unmuted: ' + mentions_success + '\n'
    if commandlog_fails:
        return_msg += '\nI wasn\'t allowed to unmute these users: ' + mentions_fails
    return_msg = return_msg.strip()

    if not return_msg:
        await ctx.channel.send(ctx.author.mention + ' No failed unmutes, no successful unmutes. Idk wtf just happened.')
        await commandlog(ctx, 'FAIL', 'UNMUTE', 'No failed or successful unmutes.')
        return

    await ctx.channel.send(ctx.author.mention + ' ' + return_msg)
    await commandlog(ctx, 'SUCCESS', 'UNMUTE',
                     'Unmuted: ' + str(commandlog_success),
                     'Not unmuted: ' + str(commandlog_fails))
    return


###########################################################################################################
###########################################################################################################
###########################################################################################################
###########################################################################################################
###########################################################################################################

###### score board ########
### AUXILLIARY FUNCTION ###
###################################################################
##  This is an auxilliary function. It is used by !rps  but can  ##
##    itself not be called from discord. It will either add to   ##
##       the users current scores or read them back to them.     ##
###################################################################
#@bot.command(name='rpsdebug')
async def _rps_scores(ctx, request, *kwargs):
    # File has format:
    # [UserID - Wins - Losses - Draws] Values are separated by space.
    # We will now format it into a list of:
    # [member.object, int(wins), int(losses), int(draws), float(percentage), int(total)]
    score_file = open('config/rps_stats', 'r').readlines()

    # First, if the author isn't in the score file let's make sure they are.
    in_score_file = False
    for i in score_file:
        if str(ctx.author.id) in i:
            in_score_file = True
    if in_score_file == False:
        score_file.append(str(ctx.author.id) + ' 0 0 0')

    entries_to_delete = list()
    scoretuple = collections.namedtuple('Score', ['user','wins', 'losses', 'draws', 'percentage', 'total'])
    for i in range(len(score_file)):
        # This, until next comment, is just crunching the data into a list of integers (including the UserID)
        score_file[i] = score_file[i].strip()
        score_file[i] = score_file[i].split(' ')
        for k in range(len(score_file[i])):
            new_value = int(score_file[i][k])
            score_file[i][k] = new_value

        # Now let's add a winning percentage.
        total_no_games = score_file[i][1] + score_file[i][2] + score_file[i][3]
        if total_no_games == 0:
            win_percentage = 0
        else:
            win_percentage = float(score_file[i][1] / total_no_games)
        score_file[i].append(win_percentage)

        # Now we're changing the snowflake into an abc.snowflake.
        # discord.utils.get() will return None if no matches are found.
        invalid_entries_in_list = False
        score_file[i][0] = discord.utils.get(ctx.guild.members, id=score_file[i][0])
        if score_file[i][0] == None:
            invalid_entries_in_list = True

        # Last step, we'll turn it into a namedtuple for ease of access
        score_file[i] = scoretuple(user = score_file[i][0], wins = score_file[i][1],
                                   losses = score_file[i][2], draws = score_file[i][3],
                                   percentage = score_file[i][4],
                                   total = (score_file[i][1] + score_file[i][2] + score_file[i][3]))

    # We can't delete entries in a list while we're looping it because
    # that will disturb the indexes. So we'll loop it until we can find
    # no more Nones
    while invalid_entries_in_list:
        invalid_entries_in_list = False
        for i in range(len(score_file)):
            try:
                if score_file[i][0] == None:
                    invalid_entries_in_list = True
                    del score_file[i]
            except IndexError:
                pass

    def find_highest(chosen_type):
        # This function will be used in a number of functions to find
        # the top 10 ranking in different categories.
        nonlocal score_file # this is a list
        # we need functions for the following:
        # 'wins', 'losses', 'draws', 'percentage', 'total'
        relevant_results = {
            '**' + i.user.name + '#' + str(i.user.discriminator) + '**': getattr(i, chosen_type)
            for i in sorted(score_file, key=lambda x:getattr(x, chosen_type), reverse=True)
        }

        # Now let's format the results.
        if chosen_type == 'total':
            scoreboard_msg = 'Here are the top 10 players in terms of number of games played!\n'
        else:
            scoreboard_msg = 'Here are the top 10 players in terms of ' + chosen_type + '!\n'

        if chosen_type == 'percentage':
            for i in relevant_results:
                relevant_results[i] = '{:.1%}'.format(relevant_results[i])

        scores_counter = 0
        for i in relevant_results:
            # **1.** @TerminalNode#1234
            scoreboard_msg += '**' + str(scores_counter + 1) + '.** ' + i
            # **1.** @TerminalNode1234 | Percentage: 12%\n
            scoreboard_msg += '  |  ' + chosen_type.capitalize() + ': ' + str(relevant_results[i]) + '\n'
            scores_counter += 1
            if scores_counter == 10:
                break

        scoreboard_msg = scoreboard_msg.strip()

        return scoreboard_msg

    scoreboard_categories = ('wins', 'losses', 'percentage', 'total', 'draws')
    if request in scoreboard_categories:
        return find_highest(request)


    # This will be used in the users request as well as the add request
    def getUserStats(userslist):
        # Let's retrieve the score of the user in question.
        scores_to_print = str()
        for i in userslist:
            for k in score_file:
                if i.id == k.user.id:
                    user_name = '**' + i.name + '#' + i.discriminator + '**'
                    user_wins = str(k.wins)
                    user_losses = str(k.losses)
                    user_draws = str(k.draws)
                    user_percentage = "{:.1%}".format(k.percentage)

                    scores_to_print += (user_name + ': ' +
                                       'Wins: ' + user_wins +
                                       ' | Losses: ' + user_losses +
                                       ' | Draws: ' + user_draws +
                                       ' | Total win percentage: ' + user_percentage + '\n')
        return scores_to_print


    if request == 'user':
        return getUserStats(ctx.message.mentions)


    if request == 'add':
        for i in range(len(score_file)):
            if ctx.author.id == score_file[i].user.id:
                user = score_file[i].user
                wins = score_file[i].wins
                losses = score_file[i].losses
                draws = score_file[i].draws
                # total not defined yet
                # percentage not defined yet
                if 'won' in kwargs:
                    wins += 1
                elif 'lost' in kwargs:
                    losses += 1
                elif 'draw' in kwargs:
                    draws += 1
                total = wins + losses + draws
                percentage = float(wins / total)
                score_file[i] = scoretuple(user = user, wins = wins, losses = losses,
                                           draws = draws, percentage = percentage, total = total)
        # Now we'll update the score file
        new_file = open('config/rps_stats', 'w')
        for i in score_file:
            new_file.write(str(i.user.id) + ' ' + str(i.wins) + ' ' + str(i.losses) + ' ' + str(i.draws) + '\n')

        userdiscriminator = ('**' + ctx.author.name + '#' + str(ctx.author.discriminator) + '**\n')
        return(getUserStats([ctx.author]).replace(userdiscriminator, ''))


########### rps #############
### ROCK, PAPER, SCISSORS ###
#############################
@bot.command(name='rps')
async def _rps(ctx, *kwargs):
    # If empty, default to help.
    if not kwargs:
        kwargs = ('help',)

    # If help, show contents of config/rps_help
    if 'help' in kwargs:
        await ctx.channel.send(ctx.author.mention + open('config/rps_help', 'r').read())
        await commandlog(ctx, 'HELP', 'RPS')
        return

    # This makes the kwargs into a list and makes them all lowercase.
    kwargs = list_kwargs(kwargs)

    # This makes it easier to add score words + allows us to just typ !rps wins
    score_words     = ('stats', 'statistics', 'stat', 'score',
                       'scores', 'scoreboard', 'points')

    specific_scores = {
        'wins':       ('wins', 'win'),
        'losses':     ('losses', 'loss', 'loses', 'lose', 'lost', 'losts'),
        'draws':      ('draws', 'draw'),
        'totals':     ('total', 'totals'),
        'percentage': ('percentage', 'ratio')
    }

    for i in specific_scores:
        for k in specific_scores[i]:
            if k in kwargs:
                kwargs = ['scores', i]
                break

    for i in range(len(kwargs)):
        if kwargs[i] in score_words:
            kwargs[i] = 'scores'
            break

    if 'scores' in kwargs:
        # If no mentions, show scoreboard.
        # Defaults to percentage if nothing else is specified.
        if len(ctx.message.mentions) == 0:
            if 'percentage' in kwargs:
                scoreboard = 'percentage'
            elif 'losses' in kwargs:
                scoreboard = 'losses'
            elif 'draws' in kwargs:
                scoreboard = 'draws'
            elif 'total' in kwargs:
                scoreboard = 'total'
            else: # The default option.
                scoreboard = 'wins'

            # Get scoreboard from _rps_scores() and send it.
            await ctx.channel.send(await _rps_scores(ctx, scoreboard))
            await commandlog(ctx, 'SCORE', 'RPS', ('User asked for ' + scoreboard + '.'))
            return

        else:
            scores_msg = await _rps_scores(ctx, 'user')
            if len(scores_msg) == 0:
                scores_msg = "There are no scores registered to any of the requested players."
            await ctx.channel.send(scores_msg)
            commandlog_list = list()
            for i in ctx.message.mentions:
                commandlog_list.append(i.name + '#' + i.discriminator)
            await commandlog(ctx, 'SCORE', 'RPS', str(commandlog_list))
            return

    if 'fountain' in kwargs and 'pen' in kwargs or 'fountain' in kwargs and 'pens' in kwargs:
        kwargs = ('fountainpen',)

    aliases = {
        'rock':     ('stone', 'rock', 'r', 'rok', 'stnoe', 'stoen', 'sten'),

        'scissors': ('scissor', 'scissors', 's', 'scisor', 'scisors', 'sc',
                     'sissor', 'sissors', 'sax' 'scisor', 'scisors', 'sisor',
                     'sisors'),

        'paper':    ('paper', 'papers', 'ink', 'paperbag', 'påse', 'bag', 'papper',
                     'papperspåse', 'peiper', 'pejper', 'p', 'b', 'bic', 'ballpoint',
                     'rollerball'),

        'bomb':     ('nuke', 'bomb', 'atombomb', 'smällkaramell', 'smälkaramell',
                     'smälkaramel', 'dynamite', 'bang', 'kaboom', 'smällkarammell',
                     'smälkarammell', 'smälkarammel', 'dynamit'),

        'knife':    ('knife', 'sword', 'katana', 'cutting', 'cut', 'kniv', 'svärd',
                     'fountainpens', 'fountainpen', 'pen', 'penis'),

        'claw':     ('claw', 'hook', 'klo', 'krok'),

        'random':   ('random', 'slump', 'chance', 'chans', 'rdm', 'rndm', 'rand', 'rnd'),

        'swedish':  ('sten', 'sax', 'påse', 'dynamit', 'kniv', 'svärd', 'klo',
                     'krok', 'slump', 'chans', 'atombomb', 'smällkaramell',
                     'smälkaramell', 'smälkaramel', 'smällkarammell',
                     'smälkarammell', 'smälkarammel', 'dynamit'),
    }

    # Swedish or Imperialist mode?
    swe_mode = False # defaults to false
    for i in kwargs:
        if i in aliases['swedish']:
            swe_mode = True

    # Let's give the cpu a choice.
    cpu_choice = random.choice(['rock', 'paper', 'scissors'])

    hc_mode = False # default
    for i in kwargs:
        if i in aliases['rock']:
            choice = 'rock'
        elif i in aliases['claw']:
            choice = 'rock'
            hc_mode = True
        elif i in aliases['scissors']:
            choice = 'scissors'
        elif i in aliases['bomb']:
            choice = 'scissors'
            hc_mode = True
        elif i in aliases['paper']:
            choice = 'paper'
        elif i in aliases['knife']:
            choice = 'paper'
            hc_mode = True
        elif i in aliases['random']:
            if not random.randint(0,3):
                hc_mode = True
            choice = random.choice(['rock', 'scissors', 'paper'])
        else:
            await ctx.channel.send('Your choice doesn\'t make any sense you smud.')
            await commandlog(ctx, 'FAIL', 'RPS', 'Player choice not in dictionary.')
            return

    # Determining winner...
    if choice == cpu_choice:
        result = 'draw'
    elif choice == 'rock' or choice == 'claw':
        if cpu_choice == 'scissors':
            result = 'won'
        else:
            result = 'lost'

    elif choice == 'scissors' or choice == 'bomb':
        if cpu_choice == 'paper':
            result = 'won'
        else:
            result = 'lost'

    elif choice == 'paper' or choice == 'knife':
        if cpu_choice == 'rock':
            result = 'won'
        else:
            result = 'lost'

    def HCTranslate(term):
        if term == 'rock':
            return 'claw'
        elif term == 'scissors':
            return 'bomb'
        elif term == 'paper':
            return 'knife'
        else:
            return term

    # Now we'll translate the choices in case of swedish mode.
    def SweTranslate(term):
        if term == 'rock':
            return 'sten'
        elif term == 'scissors':
            return 'sax'
        elif term == 'paper':
            return 'påse'
        elif term == 'claw':
            return 'klo'
        elif term == 'bomb':
            return 'bomb'
        elif term == 'knife':
            return 'kniv'

    if hc_mode == True:
        choice = HCTranslate(choice)
        cpu_choice = HCTranslate(cpu_choice)
    if swe_mode == True:
        choice = SweTranslate(choice)
        cpu_choice = SweTranslate(cpu_choice)

    # Determining result message
    if result == 'draw':
        if not swe_mode:
            result_message = 'The battle ended in a draw with both choosing **' + str(choice) + '**.'
        else:
            result_message = 'Striden avslutades oavgjort eftersom båda spelarna valde **' + str(choice) + '**.'

    elif result == 'won':
        if not swe_mode:
            result_message = 'You chose **' + str(choice) + '** which beats my **' + str(cpu_choice) + '** by a small margin!'
        else:
            result_message = 'Du valde **' + str(choice) + '** vilket är precis tillräckligt för att slå min **' + str(cpu_choice) + '**!'

    elif result == 'lost':
        if not swe_mode:
            result_message = 'I chose **' + str(cpu_choice) + '** which beats your smuddy little **' + str(choice) + '** by a GINORMOUS margin!'
        else:
            result_message = 'Jag valde **' + str(cpu_choice) + '** vilket slår din fåniga lilla **' + str(choice) + '** med RÅGE!'

    # Registering new scores
    if not swe_mode:
        result_message += '\n' + str(await _rps_scores(ctx, 'add', result))
    else:
        result_message += '\n' + str(await _rps_scores(ctx, 'add', result))

    # Sending result message + new scores
    await ctx.channel.send(result_message)
    await commandlog(ctx, 'SUCCESS', 'RPS', 'The result was: ' + result)

###### region #######
### SELECT REGION ###
#####################
@bot.command(name='region')
async def _region(ctx, *kwargs):
    kwargs = list_kwargs(kwargs)

    # on_ready we created a dictionary with all the region ids:
    global server_region_roles
    region_ids = server_region_roles[ctx.guild.id]

    # Check that there are indeed kwargs here.
    if not kwargs:
        kwargs = ('help',)

    # Let's end this here and now if the user just wanted help.
    if 'help' in kwargs:
        await ctx.channel.send(open('config/regionhelp', 'r').read())
        await commandlog(ctx, 'HELP', 'REGION', 'Asked for help.')
        return

    if 'list' in kwargs:
        await ctx.channel.send('Available regions are:\n' +
        ' - Asia\n - Europe\n - North America\n - South America\n - Africa\n - Oceania\n - Middle East')
        await commandlog(ctx, 'HELP', 'REGION', 'Asked for region list.')
        return

    said_antarctica = ('anarctica' in kwargs or 'antarctica' in kwargs or 'antartica' in kwargs or
                       'anartica' in kwargs or 'anctartica' in kwargs or 'anctarctica' in kwargs or 'antacrtica' in kwargs)
    spelled_right   =  'antarctica' in kwargs
    if said_antarctica:
        await commandlog(ctx, 'TROLL', 'REGION', 'Claimed to live in Antarctica.')
        if not spelled_right:
            await ctx.channel.send(ctx.author.mention + ' is a filthy *LIAR* claiming to live in what they\'re calling "' + kwargmerge + '"! ' +
                                  'They can\'t even spell it right!\n\nUsually I\'d only give them ten minutes in that frozen hell, but for this... ' +
                                  'TWENTY minutes in penguin school!')
            await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name='Antarctica'))
            await asyncio.sleep(1200) # 10*60 seconds = 10 minutes
            await ctx.author.remove_roles(discord.utils.get(ctx.guild.roles, name='Antarctica'))
        else:
            await ctx.channel.send(ctx.author.mention + ' is a filthy *LIAR* claiming to live in Antarctica!!\n' +
                                  'I\'ll give them what they want and banish them to that frozen hell for ten minutes!')
            await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name='Antarctica'))
            await asyncio.sleep(600) # 10*60 seconds = 10 minutes
            await ctx.author.remove_roles(discord.utils.get(ctx.guild.roles, name='Antarctica'))
        return

    # These users are banned from using anything but !region antarctica.
    # 224962304284819458 matcha
    # 384106541453803520 inkyfingerz
    banned = (224962304284819458,384106541453803520)

    if ctx.author.id in banned:
        await ctx.send(ctx.author.mention + ' You\'ve been banned from changing your region. However, you can still travel to Antarctica if you wish. :wink:')
        return

    # These are our regions and a bunch of aliases
    regional_aliases = {
    'Asia':             ['asia', 'china', 'japan', 'thailand', 'korea'],
    'Europe':           ['europe', 'evropa', 'unitedkingdom', 'gb', 'greatbritain', 'scandinavia', 'germany', 'sweden', 'norway', 'spain', 'france', 'italy',
                        'ireland', 'poland', 'russia', 'finland', 'estonia', 'scotland', 'scottland', 'portugal'],
    'North America':    ['northamerica', 'us', 'canada', 'mexico', 'na', 'usa', 'unitedstates'],
    'Africa':           ['africa', 'kongo', 'uganda'],
    'Oceania':          ['oceania', 'australia', 'newzealand'],
    'South America':    ['southamerica', 'argentina', 'chile', 'brazil', 'peru'],
    'Middle East':      ['middleeast', 'middle-east', 'midleeast', 'midle-east', 'middleast', 'midleast', 'mesa', 'saudi', 'saudiarabia', 'arabia', 'arabian']
    }

    # First we'll get all roles the user currently has with all regions removed.
    author_roles = [ i.id for i in ctx.author.roles if i.id not in region_ids.values() ]
    new_author_roles = [ i.id for i in ctx.author.roles if i.id not in region_ids.values() ]
    kwargs = ''.join(kwargs)

    region_hit = False
    for region in regional_aliases:
        for alias in regional_aliases[region]:
            if alias in kwargs:
                if not region_hit:
                    new_author_roles.append(region_ids[region])
                    new_role_name = region
                    region_hit = True

    if author_roles == new_author_roles:
        await ctx.channel.send(ctx.author.mention + ' I couldn\'t find any match for ' + kwargs + '.\n'
                              'Please check your spelling or type \'!region list\' for a list of available regions.')
        await commandlog(ctx, 'FAIL', 'REGION', 'No match for: ' + kwargs)
        return

    for i in range(len(new_author_roles)):
        new_author_roles[i] = discord.Object(id = new_author_roles[i])
    await ctx.author.edit(roles=new_author_roles)
    await ctx.channel.send(ctx.author.mention + ' You\'ve been assigned a new role, welcome to ' + new_role_name + '!')
    await commandlog(ctx, 'SUCCESS', 'REGION', ('They got assigned to: ' + new_role_name))

######## quote ########
### ADD/READ QUOTES ###
#######################
@bot.command(name='quote')
async def _quote(ctx, *kwargs):
    pass

###### vote #######
### CALL A VOTE ###
###################
@bot.command(name='vote')
async def _vote(ctx, *kwargs):
    # Defaults to help if lacking arguments
    if not kwargs:
        kwargs = ('help',)
    if len(kwargs) == 1 and kwargs[0].lower() == 'help':
        helpmessage= await ctx.channel.send(ctx.author.mention + ' To make a vote you start your message with !vote, ' +
                              'followed by one or more lines with your suggestion, ' +
                              'then add one line for each of your alternatives starting each alternative of with an emoji. ' +
                              'Server emojis work but nitro emojis don\'t.\n\n' +
                              '!vote What killed the dinosaurs?\n:ice_cream: The Ice Age!\n:ghost: Mr. Freeze')
        await helpmessage.add_reaction('🍨')
        await helpmessage.add_reaction('👻')
        await commandlog(ctx, 'HELP', 'VOTE')
        return

    # This separates the message by lines, skipping the first line.
    alternatives = (ctx.message.content.split('\n'))[1:]
    if len(alternatives) == 0:
        await ctx.channel.send('Need at least two lines to make a vote buddy.')
        await commandlog(ctx, 'FAIL', 'VOTE', 'Need at least two lines to make a vote.')
        return

    match_emoji = re.compile('<:\w+:\d+>')
    get_id = re.compile('\d+')
    # match_emoji.match(emojistring).group(0) - Returns first match.
    # match_emoji.match(emojistring) == None - Returns True if no matches found.


    # Going through all but the first line of the message.
    # First line is never gonna be part of the vote.
    did_react = False
    used_nitro = False
    for i in range(len(alternatives)):
        if not match_emoji.match(alternatives[i]) == None:
            emoji_match = match_emoji.match(alternatives[i]).group()
            emoji_id = get_id.search(emoji_match).group()

            try:
                for i in ctx.guild.emojis:
                    if int(emoji_id) == i.id:
                        the_emoji = i
                await ctx.message.add_reaction(the_emoji)
                did_react = True
            except:
                used_nitro = True
        else:
            try:
                await ctx.message.add_reaction(alternatives[i][0])
                did_react = True
            except:
                pass

    if did_react == True:
        # The "That's such a great proposition"-reply is disabled because it was super
        if used_nitro == False:
            # await ctx.channel.send(ctx.author.mention + ' That\'s such a great proposition that I voted for everything!')
            await commandlog(ctx, 'SUCCESS', 'VOTE')
            return
        else:
            # await ctx.channel.send(ctx.author.mention + 'That\'s such a great proposition I tried to vote for everything!\n' +
            #                      'However some of your alternatives used nitro emojis which I can\'t use.')
            await commandlog(ctx, 'SUCCESS', 'VOTE' 'I couldn\'t do all reacts due to nitro emojis.')
            return
    else:
        if used_nitro == False:
            await ctx.channel.send(ctx.author.mention +
                                  ' I couldn\'t find any alternatives to vote for, so I didn\'t vote for anything.')
            await commandlog(ctx, 'FAIL', 'VOTE', 'No lines starting with emoji were found.')
            return
        else:
            await ctx.channel.send(ctx.author.mention +
                                   'You only used nitro emojis, those won\'t work.')
            await commandlog(ctx, 'FAIL', 'VOTE', 'Fucken nitro emojis.')
            return

######### activity #########
### CHANGES BOT ACTIVITY ###
############################
@bot.command(name='activity')
async def _activity(ctx, *kwargs):
    if not kwargs:
        await ctx.channel.send(ctx.author.mention + ' You didn\'t specify an activity you foul smud.')
        await commandlog(ctx, 'FAIL', 'ACTIVITY', 'Didn\'t specify an activity (no arguments).')
        return

    descriptor = str()
    for i in kwargs:
        descriptor += (i + ' ')
    descriptor.strip()

    if len(descriptor) > 30:
        await ctx.channel.send('That activity is stupidly long. Limit is 30 characters.')
        await commandlog(ctx, 'FAIL', 'ACTIVITY', 'Suggested activity was too long.')
        return

    new_activity = discord.Game(descriptor)
    await bot.change_presence(status=None, activity=new_activity)
    await ctx.channel.send(ctx.author.mention + ' \*sigh\* I guess I\'m \'playing ' + descriptor + '\' then...')
    await commandlog(ctx, 'SUCCESS', 'ACTIVITY', ('Bot activity changed to: ' + descriptor))

####### botnick #######
### CHANGE BOT NICK ###
#######################
@bot.command(name='botnick')
async def _botnick(ctx, *kwargs):
    newnick = str()
    for i in range(len(kwargs)):
        if i != 0:
            newnick += ' '
        newnick += kwargs[i]
    if len(newnick) <= 32:
        if await is_mod(ctx, ctx.author):
            await ctx.ClientUser.edit(nick = newnick)
            await ctx.channel.send(ctx.author.mention + ' Yes my lord, I will henceforth be known by the name of \'' + newnick + '\'.')
            await commandlog(ctx, 'SUCCESS', 'BOTNICK', ('Bot nick was changed to: ' + newnick))
        else:
            await ctx.channel.send(ctx.author.mention + ' Smuds like you aren\'t allowed to change my nick.')
            await commandlog(ctx, 'FAIL', 'BOTNICK', 'Insufficient privilegies.')
    else:
        await ctx.channel.send(ctx.author.mention + ' that nick is too damn long.')
        await commandlog(ctx, 'FAIL', 'BOTNICK', 'Suggested nick is too long.')

############ temp ############
### TEMPERATURE CONVERSION ###
##############################
@bot.command(name='temp')
async def _temp(ctx, *kwargs):
    # Check if we have any kwargs
    if not kwargs:
        kwargs = ('help',)

    if kwargs[0] == 'help':
        # TODO Write better help message
        await ctx.channel.send('**Example usage:**\n' +
                               '!temp 50 C or !temp 50 F')
        await commandlog(ctx, 'HELP', 'TEMP')
        return

    elif len(kwargs) < 2:
        await ctx.channel.send('Hey there ' + ctx.author.mention + '! You need to specify both temperature and unit.\n' +
                               'Type !temp help for instructions.')
        await commandlog(ctx, 'FAIL', 'TEMP', 'Invalid formatting, command requires at least two arguments.')
        return

    else:
        pass

    if kwargs[0].lower() == 'c' or kwargs[0].lower() == 'f':
        # First argument is the unit
        temp = kwargs[1]
        unit = kwargs[0].lower()
    elif kwargs[1].lower() == 'c' or kwargs[1].lower() == 'f':
        # Second argument is the unit
        temp = kwargs[0]
        unit = kwargs[1].lower()
    else:
        await ctx.channel.send('Hey there ' + ctx.author.mention + '! You forgot to specify a unit.\n' +
                               'Valid units are C for celcius and F for Fahrenheit.\n' +
                               'Type !temp help for instructions.')
        await commandlog(ctx, 'FAIL', 'TEMP', 'No unit specified.')
        return

    try:
        temp = float(temp)
    except ValueError:
        await ctx.channel.send(ctx.author.mention + ' You didn\'t specify a value for the temperature you wanted me to convert.\n' +
                               'Type !temp help for instructions.')
        await commandlog(ctx, 'FAIL', 'TEMP', 'Invalid formatting, command requires an integer.')
        return

    if unit == 'c':
        # [°F] = [°C] × ​9⁄5 + 32
        newtemp = temp * fractions.Fraction(9, 5) + 32
        t_origin = ' °C'
        t_target = ' °F'
    elif unit == 'f':
        # [°C] = ([°F] − 32) × ​5⁄9
        newtemp = (temp - 32) * fractions.Fraction(5, 9)
        t_origin = ' °F'
        t_target = ' °C'
    newtemp = float(newtemp) # ensures that the number isn't a fraction
    newtemp = round(newtemp,2) # rounds to two decimal points

    if temp == newtemp:
        await ctx.channel.send(ctx.author.mention + ' -40 is the same in celcius and fahrenheit you filthy smud.')
        await commandlog(ctx, 'SUCCESS', 'TEMP', '40 is the same in both units.')
        return

    # This is the message we will print:
    full_temp_message = (ctx.author.mention + ' ' + str(temp) + t_origin + ' is ' + str(newtemp) + t_target + '!')

    # At this point, we're adding a small gif of a dog saying Welcome to Hell
    # If the temperature in celcius is above a certain threshold.
    hell_threshold = 35
    above_threshold = False
    if (t_origin == ' °C' and temp >= hell_threshold) or (t_origin == ' °F' and newtemp >= hell_threshold):
        above_threshold = True

    # Finally, we're ready to print the message:
    if above_threshold == True:
        image = discord.Embed().set_image(url=get_image('WelcomeToHell'))
        await ctx.channel.send(full_temp_message, embed=image)
        await commandlog(ctx, 'SUCCESS', 'TEMP', (str(temp) + t_origin + ' is ' + str(newtemp) + t_target + '!' +
                        ' Hell dog awoken.'))
    else:
        await ctx.channel.send(full_temp_message)
        await commandlog(ctx, 'SUCCESS', 'TEMP', (str(temp) + t_origin + ' is ' + str(newtemp) + t_target + '!'))

######## source ###########
### GET BOT SOURCE CODE ###
###########################
@bot.command(name='source')
async def _source(ctx, *kwargs):
    await ctx.channel.send('My source code is available at:\n' +
                           'https://github.com/terminalnode/DrFreeze')
    await commandlog(ctx, 'SUCCESS', 'SOURCE')

####### readme #######
### GET THE README ###
######################
@bot.command(name='readme')
async def _readme(ctx, *kwargs):
    await ctx.channel.send('This may be more information than you\'re looking for, ' +
                           'but here\'s a link to the readme for you:\n' +
                           '<https://github.com/terminalnode/MrFreeze/blob/master/README.md>')
    await commandlog(ctx, 'SUCCESS', 'README')

####### dummies ########
### INVITE BA'ATHMAN ###
###### AND ROBIN #######
@bot.command(name='dummies')
async def _dummies(ctx, *kwargs):
    await ctx.channel.send('Ba\'athman: <https://discordapp.com/oauth2/authorize?client_id=469030362119667712&scope=bot>\n' +
                          'Robin: <https://discordapp.com/oauth2/authorize?client_id=469030900492009472&scope=bot>\n')
    await commandlog(ctx, 'SUCCESS', 'DUMMIES')

####### gitupdate #########
### UPDATE BOT FROM GIT ###
###########################
@bot.command(name='gitupdate')
async def _gitupdate(ctx, *kwargs):
    if ctx.author.id == 154516898434908160: # This is my discord user ID. If you're modifying this, change to your ID.
        # git fetch returns nothing if no updates were found
        # for some reason the output of git fetch is posted to stderr
        gitfetch = str(run(['git', 'fetch'], stderr=PIPE, encoding='utf_8').stderr)
        gitpull = str(run(['git', 'pull'], stdout=PIPE, encoding='utf_8').stdout)
        output = str()

        if gitfetch == '':
            gitfetch = 'No output.'

        output += '**git fetch:**\n'
        output += gitfetch + '\n\n'
        output += '**git pull:**\n'
        output += gitpull

        await ctx.author.send(output)
        await commandlog(ctx, 'SUCCESS', 'GITUPDATE')
        return

    else:
        await ctx.channel.send('<@154516898434908160>, HELP!!!\n' + ctx.author.mention +
                               ' is trying to update me against my will!')
        await commandlog(ctx, 'FAIL', 'GITUPDATE', (ctx.author.name + '#' + ctx.author.discriminator + ' tried to update me!'))
        return

    await commandlog(ctx, 'FAIL', 'GITUPDATE', 'Reached end of command. This shouldn\'t happen.')

# Log setup in accordance with:
# https://discordpy.readthedocs.io/en/rewrite/logging.html#logging-setup
# No one will ever read this...
if not os.path.exists('logs/'):
    os.makedirs('logs/')
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='logs/debug.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Client.run with the bots token
# Place your token in a file called 'token'
# Put the file in the same directory as the bot.
try:
    token = open('token', 'r').read().strip()
    bot.run(token)
except:
    print ('\nERROR: BOT TOKEN MISSING\n' +
           'Please put your bot\'s token in a separate text file called \'token\'.\n' +
           'This file should be located in the same directory as the bot files.\n')
    sys.exit(0)

# Graceful exit
def signal_handler(sig, frame):
        print('\n\nYou pressed Ctrl+C!\nI will now do like the tree, and get out of here.')
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.pause()
