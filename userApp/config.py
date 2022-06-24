from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Awesome API"
    admin_email: str = "aman@mistpl.com"
    items_per_user: int = 50
    
    database_name: str
    user : str
    password : str
    host : str
    port : str

    secret_key : str
    algorithm : str
    access_token_expire_minutes : str

    class Config:
        env_file = ".env"

settings = Settings()