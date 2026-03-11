# Barcha handler modullarini papka ichidan chaqirib olamiz
from . import auth
from . import super_admin
from . import sub_admin
from . import client_panel
from . import daily_report

# Boshqa joydan (masalan, bot.py dan) chaqirilganda faqat shularni taqdim etamiz
__all__ = [
    "auth",
    "super_admin",
    "sub_admin",
    "client_panel",
    "daily_report"
]
