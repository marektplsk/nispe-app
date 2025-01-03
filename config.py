import os

class Config:
    DATABASE_USER = os.getenv('DB_USER', 'root')
    DATABASE_PASSWORD = os.getenv('DB_PASSWORD', 'marek123')
    DATABASE_HOST = os.getenv('DB_HOST', 'localhost')
    DATABASE_NAME = os.getenv('DB_NAME', 'nispeDB')
