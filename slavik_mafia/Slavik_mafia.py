#! /usr/bin/env python
# -*- coding: utf-8 -*-

from functions_mafia import create_logger, can_be_int, save_vars, load_vars, maf, com, doc, cits, get_game_id, get_name, send_all, mafs_acquaintance
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from time import time
from time import sleep
import telepot
import os.path
import pickle
import random
from threading import Thread
from pprint import pprint

token = '351412799:AAGrKdn6Xx-6tcAkQPQiBK-7_hQA4GEf55E'  # platryatest_bot
TelegramBot = telepot.Bot(token)
send_message = TelegramBot.sendMessage

dumpfilename = 'mafia.pickle'
startmessage = 'started'
helpmessage = 'help'
help_create_message = 'edit players1 mafs2 com3 doc4 cits5 drinker_good6 drinker_bad7 roundtime8 curetime9 mafs_known10 11_mafs_prompt_word 12cured_known'

logger_on_button = create_logger('on_button', 'debug', 'console')
logger_on_chat = create_logger('on_chat', 'debug', 'console')


def null(chat_id, *args):
    if 'dict' in args:
        storage[chat_id] = dict()
    if 'started' in args:
        storage[chat_id]['started'] = False
    if 'delay' in args:
        storage[chat_id]['delay'] = dict()
        storage[chat_id]['delay'][chat_id] = 0

    if 'info' in args:
        storage[chat_id]['info'] = dict()
        storage[chat_id]['info'][chat_id] = None


def name(chat_id, text):
    game_id = get_game_id(chat_id, storage)
    storage[game_id]['info'][chat_id] = text


def mafs_prompt_word():
    import io
    with io.open('mafia_words.txt', 'r', encoding='utf-8') as myfile:
        data = myfile.read()
    data = data.split()
    word = random.sample(data, 1)
    return word[0]


def timer(game_id):  # close thread in end
    logger_on_chat.info('timer started')
    time_start = time()
    time_cure_is_started = False
    cure_elapsed_sent = False
    while 1:
        if (storage[game_id]['can_kill'] is False and storage[game_id]['can_vote'] is False) or time() - time_start > storage[game_id]['roundtime'] * 60:
            logger_on_chat.info('new round must start')
            time_start = time()  # abilities used or time elapsed -> new round and timer
            storage[game_id]['can_kill'] = True
            storage[game_id]['can_check'] = True
            storage[game_id]['can_cure'] = True
            storage[game_id]['can_vote'] = True
            storage[game_id]['cure'] = None
            storage[game_id]['check'] = None
            time_cure_is_started = False
            cure_elapsed_sent = False

            for key, value in storage[game_id]['vote'].items():
                storage[game_id]['vote'][key] = None
            for key, value in storage[game_id]['kill'].items():
                storage[game_id]['kill'][key] = None
            send_all(game_id, 'new round', send_message, storage)
            if storage[game_id]['mafs_prompt']:
                for chat_id in storage[game_id]['mafs']:
                    send_message(chat_id, u' кодовое слово мафов: %s' % mafs_prompt_word())

        if storage[game_id]['cure'] is not None and time_cure_is_started is False:  # is curing but time not started -> start time
            time_cure_start = time()
            time_cure_is_started = True
        elif time_cure_is_started:
            if time() - time_cure_start > storage[game_id]['curetime'] * 60:  # if curing elapsed -> disable
                storage[game_id]['cure'] = None
                storage[game_id]['can_cure'] = False
                if not cure_elapsed_sent:
                    send_message(storage[game_id]['doc'], "cute time elapsed")
                cure_elapsed_sent = True

        sleep(1)
        if storage[game_id]['started'] is False:
            return


