from aiogram.fsm.state import State, StatesGroup

class AdminAdd(StatesGroup):
    waiting_for_username = State() # Admin telegram username'ini kutish

class ClientAdd(StatesGroup):
    waiting_for_name = State()     # Ism-familiya
    waiting_for_address = State()  # Manzil
    waiting_for_phone = State()    # Telefon
    waiting_for_duration = State() # Kurs muddati (tugmalar orqali)

class BroadcastState(StatesGroup):
    waiting_for_message = State()  # Barchaga xabar yuborish matni