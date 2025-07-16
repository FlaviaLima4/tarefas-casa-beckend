from flask import Flask
from flask_cors import CORS
import os
from database import init_database
from routes import api

def create_app():
    """Função factory para criar a aplicação Flask"""
    
    # Criar a instância do Flask
    app = Flask(__name__)
    
    # Configurações da aplicação
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'lar-doce-app-secret-key-2024')
    
    # Configuração do banco de dados
    if os.environ.get('RENDER'):
        # Produção na Render - PostgreSQL
        database_url = os.environ.get('DATABASE_URL')
        if database_url and database_url.startswith('postgres://'):
            # Render usa postgres://, mas SQLAlchemy precisa de postgresql://
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Desenvolvimento local - SQLite
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lar_doce_app.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False  # Manter ordem dos campos no JSON
    
    # Configurar CORS baseado no ambiente
    if os.environ.get('RENDER'):
        # Produção - permitir apenas domínios específicos
        CORS(app, origins=[
            "https://tarefas-casa-gold.vercel.app",  # Seu frontend na Vercel
            "http://localhost:3000",                 # Desenvolvimento local
            "http://localhost:5173",                 # Vite dev server
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ])
    else:
        # Desenvolvimento - permitir qualquer origem
        CORS(app, origins="*")
    
    # Inicializar o banco de dados
    init_database(app)
    
    # Registrar as rotas
    app.register_blueprint(api, url_prefix='/api')
    
    # Rota raiz para verificar se o servidor está funcionando
    @app.route('/')
    def home():
        return {
            'message': 'Bem-vindo ao Lar Doce App API! 🏠',
            'version': '1.0.0',
            'environment': 'production' if os.environ.get('RENDER') else 'development',
            'database': 'PostgreSQL' if os.environ.get('RENDER') else 'SQLite',
            'endpoints': {
                'health': '/api/health',
                'login': '/api/login',
                'users': '/api/users',
                'tasks': '/api/tasks',
                'ranking': '/api/ranking',
                'stats': '/api/stats'
            }
        }
    
    # Rota específica para CORS preflight
    @app.route('/api/<path:path>', methods=['OPTIONS'])
    def handle_options(path):
        return '', 200
    
    # Handler para erros 404
    @app.errorhandler(404)
    def not_found(error):
        return {
            'error': 'Endpoint não encontrado',
            'message': 'Verifique a URL e tente novamente'
        }, 404
    
    # Handler para erros 500
    @app.errorhandler(500)
    def internal_error(error):
        return {
            'error': 'Erro interno do servidor',
            'message': 'Algo deu errado, tente novamente mais tarde'
        }, 500
    
    return app

# Criar instância da aplicação para Gunicorn (DEVE estar no nível do módulo)
app = create_app()

def main():
    """Função principal para rodar o servidor em desenvolvimento"""
    
    # Configurações para desenvolvimento vs produção
    if os.environ.get('RENDER'):
        # Produção na Render - Gunicorn vai gerenciar
        print("🚀 Aplicação criada para produção na Render")
        return
    else:
        # Desenvolvimento local
        port = int(os.environ.get('PORT', 5000))
        host = '127.0.0.1'
        debug = True
        print("🏠 Iniciando Lar Doce App API em DESENVOLVIMENTO...")
        
        print(f"📍 Servidor rodando em: http://{host}:{port}")
        print(f"🔧 Modo debug: {debug}")
        print(f"💾 Banco de dados: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print("\n🚀 Endpoints disponíveis:")
        print(f"   • Health Check: http://{host}:{port}/api/health")
        print(f"   • Login:        http://{host}:{port}/api/login")
        print(f"   • Usuários:     http://{host}:{port}/api/users")
        print(f"   • Tarefas:      http://{host}:{port}/api/tasks")
        print(f"   • Ranking:      http://{host}:{port}/api/ranking")
        print(f"   • Estatísticas: http://{host}:{port}/api/stats")
        print("\n" + "="*50)
        
        # Rodar o servidor
        app.run(
            host=host,
            port=port,
            debug=debug
        )

if __name__ == '__main__':
    main()