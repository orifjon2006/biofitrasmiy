def get_main_router() -> Router:
    main_router = Router()
    
    # Tartib mana shunday bo'lsin:
    main_router.include_router(auth.router)         # 1. Avval login/parol tekshiruvi
    main_router.include_router(super_admin.router)  # 2. Katta admin filtri bilan
    main_router.include_router(sub_admin.router)    # 3. Kichik admin xabarlari
    main_router.include_router(client_panel.router) # 4. Mijozlar paneli
    main_router.include_router(daily_report.router) # 5. Kunlik hisobotlar
    
    return main_router
