from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from os import name
import time
import pickle

import telebot
from telebot import types
# import apiai
# import sys
import os
# import dialogflow
# import json
from random import randint


TOKEN = '1687652075:AAGfc0Y3I3R4TBn7VbHqdJuoXYjpvihnHEU'

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SCOPES2 = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1qy8A6BLjuX5O-WS6ZvDruAYCk6-_VAAw4Sso5RrYRS4'
SAMPLE_RANGE_NAME = 'Phrasal!A2:G'

SAMPLE_SPREADSHEET_ID4 = '1aTuORBpSTca88TAR2X4DYt_AH789CUQGTrY8QbqbrsY'
SAMPLE_RANGE_NAME4 = 'LOGdata!A1:D'

knownUsers = []  # todo: save these in a file,
usersInfo = []
userStep = {}  # so they won't reset every time the bot restarts

commands = {  # command description used in the "help" command
    'start'       : 'to start with',
    'help'        : 'gives you information about the available commands',
    'exercise'    : 'grammar & vocabulary exercises',
    'explore'     : 'some usefull and interesting recomendations',
    'chat'        : 'have a nice chat & improve your speeking skills',
    'new'         : 'update current user info'
}
interests = ['Fashion', 'Ecology', 'Travel', 'Art', 'IT', 'Psychology']
goals = ['Подготовиться к экзамену', 'Пополнить словарный запас', 'Для учебы, подтянуть конкретные темы', 'Улучшить разговорный английский']
formats = ['Грамматика', 'Лексика', 'Чтение']
comfyTime = None

hideBoard = types.ReplyKeyboardRemove()  # if sent as reply_markup, will hide the keyboard

# error handling if user isn't known yet
# (obsolete once known users are saved to file, because all users
#   had to use the /start command and are therefore known to the bot)
def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        knownUsers.append(uid)
        userStep[uid] = 0
        print("New user detected, who hasn't used \"/start\" yet")
        return 0


# only used for console output now
def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        if m.content_type == 'text':
            # print the sent message to the console
            print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)


bot = telebot.TeleBot(TOKEN)
bot.set_update_listener(listener)  # register listener

# handle the "/start" command
@bot.message_handler(commands=['start'])
def command_start(m):
    cid = m.chat.id
    if cid not in knownUsers:  # if user hasn't used the "/start" command yet:
        knownUsers.append(cid)  # save user id, so you could brodcast messages to all users of this bot later
        userStep[cid] = 0  # save user id and his current "command level", so he can use the "/getImage" command
        markup = types.ForceReply(selective=False)
        bot.send_message(cid, "Привет! Как тебя зовут?", reply_markup=markup)
        bot.register_next_step_handler(m, get_name) 
        # bot.send_message(cid, "Scanning complete, I know you now")
        # command_help(m)  # show the new user the help page
    else:
        bot.send_message(cid, "I already know you, no need for me to scan you again!")
def get_name(message):
    global name
    name = message.text
    usersInfo.append([name])
    markup = types.ReplyKeyboardMarkup(row_width=2)
    t1 = types.KeyboardButton('A1')
    t2 = types.KeyboardButton('A2')
    t3 = types.KeyboardButton('B1')
    t4 = types.KeyboardButton('B2')
    t5 = types.KeyboardButton('C1')
    t6 = types.KeyboardButton('C2')
    markup.add(t1, t2, t3, t4, t5, t6)
    bot.send_message(message.from_user.id, 'Какой у тебя уровень английского?', reply_markup=markup)
    bot.register_next_step_handler(message, get_level)
def get_level(message):
    global level
    level = message.text
    usersInfo.append([level])
    bot.send_message(message.from_user.id, 'Рад познакомиться, '+name+'! Сейчас твой уровень английского '+level+'. Уверен, что с моей помощью ты его не только поднимешь, но и просто интересно проведешь время!')
    markup = types.ReplyKeyboardMarkup(row_width=3)
    t1 = types.KeyboardButton(interests[0])
    t2 = types.KeyboardButton(interests[1])
    t3 = types.KeyboardButton(interests[2])
    t4 = types.KeyboardButton(interests[3])
    t5 = types.KeyboardButton(interests[4])
    t6 = types.KeyboardButton(interests[5])
    markup.add(t1, t2, t3, t4, t5, t6)
    bot.send_message(message.from_user.id, 'Расскажи мне о своих интересах', reply_markup=markup)
    bot.register_next_step_handler(message, get_int)
