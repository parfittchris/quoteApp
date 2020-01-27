from apscheduler.schedulers.blocking import BlockingScheduler
import app



schedule = BlockingScheduler()

@schedule.scheduled_job('cron', hour='9', minute='40', timezone='America/New_York')
def get_quote():
    app.send_message()

schedule.start()

