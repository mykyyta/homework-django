from datetime import timedelta
from django.contrib.auth.models import User, Group
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from booking.models import Booking
from trainer.forms import ServiceForm
from trainer.models import Service, Category, TrainerSchedule, TrainerDescription

class TrainerTestCase(TestCase):
    #fixtures = ['fixture1.json'] вирішив використати метод setUp замість fixtures
    def setUp(self):
        self.client = Client()
        self.not_trainer = User.objects.create_user(username='client', password='password')
        self.trainer = User.objects.create_user(username='trainer', password='password')
        self.trainer_group = Group.objects.create(name='trainer')
        self.trainer.groups.add(self.trainer_group)
        self.boxing_category = Category.objects.create(name='boxing')

        start_time = timezone.now() + timedelta(days=1, hours=10)
        end_time = start_time + timedelta(hours=2)
        TrainerSchedule.objects.create(
            trainer=self.trainer,
            datetime_start=start_time,
            datetime_end=end_time
            )

        self.service = Service.objects.create(
            name = 'test service',
            category = self.boxing_category,
            trainer = self.trainer,
            price = 500,
            level = 'advanced',
            duration = 120,
            )

        self.service_data = {
            'name': 'test service',
            'category': self.boxing_category.id,
            'price': 100,
            'level': 'beginner',
            'duration': 60,
            }

    def test_trainer_ger(self):
        response = self.client.get(reverse('trainers'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('trainers', response.context)
        trainers = response.context['trainers']
        for trainer in trainers:
            self.assertTrue(trainer.groups.filter(name='trainer').exists())

    def test_services_get(self):
        response = self.client.get('/services/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services.html')
        self.assertIn('selected_services', response.context)
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertEqual(form, None)

    def test_services_get_trainer_services(self):
        self.client.login(username="trainer", password="password")
        response = self.client.get(f'/services/?trainer_id={self.trainer.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services.html')
        self.assertIn('selected_services', response.context)
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertIsInstance(form, ServiceForm)

    def test_services_post_denied_for_non_trainer(self):
        self.client.login(username="client", password="password")
        response = self.client.post('/services/', self.service_data)
        self.assertEqual(response.status_code, 403)

    def test_services_post_success(self):
        self.client.login(username="trainer", password="password")
        response = self.client.post('/services/', self.service_data)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/services/', response.url)

        self.assertEqual(Service.objects.count(), 2)
        service = Service.objects.last()
        self.assertEqual(service.category, self.boxing_category)
        self.assertEqual(service.trainer, self.trainer)
        self.assertEqual(service.name, "test service")
        self.assertEqual(service.price, 100)
        self.assertEqual(service.level, "beginner")
        self.assertEqual(service.duration, 60)

    def test_services_post_invalid_form(self):
        self.client.login(username="trainer", password="password")
        response = self.client.post('/services/', {
                                        "name": "",
                                        "category": "",
                                        "price": "",
                                        "level": "",
                                        "duration": "",
                                        })

        self.assertEqual(Service.objects.count(), 1)
        self.assertEqual(response.status_code, 302)

    def test_specific_service_get_success(self):
        self.client.login(username="trainer", password="password")
        response = self.client.get(reverse('specific_service', args=[self.service.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'specific_service.html')
        self.assertIn('free_slots_list', response.context)
        self.assertIn('service_obj', response.context)
        self.assertEqual(response.context['service_obj'], self.service)

    def test_specific_service_post(self):
        self.client.login(username="client", password="password")
        booking_start_time = timezone.now() + timedelta(days=1, hours=11)
        booking_data = {'training_start': booking_start_time.isoformat()}
        response = self.client.post(reverse('specific_service', args=[self.service.id]), booking_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Booking.objects.count(), 1)
        booking = Booking.objects.first()
        self.assertEqual(booking.customer, self.not_trainer)
        self.assertEqual(booking.trainer, self.trainer)
        self.assertEqual(booking.service, self.service)
        expected_end_time = booking_start_time + timedelta(minutes=self.service.duration)
        self.assertEqual(booking.datetime_end, expected_end_time)

    def test_specific_service_get_invalid_service(self):
        response = self.client.get(reverse('specific_service', args=[99]))
        self.assertEqual(response.status_code, 404)

    def test_specific_trainer_get_invalid_trainer(self):
        response = self.client.get(reverse('specific_trainer', args=[99]))
        self.assertEqual(response.status_code, 404)

    def test_specific_trainer_get_success(self):
        self.client.login(username="client", password="password")
        response = self.client.get(reverse('specific_trainer', args=[self.trainer.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('trainer', response.context)
        self.assertNotIn('service_form', response.context)

    def test_specific_trainer_get_trainer_profile(self):
        self.client.login(username="trainer", password="password")
        response = self.client.get(reverse('specific_trainer', args=[self.trainer.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('trainer', response.context)
        self.assertIn('service_form', response.context)
        self.assertIn('trainer_description_form', response.context)
        self.assertIn('trainer_schedule_form', response.context)

    def test_specific_trainer_post_trainer_description_create(self):
        self.client.login(username="trainer", password="password")
        trainer_description = {'trainer_description': '', 'name': 'test trainer'}
        response = self.client.post(reverse('specific_trainer', args=[self.trainer.id]), trainer_description)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(TrainerDescription.objects.count(), 1)
        trainer_desc_obj = TrainerDescription.objects.filter(trainer = self.trainer).first()
        self.assertEqual(trainer_desc_obj.name, 'test trainer')
        self.assertEqual(trainer_desc_obj.trainer, self.trainer)

    def test_specific_trainer_post_trainer_description_update(self):
        self.client.login(username="trainer", password="password")
        TrainerDescription.objects.create(name='first description', trainer=self.trainer)
        new_trainer_description = {'trainer_description': '', 'name': 'second description'}
        response = self.client.post(reverse('specific_trainer', args=[self.trainer.id]), new_trainer_description)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(TrainerDescription.objects.count(), 1)
        trainer_desc_obj = TrainerDescription.objects.filter(trainer = self.trainer).first()
        self.assertEqual(trainer_desc_obj.name, 'second description')
        self.assertEqual(trainer_desc_obj.trainer, self.trainer)


    def test_specific_trainer_post_trainer_schedule(self):
        self.client.login(username="trainer", password="password")
        datetime_start = timezone.localtime(timezone.now()).replace(hour=10, minute=0, second=0, microsecond=0)
        datetime_end = datetime_start.replace(hour=12)

        schedule_data = {
            'trainer_schedule': '',
            'datetime_start': datetime_start.isoformat(),
            'datetime_end': datetime_end.isoformat(),
            }

        response = self.client.post(
            reverse('specific_trainer', args=[self.trainer.id]),
            schedule_data
            )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(TrainerSchedule.objects.count(), 2)
        trainer_schedule = TrainerSchedule.objects.last()
        self.assertEqual(trainer_schedule.trainer, self.trainer)
        self.assertEqual(trainer_schedule.datetime_start, datetime_start)
        self.assertEqual(trainer_schedule.datetime_end, datetime_end)
