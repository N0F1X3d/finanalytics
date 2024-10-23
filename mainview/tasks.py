from celery import shared_task
from moex_iss_api import get_all_securities

@shared_task
def update_db():
    get_all_securities.get_securities_list()
