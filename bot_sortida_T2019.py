# Importa l'API de Telegram, i funcions per l'us del bot.
import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler

import numpy as np
from scipy import signal

# Importa l'API pel tractament d'arxius bytes, com ara imatges.
from PIL import Image
import requests
from io import BytesIO

# Importa el modul per el seguiment de la sessio del bot.
import logging

# Importa el modul per treure accents
import unidecode

# Configurem el seguiment de la sessio del bot.
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

# Contrasenyes per debloquejar els misteris.
password = 'ESTEFANÍA'
pass_len = len(password)
answer = "87"

# Fotos amb el problema de l'aparcament i la solució final.
Riddle_URL = 'https://i.stack.imgur.com/CT56W.jpg'
response = requests.get(Riddle_URL)
imatge = Image.open(BytesIO(response.content))
Answer_URL = 'https://i.imgur.com/c4qfspT.png'
response2 = requests.get(Answer_URL)
imatge_solucio = Image.open(BytesIO(response2.content))

# Bool per quan el concursant ha encertat el primer enigma.
fase1 = True

# Respostes del Sergio com a pistes de la contrasenya.
respostes = {	
				0 : "Chicos, hay más imágenes.",
				1 : "No la conozco",
				2 : "No puedo, no quiero ver más",
				3 : "Yo es que la tengo en un 'pedastal'",
				4 : "Tengo palpitaciones en el nabo",
				5 : "No lo puedo ver, le estoy cogiendo una 'rítia'..."
			}
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
	
	uattempt = unidecode.unidecode(attempt)
	upassword = unidecode.unidecode(password)
	
	if n < m:
		sum += (m - n)*26
	for i in range(min(m, n)):
		sum += abs(float(ord(uattempt[i]) - ord(upassword[i])))
	return sum


# Funció per convertir les imatges en color a escala de grisos.
def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.2989, 0.5870, 0.1140])

# Sinusoid distorting
def sindistort(img, grau):
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

# Funció per distorsionar la imatge.
def distort(img, grau):
    # Convertir la imatge en una matriu per poder distorsionar-la.
	m = np.asarray(img)
	img2d = rgb2gray(m)
	imgmat = np.asarray(rgb2gray(np.asarray(img)))
	
	width = img2d.shape[0]
	height = img2d.shape[1]
	
	delta = np.array([[0,0,0],
	[0,1,0],
	[0,0,0]])
	
	distortion = np.array([[12,-9,4],
	[-3,-5,13],
	[9,5,-7]])
	
	grau = (grau/100)**2
	print(grau)
	
	filter = delta + grau*distortion
	
	conv = signal.convolve2d(imgmat, filter)
	
	conv_img = Image.fromarray(np.uint8(conv))
	return conv_img


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
        if unidecode.unidecode(miss_rebut.upper()) == unidecode.unidecode(password.upper()):
            global fase1
            fase1 = False
            send_photo(bot, update, miss_rebut, True, 0)
            
            try:
                message = "ESTEFANÍAAAAA, pon /speak antes de tu respuesta."
                bot.send_message(chat_id=update.message.chat_id, text=message)
            except Exception as e:
                print(e)
                bot.send_message(chat_id=update.message.chat_id, text='💣')

        elif miss_rebut == answer:
            bio = BytesIO()
            imatge_solucio.save(bio, 'PNG')
            bio.seek(0)
            bot.send_photo(chat_id=update.message.chat_id, photo=bio)
            
            message = "Fi de branca. (2/3)"
            bot.send_message(chat_id=update.message.chat_id, text=message)
            
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
