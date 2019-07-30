from scraper import Scraper
from telegram_bot import TelegramBot
import schedule
import time
import datetime

MINUTES = 10
scraper = Scraper()
bot = TelegramBot()

def get_timestamp():
    return datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %X")

def get_message(appointments):
    print(appointments)
    free_appointments = []
    message = ""
    send_message = False
    for date in appointments:
        value = appointments[date]
        if len(value) > 0:
            free_appointments.append(date)
            print(date, value)

    if len(free_appointments) == 0:
        message = f"{get_timestamp()}: Unfortunately I couldn't find any free appointment :( but I will keep you updated in {MINUTES} mins."
        send_message = False
        print(message)

    else:
        url = "https://www46.muenchen.de/termin/index.php"
        message = f"{get_timestamp()}: I found these: {free_appointments}. Get your appointment here: {url}"
        send_message = True
        print(message)

    return message, send_message


def get_appointments():
    try:
        appointments = scraper.get_appointments()
        if appointments and type(appointments) is dict:
            return appointments

    except Exception as e:
        print(e)
        return dict()


def job():
    print()
    print('Cron job running...')
    appointments = get_appointments()
    if appointments:
        message, send_message = get_message(appointments)
        if send_message:
            bot.send_message(message)
    else:
        current_time = str(datetime.datetime.now())
        print(f"{current_time}: Error in fetching appointments. Trying again in 5 minutes...")


job()
schedule.every(MINUTES).minutes.do(job)
while 1:
    schedule.run_pending()
    time.sleep(1)
