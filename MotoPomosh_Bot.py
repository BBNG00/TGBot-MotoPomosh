# Импортируем необходимые классы.
import logging
import emoji
import sqlite3
from telegram.ext import Application, MessageHandler, filters, CommandHandler,CallbackQueryHandler, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup
from pochta import otpravka_pisma

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)
text_moto='\U0001F3CD'
text_pochin='\U0001F529'
text_dobav_probl='\U0001F6E0'
text_novich='\U0001F576'
text_strelka='\U0001F448'
CHOOSING, TYPING_REPLY, TYPING_CHOICE, BLAGODARNOST = range(4)
CHOOSING1, TYPING_REPLY1, TYPING_CHOICE1, BLAGODARNOST1 = range(4)
VYDACHA = range(1)

reply_keyboard = [[rf'{text_pochin}Нати проблему', rf'{text_novich}Помощь новичку'],
                      [rf'{text_dobav_probl}Добавить проблему', rf'{text_strelka}Выход в меню']]
reply_keyboard2 = [[rf'{text_strelka}Выход в меню']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
markup2 = ReplyKeyboardMarkup(reply_keyboard2, one_time_keyboard=True)

problema = ''

#Поиск проблемы переменные
motor =''
vid =''
pr_ma=''

# Подключение к БД
basa = sqlite3.connect("bas_dan_problem.db")
# Создание курсора
cur = basa.cursor()

# Подключение к БД
basa2 = sqlite3.connect("basa_for_novichok.db")
# Создание курсора
cur2 = basa2.cursor()
# Определяем функцию-обработчик сообщений.
# У неё два параметра, updater, принявший сообщение и контекст - дополнительная информация о сообщении.
async def start(update, context):
    """Отправляет сообщение когда получена команда /start"""
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Я мотопомощь-бот {text_moto}-бот для помощи мотоциклистам. Здесь ты можешь выбрать:                                              "
    rf"{text_novich}1 --Помощь новичку-- и нати проблемы, с которыми сталкиваются юные мотоциклисты,                                                                     "
    rf"{text_pochin}2 --Нати проблему-- ты можешь нати, какая у тебя поломка и как её починить,                                                                                                "
    rf"{text_dobav_probl}--3 --Добавить проблему-- если вы нашли и устранили проблему которо нет в наше базе, вы можете отправить решение проблемы с соответствующим решением                                                                             "
    rf"{text_strelka}--4 --Выход в меню--, то-есть возврат сюда",
        reply_markup=markup
    )
#Помощь новичку
async def dlya_novichkov(update, context):
    await update.message.reply_text(
        "Здравствуй человек который недавно вступил в мотобратство! Скорее всего ты хочешь научиться обслуживать"
        " мотоцикл и узнать как им управлять или например как делать трюки на мотоцихлах. Просто напиши сюда хэштэг(лучше скопировать и вставить) из списка"
        "(тебе выдастся информация по твоему вопросу и ссылка на ютуб или статью, в которых ты узнаешь про запрос чуть глубже):                                                                                              "
        "#как_делать_вилли                                                                                                                                                                     "
        "#как_делать_бёрн_аут                                                                                                                                                                     "
        "#как_сменить_масло                                                                                                                                                                     "
        "Удачи"
        ,
        reply_markup=markup2
    )
    return VYDACHA
async def novichk(update, context):
    zapros = update.message.text
    result = cur2.execute("""SELECT * FROM novich
                        WHERE nazvanie = ?""",
                         (zapros, )).fetchall()
    if len(result) == 0:
        await update.message.reply_text(
            rf'Вы неправильно написали хэштэг. Попробуйте снова.',
            reply_markup=markup2
        )
    elif len(result) != 0:
        await update.message.reply_text(
            rf'{(result[0])[1]} Спасибо за пользование ботом новичок.',
            reply_markup=markup2
        )
    return ConversationHandler.END
#Конец
#Начало принтие проблемы(именно с ответом)
async def motor_moto(update, context):
    await update.message.reply_text(
        "Привет! Давай начнем искать,что сломалось в твоём двухколесном друге и как это починить."
        "Сначала выберем ту часть, которая сломана. Надо написать в бот один из хэштэгов снизу:                                                       "
        "#мотор  то есть у тебя произошла поломка связанная с мотором, или, например, мотор издаёт неприятный шум                                                                                                                           "
        "#мотоцикл  то есть у тебя проблема не связанная с мотором, а связанная с другими частями мотоцикла(колеса, цепь, амортизатор, рама и тд и тп)."
        "Поняв какая часть мотоцикла у тебя сломана, нужно написать #мотор или #мотоцикл соответственно сообщением в бот. Если ты случайно выбрал этот пункт, то нажмина кнопку "
        rf'{text_strelka}Выход в меню или напиши {text_strelka}Выход в меню в чат.'
        ,
        reply_markup=markup2
    )
    return CHOOSING1

