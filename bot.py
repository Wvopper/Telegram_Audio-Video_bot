# default imports
import os

# downloaded imports
from telebot import TeleBot
from telebot import types as ttp
from pytube import YouTube
from moviepy.editor import *
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())
# bot init
bot = TeleBot(token=os.getenv('TOKEN'))


# main menu
@bot.message_handler(commands=['start'])
def send_welcome(message):
    messange = """Привет!\nЭтот бот позволяет вырезать из видео звук.
    Вы отправляете сслыку на видео из <b>YouTube</b>, вам отправляете файл вида <b>mp3</b>"""
    bot.send_message(message.chat.id, messange, parse_mode='html')
    # keyboard 1
    markup = ttp.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button1 = ttp.KeyboardButton(text='/new_audio')
    markup.add(button1)
    # rules
    rules = '<b>Правила:</b>\n' \
            '1) Не отправлять видео длительностью более 7 минут. Бот вам не даст их отправить\n' \
            '2) Не спамьте в бота сообщениями и ссылками\n' \
            '3) Используйте бота в благих намерениях\n' \
            'Чтобы начать работу с ботом нажмите /new_audio\n' \
            '\n<b>УБЕДИТЕСЬ ЧТО ССЫЛКА НАЧИНАЕТСЯ С https://www.youtube.com/watch</b>'
    bot.send_message(message.chat.id, rules, parse_mode='html', reply_markup=markup)


# intermediate function
@bot.message_handler(commands=['new_audio'])
def get_url(message):
    # getting url of the video
    sent = bot.send_message(message.chat.id, 'Введите ссылку на видео: ')
    bot.register_next_step_handler(sent, downloader)


def downloader(message):
    # keyboard 2
    keyboard_return = ttp.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_to_start = ttp.KeyboardButton(text='/start')
    keyboard_return.add(button_to_start)
    # checking url validity
    # if 'youtu' in message.text:
    print(message.text)
    bot.send_message(message.chat.id, """Отично! Загрузка видео может занять какое-то время.
    Пока можете пересмотреть игру престолов""")
    url = message.text
    flag = 'sending'
    error_amount = 0
    # while True loop to avoid errors and exceptions from pytube
    while flag == 'sending':
        try:
            video = YouTube(url)
            mp4 = video.streams.filter(only_audio=True, file_extension='mp4').first()

            # downloading video from YouTube
            mp4.download('stack', f"{video.title}.mp4")
            mp4_file_path = fr"C:\Users\1234x\PycharmProjects\Telegram_Audio-Video_bot\stack\{video.title}.mp4"

            # extracting audiofile from video
            audioclip = AudioFileClip(mp4_file_path)
            audioclip.write_audiofile(f"{video.title}_audio.mp3")
            os.replace(f"{video.title}_audio.mp3", f"stack/{video.title}_audio.mp3")

            os.remove(mp4_file_path)

            # sending file to user
            with open(f"stack/{video.title}_audio.mp3", 'rb') as file_to_send:
                bot.send_audio(message.chat.id, file_to_send)

            os.remove(f"stack/{video.title}_audio.mp3")
            flag = 'success'

        except KeyError: # possible exception from pytube
            print(f'still again {error_amount}')
            error_amount += 1
            if error_amount >= 21:
                flag = 'error'

        # reaction if flag is success
        if flag == 'success':
            sent = bot.send_message(message.chat.id, """А вот и ваше аудио! Нажав на /start вы сможете вернуться в главное меню""", reply_markup=keyboard_return)
            bot.register_next_step_handler(sent, send_welcome)

        # reaction to many exceptions
        if flag == 'error':
            sent = bot.send_message(message.chat.id, """С большой долей вероятности вы ввели не ту ссылку.
                                                 Вернитесь в меню (/start), перечитайте правила, попробуйте снова""")
            bot.register_next_step_handler(sent, send_welcome)

    # reaction if url is invalid
    if flag == 'sending':
        sent = bot.send_message(message.chat.id, 'Something went wrong. Please, tap /start to reload the bot', reply_markup=keyboard_return)
        bot.register_next_step_handler(sent, send_welcome)


if __name__ == '__main__':
    bot.polling(none_stop=True)
