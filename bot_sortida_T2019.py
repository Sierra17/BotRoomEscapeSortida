# Importa l'API de Telegram, i funcions per l'us del bot.
import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler

import numpy as np

# Importa l'API pel tractament d'arxius bytes, com ara imatges.
from PIL import Image
import requests
from io import BytesIO

# Importa el modul per el seguiment de la sessio del bot.
import logging

# Configurem el seguiment de la sessio del bot.
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

# Contrasenyes per debloquejar els misteris.
password = 'LOMOQUESO'
pass_len = len(password)
answer = "87"

# Fotos amb el problema de l'aparcament i la solució final.
Riddle_URL = 'https://i.stack.imgur.com/CT56W.jpg'
response = requests.get(Riddle_URL)
imatge = Image.open(BytesIO(response.content))
Answer_URL = 'https://elcaso.elnacional.cat/uploads/s1/67/67/92/rosali-a_1_645x451.jpeg'
response2 = requests.get(Answer_URL)
imatge_solucio = Image.open(BytesIO(response2.content))

# Bool per quan el concursant ha encertat el primer enigma.
fase1 = True

# Respostes del Sergio com a pistes de la contrasenya.
respostes = {0 : "¿Qué quieres chucky?",
                1 : "4 Euros chucky (Mirada impasible)",
                2 : "Se nos ha acabado el pan especial",
                3 : "Venga Luis espabila!",
                4 : "Rubio, que te saco el cuchillo",
                5 : "A ver Vicente, que no te oigo",
                6 : "Pero tú eres tonto, que no tengo todo el día",
                7 : "A ver Antonia, tú qué quieres?",
                8 : "No tenéis ni idea de jugar al tute, ya os enseñaré algún día",
                9 : "Luis, uno con queso!",}
iterator = 0


# Primera funcio, serveix per activar el bot. Envia un breu missatge de benvinguda.
def start(bot, update, user_data):
    try:
        message = "Si quieres hablar conmigo, pon /speak antes de tu mensaje."
        bot.send_message(chat_id=update.message.chat_id, text=message)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=update.message.chat_id, text='💣')


def distance_word(password, attempt):
    sum = 0.0
    n = len(attempt)
    m = len(password)
    if n < m:
        sum += (m - n)*26**4
    for i in range(min(m, n)):
        sum += float(ord(attempt[i]) - ord(password[i]))**4
    return sum


# Funció per convertir les imatges en color a escala de grisos.
def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.2989, 0.5870, 0.1140])


# Funció per distorsionar la imatge.
def distort(img, grau):
    # Convertir la imatge en una matriu per poder distorsionar-la.
    m = np.asarray(img)
    img2d = rgb2gray(m)
    m = np.asarray(rgb2gray(np.asarray(img)))

    m2 = np.zeros((img2d.shape[0], img2d.shape[1]), dtype=np.uint8)
    width = img2d.shape[0]
    height = img2d.shape[1]

    A = m.shape[0] / 3.0
    w = grau/50 / m.shape[1]
    print(w)
    # Funció lambda per fer un shift dels píxels.
    shift = lambda x: A * np.sin(2.0*np.pi* x * w)

    for i in range(m.shape[1]):
        m2[:,i] = np.roll(m[:,i], int(shift(i)))

    img2 = Image.fromarray(np.uint8(m2))
    return img2


# Funció per enviar la foto segons si s'ha encertat el codi o no.
def send_photo(bot, update, word, correct=False, distance = 0):
    try:
        if not correct:
            imatge_enviada = distort(imatge, distance)
            # Creem un objecte de tipus "BytesIO" per guardar la imatge.
            bio = BytesIO()
            # Creem i guardem la imatge amb una funcio externa per seguidament enviar-la.
            imatge_enviada.save(bio, 'PNG')
            bio.seek(0)
            bot.send_photo(chat_id=update.message.chat_id, photo=bio)
        else:
            bio = BytesIO()
            imatge.save(bio, 'PNG')
            bio.seek(0)
            bot.send_photo(chat_id=update.message.chat_id, photo=bio)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=update.message.chat_id, text='💣')


# Funció per parlar amb el bot i enviar missatges.
def speak(bot, update, user_data):
    try:
        miss_rebut = update.message.text[7:].replace(' ', '') # esborra el "/speak " del començament del missatge.
        if miss_rebut.upper() == password:
            global fase1
            fase1 = False
            send_photo(bot, update, miss_rebut, True, 0)
        elif miss_rebut == answer:
            bio = BytesIO()
            imatge_solucio.save(bio, 'PNG')
            bio.seek(0)
            bot.send_photo(chat_id=update.message.chat_id, photo=bio)
        elif not fase1:
            message = "❌"
            bot.send_message(chat_id=update.message.chat_id, text=message)
        else:
            distance = distance_word(password.upper(), miss_rebut.upper())
            send_photo(bot, update, miss_rebut, False, distance)
            global iterator
            message = respostes[iterator]
            iterator = (iterator + 1) % len(respostes)
            bot.send_message(chat_id=update.message.chat_id, text=message) 
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
