from scraper import Scraper
from telegram_bot import TelegramBot
import schedule
import time
import datetime

MINUTES = 5
MONTH = '2019-10'
NUM_CONSECUTIVE = 2
scraper = Scraper(appointment_type="Researcher") # possible options are ["Researcher", "BlueCard"]
bot = TelegramBot()

def get_timestamp():
    return datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %X")

def get_message(appointments, consecutive=1):
    print(appointments)
    free_appointments = []
    message = ""
    send_message = False
    for date in appointments:
        value = appointments[date]
        if len(value) > 0:
            for i in range(0, len(value)):
                timestamp = time.mktime(time.strptime(value[i], '%H:%M'))
                j = i + 1
                while j < len(value):
                    timestamp_next = time.mktime(time.strptime(value[j], '%H:%M'))
                    diff = timestamp_next - timestamp
                    if diff/60 <= 30 * (j - i):
                        j = j+1
                        continue
                    else:
                        break
                if (j - i) >= consecutive:
                    free_appointments.append(date + " " + value[i])
                

    if len(free_appointments) == 0:
        message = f"{get_timestamp()}: Unfortunately I couldn't find any free appointment :( but I will keep you updated in {MINUTES} mins."
        send_message = False
        print(message)

    else:
        url = "https://www46.muenchen.de/termin/index.php"
        message = "I found the following appointments for " + str(NUM_CONSECUTIVE) + " people at " + get_timestamp() + ":\n" + "\n".join(free_appointments) + "\nGet your appointment here: " + url
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
    filtered_appointments = {}
    # Filter specific month
    filtered_month = list(filter(lambda x: MONTH in x, appointments))
    for date in filtered_month:
        filtered_appointments.update({date: appointments[date]})
    if filtered_appointments:
        message, send_message = get_message(filtered_appointments, consecutive=NUM_CONSECUTIVE)
        if send_message:
            try:
                bot.send_message(message)
            except Exception as e:
                print(e)
                print("Unable to send message via TelegramBot. Aborting until next check.")
                pass
    else:
        current_time = str(datetime.datetime.now())
        print(f"{current_time}: No appointments found in {MONTH}. Trying again in {MINUTES} minutes...")


job()
schedule.every(MINUTES).minutes.do(job)

# Special timings
# schedule.every().day.at("06:00").do(job)
# schedule.every().day.at("07:01").do(job)
# schedule.every().day.at("07:31").do(job)
# schedule.every().day.at("07:59").do(job)
# schedule.every().day.at("08:00").do(job)
# schedule.every().day.at("08:01").do(job)

while 1:
   schedule.run_pending()
   time.sleep(1)
