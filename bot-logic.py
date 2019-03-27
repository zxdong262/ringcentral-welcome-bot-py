"""
Sample Parrot Bot

This bot responds to any message by repeated what was said to it. 
"""
__name__ = 'localConfig'
__package__ = 'ringcentral_bot_framework'

import copy
import re
import pydash as _

botName = 'welcome-bot'

def defaultWelcomeMsg():
  return 'Welcome, new team member!:grinning:'

def help(id, welcomeMsg = defaultWelcomeMsg()):
  return f'''Hello, I am welcome bot. I will welcome every new member who join this chatgroup with message "@newmember {welcomeMsg}".

You can reply "![:Person]({id}) **set** your-welcome-message" if you want to set custom welcome message.'''


def botJoinPrivateChatAction(bot, groupId, user, dbAction):
  """
  This is invoked when the bot is added to a private group. 
  """
  where = {
    'id': f'{bot.id}#{groupId}#{botName}'
  }
  inst = dbAction('user', 'get', where)
  welcome = defaultWelcomeMsg()
  if not inst:
    dbAction('user', 'add', {
      'id': where['id'],
      'data': {
        'welcomeMsg': defaultWelcomeMsg()
      }
    })
  else:
    welcome = inst['data']['welcomeMsg']

  bot.sendMessage(
    groupId,
    {
      'text': help(bot.id, welcome)
    }
  )

def botGotPostAddAction(
  bot,
  groupId,
  creatorId,
  user,
  text,
  dbAction,
  handledByExtension,
  event
):
  """
  This is invoked when the user sends a message to the bot.
  """
  if handledByExtension or not f'![:Person]({bot.id})' in text:
    return

  m = re.match(r'.+ *set +(.+)$', text)
  where = {
    'id': f'{bot.id}#{groupId}#{botName}'
  }
  if m is None:
    inst = dbAction('user', 'get', where)
    welcome = None
    if not inst is None:
      welcome = inst['data']['welcomeMsg']
    text = help(bot.id, welcome)
    return bot.sendMessage(
      groupId,
      {
        'text': text
      }
    )

  welcomeMsg = m.group(1)
  dbAction('user', 'update', {
    'id': where['id'],
    'update': {
      'data': {
        'welcomeMsg': welcomeMsg
      }
    }
  })
  bot.sendMessage(
      groupId,
      {
        'text': 'New welcome message set'
      }
    )

def defaultEventHandler(
  bot,
  groupId,
  creatorId,
  user,
  text,
  dbAction,
  handledByExtension,
  event
):
  """
  default event handler, for event not match any above
  """
  msgType = _.get(event, 'body.body.type')
  if handledByExtension or not msgType == 'PersonsAdded':
    return

  where = {
    'id': f'{bot.id}#{groupId}#{botName}'
  }
  inst = dbAction('user', 'get', where)
  if not inst or inst['data'] is None:
    return
  added = _.get(event, 'body.body.addedPersonIds')
  at = ''
  for id in added:
    at = f'{at} ![:Person]({id})'
  at = at.strip()
  bot.sendMessage(groupId, {
    'text': f'''{at}
{inst['data']['welcomeMsg']}'''
  })