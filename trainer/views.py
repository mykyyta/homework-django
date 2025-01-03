from datetime import datetime, timedelta
from dateutil import parser
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from trainer.models import *
from booking.models import Booking as BookingModel
from trainer.utils import free_slots
from django.contrib.auth.models import User

def trainers(request):
    return HttpResponse("Trainers")


def specific_trainer(request, trainer_id):
    if User.groups.get(name='Trainer').exists():

        if request.method == 'GET':
            trainer_obj = get_object_or_404(User, pk=trainer_id)
            categories = Category.objects.all()
            services = Service.objects.filter(trainer = trainer_obj).all()
            return render(request, 'trainer.html', {'categories': categories, 'services': services})


def service(request):
    if request.method == 'GET':
        services = Service.objects.all()
        return render(request, 'services.html', {"services": services})
    else:
        if not request.user.groups.filter(name='Trainer').exists():
            return JsonResponse({"error": "Permission denied"}, status=403)
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        level = request.POST.get('level')
        duration = request.POST.get('duration')

        category = Category.objects.get(id=category_id)

        Service.objects.create(
            category=category,
            price=price,
            level=level,
            duration=duration,
            trainer=request.user
        )
        return JsonResponse({"message": "Service created successfully"}, status=201)


def specific_service(request, trainer_id, service_id):
    service_obj = Service.objects.get(id=service_id)
    trainer_obj = User.objects.get(pk=trainer_id)
    if request.method == 'GET':
        start_date  = (timezone.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = (timezone.now() + timedelta(days=3)).replace(hour=23, minute=59, second=59, microsecond=999999)
        trainer_schedule =  (TrainerSchedule.objects
                             .filter(trainer=trainer_obj, datetime_start__range=(start_date, end_date))
                                .values_list('datetime_start', 'datetime_end'))
        booked_slots = (BookingModel.objects
                        .filter(trainer=trainer_obj, datetime_start__range=(start_date, end_date))
                        .values_list('datetime_start', 'datetime_end'))
        free_slots_list = free_slots(trainer_schedule, booked_slots, int(service_obj.duration), 15)
        return render(request, 'specific_service.html', {'free_slots_list': free_slots_list, 'service_obj': service_obj})

    else:
        training_start = parser.parse(request.POST.get('training_start'))
        BookingModel.objects.create(customer=request.user,
                                    trainer=trainer_obj,
                                    service=service_obj,
                                    datetime_start=training_start,
                                    datetime_end=training_start+timedelta(minutes=int(service_obj.duration)),
                                    status=True
                                    )
        return redirect('specific_service', trainer_id=trainer_id, service_id=service_id)


def service_booking(request, trainer_id, service_id):
    return HttpResponse("Service booking")