def connect(chat_id, text):
    text = text.split()
    if not len(text) == 2:
        send_message(chat_id, u'неверная команда. Пример: connect 123456')
        return
    if not can_be_int(text[1]):
        send_message(chat_id, u'неверная команда: Пример: connect 123456')
        return
    game_id = int(text[1])
    if game_id not in storage:  # delete from ids and storage
        send_message(chat_id, u'неверный номер: игра отсутствует')
        return
    # for key, value in storage.items():  # if player in other game -> delete in ids
    #     if chat_id in value['ids']:
    #         remove_id(chat_id, key, storage, 'full')
    # if chat_id in storage:  # if player owns game -> delete game
    #     del storage[chat_id]
    storage[game_id]['info'][chat_id] = None
    storage[game_id]['delay'][chat_id] = 0
    send_message(chat_id, 'Connected. Now change name')


def create_keyboard(chat_id):
    game_id = get_game_id(chat_id, storage)

    buttons = list()
    buttons.append([InlineKeyboardButton(text='DELAY: ', callback_data='ignore'), InlineKeyboardButton(text='0 sec', callback_data='0sec'),
                    InlineKeyboardButton(text='3 sec', callback_data='3sec'), InlineKeyboardButton(text='6 sec', callback_data='6sec'),
                    InlineKeyboardButton(text='9 sec', callback_data='9sec')])
    buttons.append([InlineKeyboardButton(text='-', callback_data='ignore')])
    buttons.append([InlineKeyboardButton(text='VOTE:', callback_data='ignore')])
    if chat_id in storage[game_id]['alive']:
        for candidate_chat_id, name in storage[game_id]['info'].items():
            if candidate_chat_id in storage[game_id]['alive']:
                buttons.append([InlineKeyboardButton(text=name, callback_data='vote %s' % candidate_chat_id)])

    action = False
    if maf(chat_id, storage):
        action = 'kill'
    elif com(chat_id, storage):
        action = 'check'
    elif doc(chat_id, storage):
        action = 'cure'

    if action:
        buttons.append([InlineKeyboardButton(text='-', callback_data='ignore')])
        buttons.append([InlineKeyboardButton(text='%s:' % action.upper(), callback_data='ignore')])
        for candidate_chat_id, name in storage[game_id]['info'].items():
            if candidate_chat_id in storage[game_id]['alive']:
                buttons.append([InlineKeyboardButton(text=name, callback_data='%s %s' % (action, candidate_chat_id))])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def edit_keyboards(game_id):
    for chat_id in storage[game_id]['alive']:
        TelegramBot.editMessageReplyMarkup((chat_id, storage[game_id]['keyboard_ids'][chat_id]), reply_markup=create_keyboard(chat_id))


