from aiogram import Router
from . import auth, super_admin, sub_admin, client_panel

def get_main_router() -> Router:
    main_router = Router()
    
    # Routerlarni tartib bilan ulash
    # Eslatma: auth birinchi turishi tavsiya etiladi
    main_router.include_router(auth.router)
    main_router.include_router(super_admin.router)
    main_router.include_router(sub_admin.router)
    main_router.include_router(client_panel.router)
    
    return main_router