from datetime import timedelta
from dateutil import parser
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from trainer.forms import ServiceForm, TrainerDescriptionForm, TrainerScheduleForm
from trainer.models import *
from booking.models import Booking as BookingModel
from trainer.utils import free_slots
from django.contrib.auth.models import User


def trainers(request):
    if request.method == 'GET':
        selected_trainers = User.objects.filter(groups__name='trainer')
        return render(request, 'trainers.html', {'trainers': selected_trainers})


def specific_trainer(request, trainer_id):
    if request.user == User.objects.get(pk=trainer_id):
        trainer_description_form = TrainerDescriptionForm()
        trainer_schedule_form = TrainerScheduleForm()
        service_form = ServiceForm()
        current_trainer = request.user

        # Handle POST requests for each form
        if request.method == 'POST':
            if 'trainer_description' in request.POST:
                try:
                    trainer_description = TrainerDescription.objects.get(trainer=current_trainer)
                except TrainerDescription.DoesNotExist:
                    trainer_description = None

                trainer_description_form = TrainerDescriptionForm(request.POST)

                if trainer_description_form.is_valid():
                    if trainer_description:
                        trainer_description.name = trainer_description_form.cleaned_data['name']
                        trainer_description.save()
                    else:
                        TrainerDescription.objects.create(trainer=current_trainer, **trainer_description_form.cleaned_data)
                    return redirect('specific_trainer', trainer_id)

            elif 'trainer_schedule' in request.POST:
                trainer_schedule_form = TrainerScheduleForm(request.POST)
                if trainer_schedule_form.is_valid():
                    TrainerSchedule.objects.create(trainer=current_trainer, **trainer_schedule_form.cleaned_data)

                    return redirect('specific_trainer', trainer_id)

            elif 'service' in request.POST:
                service_form = ServiceForm(request.POST)
                if service_form.is_valid():
                    Service.objects.create(
                        name=service_form.cleaned_data['name'],
                        category=service_form.cleaned_data['category'],
                        trainer=request.user,
                        price=service_form.cleaned_data['price'],
                        level=service_form.cleaned_data['level'],
                        duration=service_form.cleaned_data['duration'],
                    )
                    return redirect('specific_trainer', trainer_id)

        return render(request, 'trainer_account.html', {'trainer_description_form': trainer_description_form,
                                                                                'trainer_schedule_form': trainer_schedule_form,
                                                                                'service_form': service_form,
                                                                                "trainer": current_trainer})


def services(request):
    if request.method == 'GET':
        selected_services = Service.objects.all()
        form = ServiceForm()
        return render(request, 'services.html', {"selected_services": selected_services, "form": form})
    else:
        if not request.user.groups.filter(name='trainer').exists():
            return JsonResponse({"error": "Permission denied"}, status=403)
        form = ServiceForm(request.POST)
        if form.is_valid():
            Service.objects.create(
                name = form.cleaned_data['name'],
                category = form.cleaned_data['category'],
                trainer = request.user,
                price = form.cleaned_data['price'],
                level = form.cleaned_data['level'],
                duration = form.cleaned_data['duration'],
            )

        return redirect('services')


def specific_service(request, service_id):
    service_obj = Service.objects.get(id=service_id)
    trainer_obj = service_obj.trainer
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
        return redirect('specific_service', service_id=service_id)


def service_booking(request, trainer_id, service_id):
    return HttpResponse("Service booking")