async def vid_marka(update, context):
    global motor
    motor = update.message.text
    await update.message.reply_text(
        "Теперь, выбрав часть мотоцикла - выберем, либо мотор, либо марку мотоцикла. "
        "Если у вас питбайк(в особенности 125 кубов, ну то есть обычный китайский пит) то напишите хэштэг:                                                                                                                                     "
        "#YX125 ,если вдруг наша команда нашла мотор для пита, который отличается строением(вплане какие-то пломки решаются иначе,чем обычно) то он будет в этом списке:                                                                              "
        "Если у вас китайский эндуро то тут такая же схема. Общий хэштэг:                                                                                                                                           "
        "#YX250  ,моторы с отличием:                                                                                                                                                                                             "
        "Теперь моторы список моторов:                                                                                                                                                                                             "
        "МАРКИ МОТОЦИКЛОВ(то есть это хэштэги для проблем, не связанных с мотором).                                                                                                                                               "
        "Общие: #питбайк , #эндуро , #дорожныемотоциклы                                                                                                                           "
        "Марки отдельно:")
    return TYPING_REPLY1
async def nazvanie_problemy_samoy(update, context):
    global vid
    vid = update.message.text
    await update.message.reply_text(
        "Теперь выберите проблему:                                                                                                 "
        "#YX125 :                                                                                                 "
        "- #протечка_масла_слева                                                                                                 "
        "- #металлический_скрежет_при_работе_мотора                                                               "
        "#YX250 :                                                                                                 "
        "- #металлический_скрежет_при_работе_мотора                                                               "
        "#питбайк :                                                                                                 "
        "- #неработает_электростартер                                                                                                 "
        "- #восьмёрка_колеса                                                                                                 "
        "#эндуро :                                                                                                 "
        "- #восьмёрка_колеса                                                                                                 "
        "#дорожныемотоциклы :                                                                                                 "
        "- #                                                                                                 "
        
        "Если у вы увидели проблему на другом моторе но на вашем его нет, "
        "то вернитесь в начало и поищите в проблемах для общих проблем. Если в общих нет, то откройте решение проблемы на другом моторе."
        "Если это решение не подошло и проблемы на вашем моторе нет, извините пожалуйста, мы пока не добавили этку прблему в базу."
        rf"Мы будем очень благодарны, если вы найдёте проблему которой нету в нашей базе и добавите её(пункт {text_dobav_probl}Добавить проблему)",
    )
    return BLAGODARNOST1

async def spasibo(update, context):
    """Запрос описания пользовательской категории."""
    global motor, vid, pr_ma
    pr_ma = update.message.text
    result = cur.execute("""SELECT * FROM baseproblems
                    WHERE chast = ? and motorormarka = ? and samaproblema = ?""",
                         (motor, vid, pr_ma)).fetchall()
    if len(result) == 0:
        await update.message.reply_text('Благодарим за использование бота. К сожалению мы не нашли решение к вашей проблеме(скорее всего вы неправильно писали хэштэги'
                                        ' попробуйте снова). Если вы нашли проблему, которой'
            rf' нет в нашей базе, и нашли к ней решение, то будем благодарны, если вы добавите её в базу(пункт {text_dobav_probl}Добавить проблему).',
            reply_markup=markup2
        )
    elif len(result) != 0:
        await update.message.reply_text(
            rf'{(result[0])[3]}                                                                                                                                                                                             '
            'Благодарим за использование бота. Если вы нашли проблему, которой'
            rf' нет в нашей базе, и нашли к ней решение, то будем благодарны, если вы добавите её в базу(пункт {text_dobav_probl}Добавить проблему).',
            reply_markup=markup2
        )
    return ConversationHandler.END

#конец принятия


