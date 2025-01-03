from datetime import timedelta

def free_slots (trainer_slots, booked_slots, training_time, interval):

    def round_dt(dt): #функція для округлення часу вверх відповідно до заданого інтервалу (н-д 9:05 -> 9:15)
        minutes_past_rounded_dt = dt.minute % interval
        if minutes_past_rounded_dt > 0:
            minutes_to_add = interval - minutes_past_rounded_dt
        else:
            minutes_to_add = 0
        return dt + timedelta(minutes=minutes_to_add, seconds=0, microseconds=0)

    available_slots = []

    for trainer_slot in trainer_slots: #проходимо по слотах в які тренер працює
        start_dt = round_dt(trainer_slot[0])
        while start_dt+timedelta(minutes=training_time) <= trainer_slot[1]: #перевіряємо всі варіанти стартового часу з заданим кроком до кінця поточного слоту тренера
            finish_dt= start_dt + timedelta(minutes=training_time)

            is_free = True
            for booked_slot in booked_slots: #перевіряємо чи є перетин з бронюваннями
                if not (finish_dt <= booked_slot[0] or start_dt >= booked_slot[1]):
                    is_free = False
                    break

            if is_free:
                available_slots.append(start_dt)

            start_dt += timedelta(minutes=interval)

    return available_slots