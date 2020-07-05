import telebot
import re
import markovify
from pymorphy2 import MorphAnalyzer
import os

morph = MorphAnalyzer()

if 'CONFIG_IN_ENVIRON' in os.environ:
#     PROXY = {'https': os.environ.get('PROXY')}
    TOKEN = os.environ.get('TOKEN')
else:
    import config
#     PROXY = config.PROXY
    TOKEN = config.TOKEN

# telebot.apihelper.proxy = PROXY
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id,
                     "Привет, самурай,\nлюбитель хокку юный.\nГотов сочинять.")

@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(message.chat.id,
                     "Введите команду /hokku, чтобы получить случайное хокку.\nВведите /hokku <ваше слово>, чтобы получить хокку с вашим словом." +
                     "\nПожалуйста, вводите только существительные!")

def get_text(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
    return text


def get_vowel_num(line):
    num = 0
    vowels = {'а', 'о', 'ы', 'я', 'ё', 'и', 'у', 'ю', 'е'}
    for v in vowels:
        vows = re.findall(v, line)
        num += len(vows)
    return num


def make_line(m, num):
    f = 0
    while f != 1:
        sent = m.make_short_sentence(30)
        if sent != None:
            vowel_num = get_vowel_num(sent)
            if vowel_num == num:
                f = 1
    return sent


def change_given(word, given):
    given_res = morph.parse(given)
    word_res = morph.parse(word)
    if word_res[0].tag.number is not None:
        given_res = given_res[0].inflect({word_res[0].tag.number})
    if word_res[0].tag.case is not None:
        given_res = given_res.inflect({word_res[0].tag.case})
    return given_res.word


def check_POS(word, given):
    result_given = morph.parse(given)
    given_pos = str(result_given[0].tag).split(',')[0]
    result_word = morph.parse(word)
    word_pos = str(result_word[0].tag).split(',')[0]
    if given_pos == word_pos:
        return True
    return False


def line_with_word(m, given, num):
    given_num = get_vowel_num(given)
    k = 0
    while k != 1:
        f = 0
        while f != 1:
            sent = m.make_short_sentence(30)
            if sent is not None:
                vowel_num = get_vowel_num(sent)
                if vowel_num == num:
                    f = 1
        words = sent.split()
        for word in words:
            word_num = get_vowel_num(word)
            if word_num == given_num and check_POS(word, given):
                new_given = change_given(word, given)
                new_sent = sent.replace(word, new_given)
                print(sent)
                return new_sent


def make_hokku():
    text = get_text('big_hokku_texts.txt')
    m = markovify.Text(text, state_size=2)
    first = make_line(m, 5)
    second = make_line(m, 7)
    f = 0
    while f != 1:
        third = make_line(m, 5)
        if third != first:
            f = 1
    return first.capitalize() + '\n' + second.capitalize() + '\n' + third.capitalize()


def make_hokku_with_word(word, vowel_num):
    text = get_text('big_hokku_texts.txt')
    m = markovify.Text(text, state_size=2)
    first = make_line(m, 5)
    if vowel_num == 7:
        second = word
    else:
        second = line_with_word(m, word, 7)
    f = 0
    while f != 1:
        third = make_line(m, 5)
        if third != first:
            f = 1
    return first.capitalize() + '\n' + second.capitalize() + '\n' + third.capitalize()


@bot.message_handler(regexp=r'/hokku (.+)')
def send_welcome(message):
    word = message.text.replace('/hokku ', '')
    res = morph.parse(word)
    if res[0].tag.POS != 'NOUN':
        bot.send_message(message.chat.id,
                         'Это не существительное :(')
        return 'ok'
    vowel_num = get_vowel_num(word)
    if vowel_num > 7:
        bot.send_message(message.chat.id,
                         'Это слишком большое слово :(')
        return 'ok'
    hokku = make_hokku_with_word(word, vowel_num)
    bot.send_message(message.chat.id,
                     hokku)


@bot.message_handler(commands=['hokku'])
def send_welcome(message):
    hokku = make_hokku()
    bot.send_message(message.chat.id,
                     hokku)

if __name__ == '__main__':
    bot.polling(none_stop=True)