def get_int(message):
    usersInfo.append([message.text])
    markup = types.ReplyKeyboardMarkup(row_width=1)
    t1 = types.KeyboardButton(goals[0])
    t2 = types.KeyboardButton(goals[1])
    t3 = types.KeyboardButton(goals[2])
    t4 = types.KeyboardButton(goals[3])
    markup.add(t1, t2, t3, t4)
    bot.send_message(message.from_user.id, 'Здорово! В дальнейшем мы будем присылать подборки с познавательными материалами на основе твоих интересов.', reply_markup=hideBoard)
    bot.send_message(message.from_user.id, 'А теперь расскажи мне про свои цели в изучении английского:', reply_markup=markup)
    # bot.answer_callback_query(message.from_user.id, text="Супер!")

    # bot.send_message(message.from_user.id, 'Готов начать?')
    # get_goals(message)
    bot.register_next_step_handler(message, get_goals)

def get_goals(message):
    global goals
    goals = message.text
    usersInfo.append([message.text])
    bot.send_message(message.from_user.id, "Супер! Теперь я могу составлять индивидуальные рекомендации и помогать тебе с изучением английского!")
    creds = None
    if os.path.exists('token4.json'):
        creds = Credentials.from_authorized_user_file('token4.json', SCOPES2)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES2)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token4.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)
    service.spreadsheets().values().append(
        spreadsheetId=SAMPLE_SPREADSHEET_ID4,
        range=SAMPLE_RANGE_NAME4,
        body={
            "majorDimension": "COLUMNS",
            "values": usersInfo
        },
        valueInputOption="USER_ENTERED"
    ).execute()
    usersInfo.clear()
    command_help(message)  # show the new user the help page


@bot.message_handler(commands=['new'])
def toNull(m):
    cid = m.chat.id
    knownUsers.remove(cid)

# help page
@bot.message_handler(commands=['help'])
def command_help(m):
    cid = m.chat.id
    help_text = "Вот список доступных команд: \n"
    for key in commands:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(cid, help_text, reply_markup=hideBoard)  # send the generated help page


# chat_action example (not a good one...)
@bot.message_handler(commands=['chat'])
def command_chat(m):
    cid = m.chat.id
    # bot.send_message(cid, "Let's talk!")
    bot.send_chat_action(cid, 'typing')  # show the bot "typing" (max. 5 secs)
    time.sleep(1)
    # bot.send_message(cid, ".")
    command_default(m)


@bot.message_handler(commands=['exercise'])
def command_ex(m):
    cid = m.chat.id
    # bot.send_message(cid, "What is your mood today?", )
    bot.send_chat_action(cid, 'typing')  # show the bot "typing" (max. 5 secs)
    time.sleep(1)
    markup = types.ReplyKeyboardMarkup(row_width=3)
    t1 = types.KeyboardButton('To improve my vocabulary')
    t2 = types.KeyboardButton('To improve my grammar skills')
    markup.add(t1, t2)
    bot.send_message(m.from_user.id, 'What is your mood today?', reply_markup=markup)

    # if m.text == 'To improve your vocabulary':
    bot.register_next_step_handler(m, format_ch)

def format_ch(m):
    bot.send_message(m.from_user.id, "Let's start!", reply_markup=hideBoard)
    if m.text == 'To improve my vocabulary':
        command_voc(m)
    else:
        command_gram(m)



SAMPLE_SPREADSHEET_ID3 = '1PYmJdJYaDuONiAoW-koTZtw1pWacDz0ipTAkrCZZ3YI'
SAMPLE_RANGE_NAME3 = 'Voc!F1:T'
def command_voc(m):
    cid = m.chat.id
    bot.send_chat_action(cid, 'typing')  # show the bot "typing" (max. 5 secs)
    time.sleep(1)
    
    creds = None
    
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token3.json'):
        creds = Credentials.from_authorized_user_file('token3.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token3.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID3,
                                range=SAMPLE_RANGE_NAME3).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        # for row in values:
        numVoc = randint(2, 54)
        rowTypes = values[0]
        row = values[numVoc]
        textMovie =  'Topic: ' + rowTypes[0] + '\n' + 'Word: ' + row[0] + '\n' + 'Translation: ' + row[1]
        textMusic =  'Topic: ' + rowTypes[4] + '\n' + 'Word: ' + row[4] + '\n' + 'Transcription: ' + row[5] + '\n' + 'Translation: ' + row[6]
        # textTravel =  'Topic: ' + rowTypes[9] + '\n' + 'Word: ' + row[9] + '\n' + 'Transcription: ' + row[10] + '\n' + 'Translation: ' + row[11]
        textIT =  'Topic: ' + rowTypes[13] + '\n' + 'Word: ' + row[13] + '\n' + 'Translation: ' + row[14]
        bot.send_message(m.from_user.id, textMovie)
        bot.send_message(m.from_user.id, textMusic)
        # bot.send_message(m.from_user.id, textTravel)
        bot.send_message(m.from_user.id, textIT)
            

