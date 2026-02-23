from app.modules.auth import auth_service


async def register_user(body):
    return await auth_service.register_user(body)


async def login_user(body):
    return await auth_service.login_user(body)


async def refresh_user_token(body):
    return await auth_service.refresh_user_token(body)


async def get_user_profile(user_id: str):
    return await auth_service.get_user_profile(user_id)
