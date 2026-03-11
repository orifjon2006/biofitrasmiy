from aiogram.fsm.state import State, StatesGroup

class AuthState(StatesGroup):
    waiting_for_login = State()    # Login kiritish bosqichi
    waiting_for_password = State() # Parol kiritish bosqichi

class DailyReportState(StatesGroup):
    waiting_for_video = State()    # Mashq videosini kutish