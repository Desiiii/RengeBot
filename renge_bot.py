# import
import discord
import time
import random
import importlib
import logging
import sqlite3
import datetime
import asyncio

# modules
import cmds_info
import cmds_mod
import cmds_action
import cmds_currency
import cmds_games
import cmds_misc
import cmds_owner

# commands
from renge_utils import create_profile

# client
client = discord.Client()

# database
conn = sqlite3.connect('renge.db')
cur = conn.cursor()

# startup variables
prefix = 'prefix'
token = 'token'

# song of the day values
sotd_t1 = datetime.datetime.now().day
sotd_t2 = sotd_t1

# message received
@client.event
async def on_message(message):
	
	# update name in profile
	try:
		await create_profile(message.author, conn, cur)
		t = (message.author.name + '#' + message.author.discriminator, message.author.id)
		cur.execute('UPDATE profiles SET name=? WHERE id=?', t)
		conn.commit()
	except:
		pass
	
	# variables
	log_channel = discord.Object('314283195866677251')
	dm_log = discord.Object('342097197443317760')
	
	# check message source
	check = True
	if (message.server is None):
		if (message.author.bot == False):
			await client.send_message(dm_log, 'Received DM from `' + message.author.name + '#' + message.author.discriminator + '`: ' + message.content)
		check = True
	if (message.author.bot == True):
		check = False
	
	# if message received from server
	if (check == True):
		
		# transfer message to variable and format
		umsg = message.content
		umsg.lower()
		
		# check prefix
		if umsg.startswith(prefix):
			
			# more formatting
			umsg = umsg[1:]
			
			# command lists
			await cmds_info.cmds_info(message, umsg, client)
			await cmds_mod.cmds_mod(message, umsg, prefix, client)
			await cmds_action.cmds_action(message, umsg, client)
			await cmds_currency.cmds_currency(message, umsg, client, conn, cur)
			await cmds_games.cmds_games(message, umsg, client, conn, cur)
			await cmds_misc.cmds_misc(message, umsg, client, conn, cur)
			await cmds_owner.cmds_owner(message, umsg, client, conn, cur)
			
			# reload module
			if (message.author.id == '188663897279037440'):
				args = umsg.split(' ')
				if (args[0] == 'reload' and len(args) == 2):
					try:
						if (args[1] == 'action'):
							importlib.reload(cmds_action)
						elif (args[1] == 'currency'):
							importlib.reload(cmds_currency)
						elif (args[1] == 'games'):
							importlib.reload(cmds_games)
						elif (args[1] == 'info'):
							importlib.reload(cmds_info)
						elif (args[1] == 'misc'):
							importlib.reload(cmds_misc)
						elif (args[1] == 'mod'):
							importlib.reload(cmds_mod)
						elif (args[1] == 'owner'):
							importlib.reload(cmds_owner)
						else:
							raise Exception
						await client.send_message(message.channel, 'Reloaded ' + args[1] + ' command module successfully!')
					except:
						await client.send_message(message.channel, 'Failed to load module!')

# log server join
@client.event
async def on_server_join(server):
	log_channel = discord.Object('314283195866677251')
	await client.send_message(log_channel, 'Joined server `' + server.name + '`, owned by `' + server.owner.name + '#' + server.owner.discriminator + '`')

# log server leave
@client.event
async def on_server_remove(server):
	log_channel = discord.Object('314283195866677251')
	await client.send_message(log_channel, 'Left server `' + server.name + '`, owned by `' + server.owner.name + '#' + server.owner.discriminator + '`')
	
# song of the day updater
async def sotd():
	global sotd_t1
	global sotd_t2
	await client.wait_until_ready()
	while not client.is_closed:
		await asyncio.sleep(60)
		sotd_t1 = sotd_t2
		sotd_t2 = datetime.datetime.now().day
		if (sotd_t1 != sotd_t2):
			cur.execute('DELETE FROM sotd WHERE rowid=(SELECT MIN(rowid) FROM sotd)')
			conn.commit()

# startup
@client.event
async def on_ready():
	print('Logged in as:')
	print(client.user.name)
	print(client.user.id)
	print('------')
	await client.change_presence(game=discord.Game(type=0, name=prefix+'help | Nyanpasuuu~'), status=None, afk=False)
	cur.execute('DELETE FROM games')
	conn.commit()

# logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='logs.txt', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# run
random.seed(time.time())
client.loop.create_task(sotd())
client.run(token)
