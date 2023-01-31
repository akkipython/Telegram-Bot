import telebot
import itertools
import json
import random
import time
import threading
from dotenv import load_dotenv
import os
from telebot import *
from telegram import *
from telegram.ext import *

load_dotenv()
token = os.environ.get("BOT_TOKEN")
botCMD = os.environ.get("BOT_CMD")


data = {}
wordList = []
# Open the Dictionary 
with open("dictionary.json") as f:
    data = json.load(f)
    wordList = list(data.keys())
short_keys = [key for key in data if len(key) < 9 and len(key) > 5]

# Generate the Random Word From Dictionary
def generate_words(letters):
    permutations = []
    for i in range(3, len(letters) + 1):
        for p in itertools.permutations(letters, i):
            permutations.append(''.join(p))
    valid_words = []
    for perm in permutations:
        word = ''.join(perm)
        if word in data and data[word]:
            valid_words.append(word)
    return valid_words


bot = telebot.TeleBot(token)

# For 1 Minute Timer
def timer_function(chat_id):
    # Sleep for 1 minutes
    time.sleep(60)

# Call back function (Button Handler)
@bot.callback_query_handler(func=lambda call: call.data == "yes")
def handle_yes(callback):
    instructions(callback.message)

@bot.callback_query_handler(func=lambda call: call.data == "yes_I_want")
def handle_yes(callback):
    game(callback.message)


@bot.callback_query_handler(func=lambda call: call.data == "no_I_Do_not_want")
def handle_yes(callback):
    stop_stop(callback.message)

@bot.callback_query_handler(func=lambda call: call.data == "no")
def handle_yes(callback):
    stop_stop(callback.message)

@bot.callback_query_handler(func=lambda call: call.data == "start_game")
def handle_yes(callback):
    game(callback.message)

# For Multiplayer But currently it is not working
# @bot.callback_query_handler(func=lambda call: call.data == "multiplayer")
# def multiplayer(callback):
#     print(callback)
#     chat_id = callback.from_user.id
#     # Redirect the user to the game bot
#     bot.send_message(chat_id=chat_id,text='Redirecting you to the game bot...',)
#     bot.forward_message(chat_id=chat_id,from_chat_id=callback.from_user.id,message_id=callback.message.message_id,)
#     keyboard = [[InlineKeyboardButton("Multiplayer", callback_data='multiplayer')]]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     bot.send_message(chat_id=callback.message.chat_id,text='Click the button to start the multiplayer game',reply_markup=reply_markup,)

# Handle the Hello , Start and hi command
@bot.message_handler(commands=['start', 'hello','hi'])
def send_welcome(message):
    print(message.from_user.first_name)
    bot.send_message(message.chat.id, "Hello! "+message.from_user.first_name +
                 "🤗\nThis message is from intro bot created by Dhwani 🤖")

    markup_inline = types.InlineKeyboardMarkup()
    yes = types.InlineKeyboardButton(text="yes",callback_data="yes")
    no = types.InlineKeyboardButton(text="no",callback_data="no")
    multiplayer= types.InlineKeyboardButton(text="multiplayer",callback_data="multiplayer")
    markup_inline.add(yes,no,multiplayer)
    bot.send_message(message.chat.id,"Do you want to play the game",reply_markup=markup_inline)


# Time is up 
def after_time_up(message):
    bot.send_message(
        message.chat.id, "If you want to play Scramble Word Game🃏\nClick on /"+botCMD)

# Handle the user dont want to play game
def stop_stop(message):
    bot.send_message(message.chat.id,"Thankyou for using the bot\nBye:👋\nWe meet Again")
# Handle the user dont want to play game
def stop(message):
    bot.send_message(message.chat.id,"Thankyou for using the bot\n"+message.from_user.first_name)
    markup_inline = types.InlineKeyboardMarkup()
    yes = types.InlineKeyboardButton(text="yes_I_want",callback_data="yes_I_want")
    no = types.InlineKeyboardButton(text="no_I_Do_not_want",callback_data="no_I_Do_not_want")
    multiplayer= types.InlineKeyboardButton(text="multiplayer",callback_data="multiplayer")
    markup_inline.add(yes,no,multiplayer)
    bot.send_message(message.chat.id,"Do you want to play the game by button",reply_markup=markup_inline)

