import os
import requests
import telegram
import time
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

FORMAT = '%(asctime)-15s %(message)s'
PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
BOT = telegram.Bot(token=TELEGRAM_TOKEN)
HOME_WORK_STATUSES = ['approved', 'rejected']
HOMEWORK_STATE_KEYS = ['homework_name', 'status']


def parse_homework_status(homework):
    for key in HOMEWORK_STATE_KEYS:
        if key not in homework.keys():
            raise KeyError(f'Не обнаружен ключ: {key}')
    homework_name = homework[HOMEWORK_STATE_KEYS[0]]
    hw_status = homework[HOMEWORK_STATE_KEYS[1]]

    if hw_status not in HOME_WORK_STATUSES:
        raise ValueError('Неожиданный статус работы')
    if hw_status == HOME_WORK_STATUSES[1]:
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = (
            'Ревьюеру всё понравилось, можно приступать к следующему '
            'уроку.'
        )
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    if current_timestamp is None:
        raise ValueError('current_date == None')
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    homework_statuses = requests.get(
        URL, headers=headers, params=params
    )
    if homework_statuses.status_code != 200:
        logger.info('Неудачная попытка установить соединение')
    return homework_statuses.json()


def send_message(message):
    logger.info(f'Посылаю сообщение - {message}')
    return BOT.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())
    logger.info('Бот запущен')

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0])
                )
            current_timestamp = new_homework.get('current_date')
            time.sleep(60 * 10)

        except Exception as e:
            logger.exception(e)
            time.sleep(60)
            continue


if __name__ == '__main__':
    main()
