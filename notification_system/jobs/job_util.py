import os
from util import utils
from util.custom_logger import getLogger

logger = getLogger()
def schedule_final_reminder_job():#For now it runs a job for all the guests who has not paid.
    format_at_2330 = "30 23 * * *"
    format_every_4min = "*/4 * * * *"
    command = "python3 /path/to/your_script.py"
    job_name = f"Final remainder for {utils.get_today_date()}"
    create_job(format_every_4min, command, job_name)

def remove_final_reminder_job():#For now it runs a job for all the guests who has not paid.
    job_name = f"Final remainder for {utils.get_today_date_minus_one_day()}"
    remove_job(job_name)



def create_job(cron_time, command, job_marker):
    logger.info("Operation [create_job] started")

    #Validate if existing, read jobs
    existing_jobs = os.popen('crontab -l').read()

    if job_marker not in existing_jobs:
        new_cron = existing_jobs + f"{cron_time} {command} {job_marker}"
        os.system(f'(echo "{new_cron.strip()}") | crontab -')
        logger.info(f"Cronjob scheduled for {cron_time}")
        return True

    logger.info(f"Cronjob already scheduled for {job_marker}")
    logger.info("Operation [create_job] finished")
    return False


def remove_job(job_marker):
    logger.info("Operation [remove_job] started")

    existing_jobs = os.popen('crontab -l').read()
    new_cron = '\n'.join(line for line in existing_jobs.splitlines() if job_marker not in line)
    os.system(f'(echo "{new_cron.strip()}") | crontab -')

    logger.info("Removed midnight cron job after execution")
    logger.info("Operation [remove_job] finished")