def create_game(chat_id, game_id):
    if game_id is None:
        game_id = chat_id
        null(chat_id, 'dict', 'started', 'delay', 'info')

    storage[game_id]['started'] = False

    buttons = list()
    buttons.append([InlineKeyboardButton(text='Mafs: ', callback_data='ignore'), InlineKeyboardButton(text='1', callback_data='maf 1'), InlineKeyboardButton(text='2', callback_data='maf 2'), InlineKeyboardButton(text='3', callback_data='maf 3')])
    buttons.append([InlineKeyboardButton(text='Com: ', callback_data='ignore'), InlineKeyboardButton(text='0', callback_data='com 0'), InlineKeyboardButton(text='1', callback_data='com 1')])
    buttons.append([InlineKeyboardButton(text='Doc: ', callback_data='ignore'), InlineKeyboardButton(text='0', callback_data='doc 0'), InlineKeyboardButton(text='1', callback_data='doc 1')])
    buttons.append([InlineKeyboardButton(text='Cits: ', callback_data='ignore'), InlineKeyboardButton(text='0', callback_data='cits 0'), InlineKeyboardButton(text='1', callback_data='cits 1'), InlineKeyboardButton(text='2', callback_data='cits 2'), InlineKeyboardButton(text='3', callback_data='cits 3')])
    buttons.append([InlineKeyboardButton(text='Roundtime: ', callback_data='ignore'), InlineKeyboardButton(text='0.5', callback_data='roundtime 0.5'),
                    InlineKeyboardButton(text='1', callback_data='roundtime 1'), InlineKeyboardButton(text='1.5', callback_data='roundtime 1.5'),
                    InlineKeyboardButton(text='2', callback_data='roundtime 2'), InlineKeyboardButton(text='2.5', callback_data='roundtime 2.5'),
                    InlineKeyboardButton(text='3', callback_data='roundtime 3')])
    buttons.append([InlineKeyboardButton(text='Curetime: ', callback_data='ignore'), InlineKeyboardButton(text='0.5', callback_data='curetime 0.5'),
                    InlineKeyboardButton(text='1', callback_data='curetime 1'), InlineKeyboardButton(text='1.5', callback_data='curetime 1.5'),
                    InlineKeyboardButton(text='2', callback_data='curetime 2'), InlineKeyboardButton(text='2.5', callback_data='curetime 2.5'),
                    InlineKeyboardButton(text='3', callback_data='curetime 3')])
    buttons.append([InlineKeyboardButton(text='Mafs_known: ', callback_data='ignore'), InlineKeyboardButton(text='False', callback_data='mafs_known false'), InlineKeyboardButton(text='True', callback_data='mafs_known true')])
    buttons.append([InlineKeyboardButton(text='Mafs_prompt: ', callback_data='ignore'), InlineKeyboardButton(text='False', callback_data='mafs_prompt false'), InlineKeyboardButton(text='True', callback_data='mafs_prompt true ')])
    buttons.append([InlineKeyboardButton(text='Cured_known: ', callback_data='ignore'), InlineKeyboardButton(text='False', callback_data='cured_known false'), InlineKeyboardButton(text='True', callback_data='cured_known true')])

    send_message(chat_id, 'Set up the game, your game_id is %s' % game_id, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


def startgame(chat_id):
    game_id = get_game_id(chat_id, storage)
    if game_id is None:
        send_message(chat_id, 'create game first')  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        return
    logger_on_chat.info('setting roles')
    if not set_roles(chat_id):
        return

    storage[game_id]['can_kill'] = True
    storage[game_id]['can_check'] = True
    storage[game_id]['check'] = None
    storage[game_id]['can_cure'] = True
    storage[game_id]['cure'] = None
    storage[game_id]['can_vote'] = True
    storage[game_id]['started'] = True

    send_starts(game_id)

    thread_time = Thread(target=timer, args=(game_id,))
    thread_time.start()


def set_roles(chat_id):
    game_id = get_game_id(chat_id, storage)
    mafs_count = storage[game_id]['mafs_count']
    com_count = storage[game_id]['com_count']
    doc_count = storage[game_id]['doc_count']
    cits_count = storage[game_id]['cits_count']
    if mafs_count + com_count + doc_count + cits_count != len(storage[game_id]['info']):
        send_message(chat_id, "len(info') != roles_count")
        return False

    storage[game_id]['mafs'] = list()
    storage[game_id]['cits'] = list()
    storage[game_id]['goods'] = list()
    storage[game_id]['mafs'] = random.sample(set(storage[game_id]['info'].keys()), mafs_count)
    storage[game_id]['com'] = random.sample(set(storage[game_id]['info'].keys()) - set(storage[game_id]['mafs']), com_count)
    storage[game_id]['doc'] = random.sample(set(storage[game_id]['info'].keys()) - set(storage[game_id]['mafs']) - set(storage[game_id]['com']), doc_count)

    storage[game_id]['cits'] = list(set(storage[game_id]['info'].keys()) - set(storage[game_id]['mafs']) - set(storage[game_id]['com']) - set(storage[game_id]['doc']))
    storage[game_id]['goods'] = list(set(storage[game_id]['info'].keys()) - set(storage[game_id]['mafs']))

    if storage[game_id]['com'] == []:
        storage[game_id]['com'] = None

    else:
        storage[game_id]['com'] = storage[game_id]['com'][0]

    if storage[game_id]['doc'] == []:
        storage[game_id]['doc'] = None
    else:
        storage[game_id]['doc'] = storage[game_id]['doc'][0]

    storage[game_id]['alive'] = list()
    for chat_id in storage[game_id]['info']:
        storage[game_id]['alive'].append(chat_id)
    return True


def send_starts(chat_id):
    game_id = get_game_id(chat_id, storage)
    storage[game_id]['kill'] = dict()
    storage[game_id]['keyboard_ids'] = dict()
    storage[game_id]['vote'] = dict()

    for chat_id in storage[game_id]['info']:
        if maf(chat_id, storage):
            role = 'maf'
        if com(chat_id, storage):
            role = 'com'
        if doc(chat_id, storage):
            role = 'doc'
        if cits(chat_id, storage):
            role = 'citizen'

        sent_data = send_message(chat_id, u'игроков %s, мафов %s, комиссар %s, доктор %s, горожане %s, продолжительность раунда %s, продолжительность лечения доктора %s, мафы знакомы %s, словесная подсказка мафам %s, инфа об успешном лечении %s.\n\nВаша роль: %s' % (len(storage[game_id]['info']), storage[game_id]['mafs_count'], storage[game_id]['com_count'], storage[game_id]['doc_count'], storage[game_id]['cits_count'], storage[game_id]['roundtime'], storage[game_id]['curetime'], storage[game_id]['mafs_known'], storage[game_id]['mafs_prompt'], storage[game_id]['cured_known'], role.upper()), reply_markup=create_keyboard(chat_id))
        # sent_data = send_message(chat_id, 'aaa', reply_markup=create_keyboard(chat_id))

        storage[game_id]['keyboard_ids'][chat_id] = sent_data['message_id']

    if storage[game_id]['mafs_known']:
        mafs_acquaintance(game_id, send_message, storage)  # znakomstvo mafov


def parse_query(chat_id, query_data):
    if query_data == 'ignore':
        return
    game_id = get_game_id(chat_id, storage)

    if query_data[-3:] == 'sec':
        storage[game_id]['delay'][chat_id] = int(query_data[0])

    else:
        sleep(storage[game_id]['delay'][chat_id])
        query_data = query_data.split()
        logger_on_button.debug('query data = %s' % query_data)
        key = query_data[0]
        value = query_data[1]
        if value == 'true':
            value = True
        elif value == 'false':
            value = False

        if key == 'maf':
            storage[game_id]['mafs_count'] = int(value)
        elif key == 'com':
            storage[game_id]['com_count'] = int(value)
        elif key == 'doc':
            storage[game_id]['doc_count'] = int(value)
        elif key == 'cits':
            storage[game_id]['cits_count'] = int(value)
        elif key == 'roundtime':
            storage[game_id]['roundtime'] = float(value)
        elif key == 'curetime':
            storage[game_id]['curetime'] = float(value)
        elif key == 'mafs_known':
            storage[game_id]['mafs_known'] = value
        elif key == 'mafs_prompt':
            storage[game_id]['mafs_prompt'] = value
        elif key == 'cured_known':
            storage[game_id]['cured_known'] = value

        if 'alive' not in storage[game_id]:
            return

        if chat_id not in storage[game_id]['alive'] or not storage[game_id]['started']:
            return

        if key == 'vote' and storage[game_id]['can_vote']:
            storage[game_id]['vote'][chat_id] = int(value)
            send_message(chat_id, 'OK, voting %s' % get_name(game_id, int(value), storage))

        elif key == 'kill' and storage[game_id]['can_kill']:
            storage[game_id]['kill'][chat_id] = int(value)
            send_message(chat_id, 'OK, trying to kill %s' % get_name(game_id, int(value), storage))

        elif key == 'check' and storage[game_id]['can_check']:
            storage[game_id]['check'] = int(value)

        elif key == 'cure' and storage[game_id]['can_cure']:
            storage[game_id]['cure'] = int(value)
            send_message(chat_id, 'OK, curing %s' % get_name(game_id, int(value), storage))

        elif key == 'check' and not storage[game_id]['can_vote']:
            send_message(chat_id, "u can't vote")

        elif key == 'check' and not storage[game_id]['can_kill']:
            send_message(chat_id, "u can't kill")

        elif key == 'check' and not storage[game_id]['can_check']:
            send_message(chat_id, "u can't check")

        elif key == 'check' and not storage[game_id]['can_cure']:
            send_message(chat_id, "u can't cure")

    reply(chat_id)


def check_mafs_murder(game_id):
    # if len(storage[game_id]['kill']) == 0:
    #     return
    target = list(set(storage[game_id]['kill'].values()))
    if len(target) != 1 or len(storage[game_id]['kill'].values()) != len(storage[game_id]['mafs']):
        return False
    target = list(set(storage[game_id]['kill'].values()))[0]

    if target != storage[game_id]['cure']:
        kill_chat_id(target, game_id)
        send_all(game_id, '%s killed' % get_name(game_id, target, storage), send_message, storage)
        storage[game_id]['can_kill'] = False
        return True
    else:
        if storage[game_id]['cured_known']:
            send_all(game_id, 'cured', send_message, storage)
        storage[game_id]['can_cure'] = False
    storage[game_id]['can_kill'] = False
    storage[game_id]['kill'] = dict()
    return False


def comissaire_check(game_id):
    if storage[game_id]['check'] is not None:
        if maf(storage[game_id]['check'], storage):
            send_message(storage[game_id]['com'], 'maf')
        else:
            send_message(storage[game_id]['com'], 'not maf')
        storage[game_id]['can_check'] = False
        storage[game_id]['check'] = None


def check_votes(game_id):  # голосование сохранено в словаре {123456: 789456, 789456: 123456}  # (кто: против кого)
    from collections import Counter
    import math
    votes = Counter(storage[game_id]['vote'].values()).most_common()  # получается что-то типа [(123456, 2), (789456, 1)], где первым элементом наиболее частый ключ и число совпадений
    logger_on_button.debug('votes = %s' % votes)
    if len(votes) > 0:  # если вообще есть голосования
        if votes[0][0] is not None:
            if votes[0][1] >= math.ceil(len(storage[game_id]['alive']) / 2.0):  # если одинаковых голосов больше чем половина живых округлённая вверх для нечётного числа:
                storage[game_id]['can_vote'] = False  # голосовать больше нельзя
                print 'votes = ', votes
                print 'votes 00', votes[0][0]
                kill_chat_id(votes[0][0], game_id)  # удалить chat_id отовсюду
                send_all(game_id, '%s voted' % get_name(game_id, votes[0][0], storage), send_message, storage)  # сообщение всем об убийстве голосованием
                return True
    return False


def kill_chat_id(chat_id, game_id):
    if maf(chat_id, storage):
        storage[game_id]['mafs'].remove(chat_id)
    elif com(chat_id, storage):
        storage[game_id]['com'] = None
        storage[game_id]['com_check'] = None
    elif doc(chat_id, storage):
        storage[game_id]['doc'] = None
        storage[game_id]['doc_cure'] = None
    for key, value in storage[game_id]['kill'].items():
        if value == chat_id:
            storage[game_id]['kill'][key] = None
    if chat_id in storage[game_id]['alive']:
        storage[game_id]['alive'].remove(chat_id)
    if chat_id in storage[game_id]['goods']:
        storage[game_id]['goods'].remove(chat_id)


def check_alive(game_id):
    if len(storage[game_id]['mafs']) == 0:
        send_all(game_id, 'goods_wins!', send_message, storage)
        storage[game_id]['started'] = False
    elif len(storage[game_id]['goods']) == 0:
        send_all(game_id, 'evil_wins!', send_message, storage)
        storage[game_id]['started'] = False


def reply(chat_id):
    game_id = get_game_id(chat_id, storage)
    save_vars(dumpfilename, storage)
    if 'alive' not in storage[game_id]:
        return
    if chat_id not in storage[game_id]['alive']:
        return
    logger_on_button.info('Killed?')
    if check_mafs_murder(game_id):
        logger_on_button.info('Yes, edit keyboards')
        edit_keyboards(game_id)
    logger_on_button.info('No')

    comissaire_check(game_id)

    logger_on_button.info('Killed in vote?')
    if check_votes(game_id):
        logger_on_button.info('Yes, edit keyboards')
        try:
            edit_keyboards(game_id)
        except:
            pass
    logger_on_button.info('No')

    logger_on_button.info('Checking alive')
    check_alive(game_id)
    logger_on_button.info('OK')


def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    chat_id = msg['message']['chat']['id']
    # if chat_id not in storage:
    #     null(chat_id, 'dict', 'started', 'delay', 'info')
    game_id = get_game_id(chat_id, storage)
    logger_on_button.info('button pressed, query data = %s' % query_data)
    thread_parse = Thread(target=parse_query, args=(chat_id, query_data,))
    thread_parse.start()


def on_chat_message(msg):
    save_vars(dumpfilename, storage)
    content_type, chat_type, chat_id = telepot.glance(msg)
    game_id = get_game_id(chat_id, storage)

    # if chat_id not in storage:
    #     null(chat_id, 'dict', 'started', 'delay', 'info')
    save_vars(dumpfilename, storage)
    if not content_type == 'text':
        return
    text = msg['text'].lower()
    logger_on_chat.info('message recieved, text = %s' % text)

    if text == '/start':
        send_message(chat_id, startmessage)

    elif text == '/help':
        send_message(chat_id, helpmessage)

    elif text == 'helpcreate' or text == '/helpcreate':
        send_message(chat_id, help_create_message)

    elif text[:6] == 'create' or text[:7] == '/create':
        create_game(chat_id, game_id)
        return

    elif text[:7] == 'connect' or text[:8] == '/connect':
        connect(chat_id, text)
        return

    elif text[:4] == 'kick' or text[:5] == '/kick' and chat_id in storage and game_id is not None:
        text = text.split()
        del storage[game_id]['info'][int(text[1])]
        return

    # elif text[:4] == 'name' or text[:5] == '/name':
    #     changename(text, game_id, chat_id, storage)

    elif text[:4] == 'name':
        logger_on_chat.info('Name command passed')
        if game_id is not None:
            storage[game_id]['info'][chat_id] = text.split()[1]
        return

    elif text == 'go' or text == '/go':
        logger_on_chat.info('startgame launched')
        startgame(chat_id)
        return

    elif text == 'end' or text == '/end' and chat_id in storage:
        storage[game_id]['started'] = False

    # elif text == 'st':
    #     print_storage(game_id, storage)

    elif text == 'st':
        pprint(storage)
        return

    elif text == 'sto':
        send_message(chat_id, str(storage))
        return

    if game_id is None:
        send_message(chat_id, u'нет активной игры. создайте свою или присоединитесь к чужой')
        return

    if not storage[game_id]['started']:
        send_message(chat_id, u'игра создана, но не начата')
        return

    logger_on_chat.info('Creating keyboard')
    send_message(chat_id, '.', reply_markup=create_keyboard(chat_id))

    with open(dumpfilename, 'w') as dumpfile:
        pickle.dump(storage, dumpfile)

if os.path.isfile(dumpfilename):
    storage = load_vars(dumpfilename)
    print 'dump loaded'
else:
    storage = dict()
TelegramBot.message_loop({'chat': on_chat_message, 'callback_query': on_callback_query})  # receive bot messages

print ('Listening ...')

while 1:  # Keep the program running.
    sleep(10)

# kick
# disconnect ability - кик себя
# нельзя менять имена после начала
# проверять не занято ли имя ???
# defaults for roles
