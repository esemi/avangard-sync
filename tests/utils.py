from app.settings import app_settings


def avangard_client_configured() -> bool:
    return app_settings.avangard_login and app_settings.avangard_password
