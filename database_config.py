# database_config.py - Configuração para PostgreSQL na Render

import os
from urllib.parse import urlparse

def get_database_url():
    """
    Retorna a URL do banco de dados baseada no ambiente
    """
    # Se estiver na Render, usar o PostgreSQL
    if os.environ.get('RENDER'):
        database_url = os.environ.get('DATABASE_URL')
        if database_url and database_url.startswith('postgres://'):
            # Render usa postgres://, mas SQLAlchemy precisa de postgresql://
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return database_url
    
    # Ambiente local - continua usando SQLite
    return 'sqlite:///lar_doce_app.db'

def get_app_config():
    """
    Retorna configurações da aplicação baseadas no ambiente
    """
    config = {
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'lar-doce-app-secret-key-2024'),
        'SQLALCHEMY_DATABASE_URI': get_database_url(),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JSON_SORT_KEYS': False,
    }
    
    # Configurações específicas para produção
    if os.environ.get('RENDER'):
        config.update({
            'DEBUG': False,
            'TESTING': False,
        })
    else:
        config.update({
            'DEBUG': True,
            'TESTING': True,
        })
    
    return config

# Para usar no main.py, substitua a configuração atual por:
# app.config.update(get_app_config())