def command_gram(m):
    cid = m.chat.id
    bot.send_message(cid, "Choose the correct phrasal verb")
    bot.send_chat_action(cid, 'typing')  # show the bot "typing" (max. 5 secs)
    time.sleep(1)
    
    creds = None
    
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        for i in range(3):
            numGram = randint(1, 11)
            row = values[numGram]
            markup = types.InlineKeyboardMarkup([
            [types.InlineKeyboardButton(text=row[1], callback_data=row[1])], 
            [types.InlineKeyboardButton(text=row[2], callback_data=row[2])], 
            [types.InlineKeyboardButton(text=row[3], callback_data=row[3])]])
            bot.send_message(m.from_user.id, row[4], reply_markup=markup)
            time.sleep(5)
            @bot.callback_query_handler(func = lambda call: True)
            def what(call):
                if call.message:    
                    bot.send_message(m.from_user.id, 'Your answer is: ' + call.data)
            time.sleep(3)
            bot.send_message(m.from_user.id, 'The correct answer is: ' + row[6])
            
SAMPLE_SPREADSHEET_ID2 = '136keSvzD-A9yshFq8fpD4ItPgJ6qX5eDXQcy-PepIA0'
SAMPLE_RANGE_NAME2 = 'Rec!A1:E'

@bot.message_handler(commands=['explore'])
def command_rec(m):
    cid = m.chat.id
    bot.send_message(cid, "I have a great recommendation for you:")
    bot.send_chat_action(cid, 'typing')  # show the bot "typing" (max. 5 secs)
    time.sleep(1)
    
    creds = None
    
    if os.path.exists('token2.json'):
        creds = Credentials.from_authorized_user_file('token2.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token2.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID2,
                                range=SAMPLE_RANGE_NAME2).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        numRec = randint(0, 15)
        row = values[numRec]
        text =  'Type: ' + row[0] + '\n' + 'Name: ' + row[2] + '\n' + 'About: ' + '\n' + row[3] + '\n' + 'Link: ' + row[4]
        bot.send_message(m.from_user.id, 'If you are interested in ' + '\n' + row[1])
        bot.send_message(m.from_user.id, text)
        # time.sleep(5)



# filter on a specific message
@bot.message_handler(func=lambda message: message.text == "i love u")
def command_text_hi(m):
    bot.send_message(m.chat.id, "I love you too!")

CLIENT_ACCESS_TOKEN = 'ya29.c.KqYBAQji8q6cfWj5X5H8MT3P9qLbsLqANLlAtk8y1qybMY5eyscGyg6MTX0icerqd3qCU_4AJhbScV9PZ5rFHF5KLbxiMIPOd6BcxdCybBOUIlgQQTsvCOFbu5UCV4mpiqwcbMWC20kgXw7FIRosDWDyfbCcVnEZ2-ja8WnnAF9F37jhy2V1kvC9VbohGJRXoxVe8KXHqDddL5d5KOG72vw6Utlwoqd65Q' # ? api key # If modifying these scopes, delete the file token.json.

#default handler for every other text

import dialogflow
from google.api_core.exceptions import InvalidArgument

@bot.message_handler(func=lambda message: True, content_types=['text'])
def command_default(m):
    DIALOGFLOW_PROJECT_ID = 'small-talk-ed-ilgo'
    DIALOGFLOW_LANGUAGE_CODE = 'en'
    GOOGLE_APPLICATION_CREDENTIALS = 'small-talk-ed.json'
    SESSION_ID = 'current-user-id'
    text_to_be_analyzed = m.text
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(DIALOGFLOW_PROJECT_ID, SESSION_ID)
    text_input = dialogflow.types.TextInput(text=text_to_be_analyzed, language_code=DIALOGFLOW_LANGUAGE_CODE)
    query_input = dialogflow.types.QueryInput(text=text_input)
    try:
        response = session_client.detect_intent(session=session, query_input=query_input)
    except InvalidArgument:
        raise
    bot.send_message(chat_id=m.from_user.id, text=response.query_result.fulfillment_text)
    # print("Query text:", response.query_result.query_text)
    # print("Detected intent:", response.query_result.intent.display_name)
    # print("Detected intent confidence:", response.query_result.intent_detection_confidence)
    # print("Fulfillment text:", response.query_result.fulfillment_text)
    # this is the standard reply to a normal message
    # bot.send_message(m.chat.id, "I don't understand \"" + m.text + "\"\nMaybe try the help page at /help")


bot.polling(none_stop=True, interval=0)