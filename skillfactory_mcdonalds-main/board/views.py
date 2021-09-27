from django.shortcuts import redirect
from django.views.generic import TemplateView, CreateView
from .tasks import complete_order
from .models import Order
from datetime import datetime
from django.db.models.signals import post_save
from django.core.mail import mail_managers
from .models import Appointment
from django.views import View
from django.shortcuts import render
from django.core.mail import mail_admins


class IndexView(TemplateView):
    template_name = "board/index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = Order.objects.all()
        return context


class NewOrderView(CreateView):
    model = Order
    fields = ['products']
    template_name = 'board/new.html'
    
    def form_valid(self, form):
        order = form.save()
        order.cost = sum([prod.price for prod in order.products.all()])
        order.save()
        complete_order.apply_async([order.pk], countdown = 5)
        return redirect('/')
        

def take_order(request, oid):
    order = Order.objects.get(pk=oid)
    order.time_out = datetime.now()
    order.save()
    return redirect('/')


def notify_managers_appointment(sender, instance, created, **kwargs):
    subject = f'{instance.client_name} {instance.date.strftime("%d %m %Y")}'

    mail_managers(
        subject=subject,
        message=instance.message,
    )


post_save.connect(notify_managers_appointment, sender=Appointment)


class AppointmentView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'make_appointment.html', {})

    def post(self, request, *args, **kwargs):
        appointment = Appointment(
            date=datetime.strptime(request.POST['date'], '%Y-%m-%d'),
            client_name=request.POST['client_name'],
            message=request.POST['message'],
        )
        appointment.save()

        mail_admins(
            subject=f'{appointment.client_name} {appointment.date.strftime("%d %m %Y")}',
            message=appointment.message,
        )

        return redirect('appointments:make_appointment')