from django.http import HttpResponse
from django.shortcuts import render

import trainer
from trainer.models import Category


def trainers(request):
    return HttpResponse("Trainers")


def specific_trainer(request, trainer_id):
    if request.method == 'GET':
        categories = trainer.models.Category.objects.all()
        services = trainer.models.Service.objects.filter(trainer = trainer_id)
        return render(request, 'trainer.html', {'categories': categories, 'services': services})


def service(request):
    if request.method == 'POST':
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        level = request.POST.get('level')
        duration = request.POST.get('duration')

        category = Category.objects.get(id=category_id)

        trainer.models.Service.objects.create(
            category=category,
            price=price,
            level=level,
            duration=duration,
            trainer=request.user
        )
    return HttpResponse("Service")


def specific_service(request, trainer_id, service_id):
    return HttpResponse("Specific trainer. Specific service")


def service_booking(request, trainer_id, service_id):
    return HttpResponse("Service booking")