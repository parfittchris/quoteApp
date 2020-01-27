from apscheduler.schedulers.background import BlockingScheduler
import app



schedule = BlockingScheduler()

@schedule.scheduled_job('cron', hour='9', minute='30', timezone='America/New_York')
def get_quote():
    app.send_message()

# schedule.add_job(app.send_message, trigger='cron', hour='9', minute='10')
schedule.start()

