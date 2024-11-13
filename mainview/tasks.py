from celery import shared_task
from moex_iss_api import get_all_securities, take_data_frame

@shared_task
def update_db():
    get_all_securities.get_securities_list()

@shared_task
def update_data():
    take_data_frame.fill_data_every_day()