#Handle User Attempts 
def user_attempt(message, words, attempts,thread,check_duplicate): 
    if thread.is_alive():
        if len(message.text) >2:
            text = message.text
            text = text.lower()
            print(text)
            if message.text == "/hello" or message.text == "/start":
                send_welcome(message)
            elif message.text == "/gamestart":
                game(message)
            elif message.text == "/stop" or message.text =="/stop@Game_assi_bot":
                stop(message)
            else :
                
                if text in check_duplicate:
                    bot.reply_to(message,"You enter duplicate word \nTry again!")
                    bot.register_next_step_handler(message,user_attempt,words,attempts,thread,check_duplicate)
                    return 
                
                check_duplicate.add(text)
                attempts.append(text)
                counter = len(attempts)
                text = text.lower()

                if text in words:
                    bot.reply_to(message, "Your answer is correct 😊👍")
                    # bot.send_message(
                    #     message.chat.id, "You have only "+str(5-counter)+" attempts left \n Next Attempt!")
                    # bot.register_next_step_handler(
                    #     message, user_attempt, words, attempts)
                else:
                    bot.reply_to(message, "Your answer is incorrect 😔👎")
                    
                if counter == 5:
                    print(attempts)
                    common_words1 = set(attempts).intersection(words)
                    bot.send_message(message.chat.id, "You have no more attempt left!\n" + ("\n".join(attempts))+"\nYour Score:"+str(len(common_words1))+" out of 5\n\nYou want to replay")
                    markup_inline=types.InlineKeyboardMarkup()
                    yes = types.InlineKeyboardButton(text="yes_I_want",callback_data="yes_I_want")
                    no = types.InlineKeyboardButton(text="no_I_Do_not_want",callback_data="no_I_Do_not_want")
                    multiplayer= types.InlineKeyboardButton(text="multiplayer",callback_data="multiplayer")
                    markup_inline.add(yes,no,multiplayer)
                    bot.send_message(message.chat.id,"Do you want to play the game by button",reply_markup=markup_inline)
                else:
                    bot.send_message(
                        message.chat.id, "You have only "+str(5-counter)+" attempts left \n Next Attempt!")
                    bot.register_next_step_handler(
                        message, user_attempt, words, attempts,thread,check_duplicate)
        else:
            bot.send_message(message.chat.id, "You enter 2 Alphabet Word\nPlease enter minimum 3 Aplhabet words")  
            bot.register_next_step_handler(message,user_attempt,words,attempts,thread,check_duplicate)
            return 
    else:
        bot.send_message(message.chat.id, "⏰ Timer is up, command ended.\nYour score is not Generated Because you have reached the time limit.\nIf you want to play again click on /"+str(botCMD))

#Game Instruction
instruction = "Please follow the Instructions\n1.A set of letters is given to the player. This set of letters can be chosen randomly, or it can be a specific word that has been scrambled.\n2.User has to use minimum 3 Alphabhet to make a word\n3.The player must use the given letters to form only five words as possible.\n4.When you finished your attempts you get your Score \n5.To Stop the Gameat current moment use /stop \n\nNOTE: You have only 1 min "

# Handle the Game start
@bot.message_handler(commands=['gamestart'])
def instructions(message):    
    # bot.send_message(message.chat.id, "Welcome to the Game\nInstructions:\n" +
    #                     instructions)
    markup_inline=types.InlineKeyboardMarkup()
    start_game= types.InlineKeyboardButton(text="start_game",callback_data="start_game")
    markup_inline.add(start_game)
    bot.send_message(message.chat.id,"Welcome to the Game\nInstructions:\n" +instruction,reply_markup=markup_inline)
def game(message):
    
    thread = threading.Thread(target=timer_function, args=(message.chat.id,))
    thread.start()
    if thread.is_alive():
        random_word = random.choice(short_keys)
        scrambled_word_for_words = ''.join(
            random.sample(random_word, len(random_word)))
        scrambled_word = scrambled_word_for_words.upper()
        scrambled_word = "-".join(scrambled_word)
        print(message.chat.first_name,
            "[", random_word, "]", "::", scrambled_word)

        words = generate_words(scrambled_word_for_words)
        # print(words)
        # bot.reply_to(message, "Hello "+message.from_user.first_name)
        
        # bot.send_message(message.chat.id, "Welcome to the Game\nInstructions:\n" +
        #                 instructions+"\n\nHere is your word\n"+scrambled_word)
        bot.send_message(message.chat.id, "Here is your word\n"+scrambled_word)
        bot.send_message(message.chat.id, "You have only 5 attempts \n\nYour Time Start Now! ⏰ ")
        
        check_duplicate = set()
        bot.register_next_step_handler(message, user_attempt, words, [],thread,check_duplicate)
    else:
        bot.send_message(message.chat.id, " ⏰ Timer is up, command ended.\nYour score is not Generated Because you have reached the time limit.\nIf you want to play again click on /"+str(botCMD))



# Handle all other message send by user if that input is not a command
@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, "Hi Please click on /hello")


bot.infinity_polling()