# начало принятия проблемы
async def nach_problema(update, context):
    """Начvало разговора, просьба ввести данные."""
    await update.message.reply_text(
        "Привет! Скоре-всего вы очень хороший человек и решили добавить новую проблему. Давайте"
        " начнем с выбора хэштэгов:                                                                                                     "
        "#мотор  то есть у тебя произошла поломка связанная с мотором, или, например, мотор издаёт неприятный шум                                                                                                                           "
        "#мотоцикл  то есть у тебя проблема не связанная с мотором, а связанная с другими частями мотоцикла(колеса, цепь, амортизатор, рама и тд и тп).                                                                                               "
        "Напиши один из хэштэгов, подходящий к твоей проблеме.",
        reply_markup=markup2
    )
    return CHOOSING

async def vyhod_v_nachalo(update, context):
    """Отправляет сообщение когда получена команда /start"""
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Я мотопомощь-бот {text_moto}-бот для помощи мотоциклистам. Здесь ты можешь выбрать:                                              "
    rf"{text_novich}1 --Помощь новичку-- и нати проблемы, с которыми сталкиваются юные мотоциклисты,                                                                     "
    rf"{text_pochin}2 --Нати проблему-- ты можешь нати, какая у тебя поломка и как её починить,                                                                                                "
    rf"{text_dobav_probl}--3 --Добавить проблему-- если вы нашли и устранили проблему которо нет в наше базе, вы можете отправить решение проблемы с соответствующим решением                                                                             "
    rf"{text_strelka}--4 --Выход в меню--, то-есть возврат сюда",
        reply_markup=markup
    )
    return ConversationHandler.END
async def nazvanie_problemy(update, context):
    global problema
    problema += update.message.text
    await update.message.reply_text(
        "Теперь добавь саму проблему(с хэштэгом). Например: (#протечка_масла_с_левой_стороны_мотора).",
    )
    return TYPING_CHOICE

async def sama_problema(update, context):
    """Запрос описания пользовательской категории."""
    global problema
    problema += ' ' + update.message.text
    await update.message.reply_text(
        'Теперь опишите проблему, и как вы её решили(было бы круто с ссылкой на видео на ютубе, если такая есть)',
    )
    return TYPING_REPLY
async def marka(update, context):
    """Запрос описания пользовательской категории."""
    global problema
    problema += ' ' + update.message.text
    await update.message.reply_text(
        'Теперь добавть марку мотора(например #139FMB), и добавьте марку мотоцикла(#KAWASAKI_KDX_125). Вот как'
        ' это должно выглядеть. (#139FMB #KAWASAKI_KDX_125)'
    )
    return BLAGODARNOST
async def poka(update, context):
    """Запрос описания пользовательской категории."""
    global problema
    problema += ' ' + update.message.text
    otpravka = otpravka_pisma(problema)
    await update.message.reply_text(
        rf'Благодарим за добавление проблемы. {problema}',
        reply_markup=markup2
    )
    problema =''
    return ConversationHandler.END
#конец




def main():
    application = Application.builder().token('xxxxxxxxxxxxxx').build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(rf'^{text_novich}Помощь новичку$'), dlya_novichkov)],
        states={
            VYDACHA: [
                MessageHandler(filters.Regex(rf'^{text_strelka}Выход в меню$'), vyhod_v_nachalo),
                MessageHandler(
                    filters.TEXT, novichk
                )
            ]
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), marka)],
    ))

    application.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(rf'^{text_pochin}Нати проблему$'), motor_moto)],
        states={
            CHOOSING1: [
                MessageHandler(filters.Regex(rf'^{text_strelka}Выход в меню$'), vyhod_v_nachalo),
                MessageHandler(
                    filters.TEXT, vid_marka
                )
            ],
            TYPING_REPLY1: [
                MessageHandler(
                    filters.TEXT, nazvanie_problemy_samoy
                )
            ],
            BLAGODARNOST1: [
                MessageHandler(
                    filters.TEXT, spasibo
                )
            ]
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), marka)],
    ))

    application.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(rf'^{text_dobav_probl}Добавить проблему$'), nach_problema)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex(rf'^{text_strelka}Выход в меню$'), vyhod_v_nachalo),
                MessageHandler(
                    filters.TEXT, nazvanie_problemy
                )
            ],
            TYPING_CHOICE: [
                MessageHandler(
                    filters.TEXT, sama_problema
                )
            ],
            TYPING_REPLY: [
                MessageHandler(
                    filters.TEXT, marka
                )
            ],
            BLAGODARNOST: [
                MessageHandler(
                    filters.TEXT, poka
                )
            ]
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), marka)],
    ))

    application.add_handler(MessageHandler(filters.Regex(rf'^{text_strelka}Выход в меню$'), start))

    # Запускаем приложение.
    application.run_polling()

# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
