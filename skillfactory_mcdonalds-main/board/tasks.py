from celery import shared_task
from .models import Order
import datetime
from datetime import timedelta

@shared_task
def complete_order(oid):
    order = Order.objects.get(pk = oid)
    order.complete = True
    order.save()

@shared_task
def clear_old():
    old_orders = Order.objects.all().exclude(time_in__gt =
                        datetime.now() - timedelta(minutes = 5))
    old_orders.delete()


