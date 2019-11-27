# Importa l'API de Telegram, i funcions per l'us del bot.
import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler

import numpy as np
import matplotlib.pyplot as plt

# Importa l'API pel tractament d'arxius bytes, com ara imatges.
from PIL import Image
import requests
from io import BytesIO

# Importa el modul per el seguiment de la sessio del bot.
import logging

# Configurem el seguiment de la sessio del bot.
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

# Contrasenya per debloquejar el misteri.
password = 'APARCAMENT'

# Foto amb el problema de l'aparcament.
Riddle_URL = 'https://i.stack.imgur.com/CT56W.jpg'
response = requests.get(Riddle_URL)
imatge = Image.open(BytesIO(response.content))


# Primera funcio, serveix per activar el bot. Envia un breu missatge de benvinguda.
def start(bot, update, user_data):
    try:
        message = "Si vols parlar amb mi, posa /speak abans del teu missatge."
        bot.send_message(chat_id=update.message.chat_id, text=message)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=update.message.chat_id, text='💣')


def distance_word(word1, word2):
    sum = 0.0
    for i in range(min(len(word1), len(word2))):
        sum += float((ord(word1[i]) - ord(word2[i])))**2
    return sum


def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.2989, 0.5870, 0.1140])

# Funció per distorsionar la imatge.
def distort(img, grau):
    # Convertir la imatge en una matriu per poder distorsionar-la.
    m = np.asarray(img)
    img2d = rgb2gray(m)
    m = np.asarray(img2d)

    m2 = np.zeros((img2d.shape[0], img2d.shape[1]), dtype=np.uint8)
    width = img2d.shape[0]
    height = img2d.shape[1]

    A = m.shape[0] / 3.0
    w = 1.0 / m.shape[1]

    # Funció lambda per fer un shift dels píxels.
    shift = lambda x: A * np.sin(2.0*np.pi*x * w)

    for i in range(m.shape[0]):
        m2[:,i] = np.roll(m[:,i], int(shift(i)))

    img2 = Image.fromarray(np.uint8(m2))
    return img2


# Funció per enviar la foto segons si s'ha encertat el codi o no.
def send_photo(bot, update, word, correct=False, distance = 0):
    try:
        if not correct:
            imatge_enviada = distort(imatge, distance)
            # Creem un objecte de tipus "BytesIO" per guardar la imatge del graf.
            bio = BytesIO()
            # Creem i guardem la imatge amb una funcio externa per seguidament enviar-la.
            imatge_enviada.save(bio, 'PNG')
            bio.seek(0)
            bot.send_photo(chat_id=update.message.chat_id, photo=imatge_enviada)
        else:
            bio = BytesIO()
            # Creem i guardem la imatge amb una funcio externa per seguidament enviar-la.
            imatge.save(bio, 'PNG')
            bio.seek(0)
            bot.send_photo(chat_id=update.message.chat_id, photo=bio)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=update.message.chat_id, text='💣')


# Funció per parlar amb el bot i enviar missatges.
def speak(bot, update, user_data):
    try:
        miss_rebut = update.message.text[7:] # esborra el "/speak " del començament del missatge.
        if miss_rebut.upper() == password:
            send_photo(bot, update, miss_rebut, True, 0)
        else:
            distance = distance_word(password.upper(), miss_rebut.upper())
            send_photo(bot, update, miss_rebut, False, distance)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=update.message.chat_id, text='💣')


# Funcio que es crida quan es produeixen errors de sessio, enviant un avis.
def error(update, bot):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


###########################################################################################


# Codi d'entrada que guardem en una variable per poder accedir al bot.
TOKEN = open('token.txt').read().strip()

# Crea els objectes per treballar amb Telegram.
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher

# Indica que quan el bot rep una ordre donada s'executi la seva funcio corresponent.
dispatcher.add_handler(CommandHandler('start', start, pass_user_data=True))
dispatcher.add_handler(CommandHandler('speak', speak, pass_user_data=True))

# Avis de qualsevol error que te lloc en una sessio del bot.
dispatcher.add_error_handler(error)

# Encen el bot.
updater.start_polling()
