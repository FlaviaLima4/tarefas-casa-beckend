from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Inicializar SQLAlchemy
db = SQLAlchemy()

# Modelo de Usuário
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar_color = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Criptografa e define a senha do usuário"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Converte o usuário para dicionário (para JSON)"""
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'avatar_color': self.avatar_color,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Modelo de Tarefa
class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(20), nullable=False)  # Segunda, Terça, etc.
    task_name = db.Column(db.String(200), nullable=False)
    points = db.Column(db.Integer, default=1)  # Pontos que a tarefa vale
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    completed_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    assigned_user = db.relationship('User', foreign_keys=[assigned_user_id], backref='assigned_tasks')
    completed_by_user = db.relationship('User', foreign_keys=[completed_by_user_id], backref='completed_tasks')
    
    def to_dict(self):
        """Converte a tarefa para dicionário (para JSON)"""
        return {
            'id': self.id,
            'day': self.day,
            'task_name': self.task_name,
            'points': self.points,
            'assigned_user_id': self.assigned_user_id,
            'is_completed': self.is_completed,
            'completed_by_user_id': self.completed_by_user_id,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

def init_database(app):
    """Inicializa o banco de dados"""
    db.init_app(app)
    
    with app.app_context():
        # Criar todas as tabelas
        db.create_all()
        
        # Verificar se já existem usuários, se não, criar dados iniciais
        if User.query.count() == 0:
            create_initial_data()

def create_initial_data():
    """Cria dados iniciais no banco"""
    
    # Criar usuários iniciais
    users_data = [
        {'name': 'Igor', 'username': 'igor', 'password': '12345', 'avatar_color': 'bg-sky-500'},
        {'name': 'Beatriz', 'username': 'beatriz', 'password': '12345', 'avatar_color': 'bg-pink-500'},
        {'name': 'Gabriela', 'username': 'gabriela', 'password': '12345', 'avatar_color': 'bg-emerald-500'},
        {'name': 'Salomão', 'username': 'salomao', 'password': '12345', 'avatar_color': 'bg-amber-500'},
        {'name': 'Flavia', 'username': 'flavia', 'password': '12345', 'avatar_color': 'bg-purple-500'},
    ]
    
    users = []
    for user_data in users_data:
        user = User(
            name=user_data['name'],
            username=user_data['username'],
            avatar_color=user_data['avatar_color']
        )
        user.set_password(user_data['password'])
        users.append(user)
        db.session.add(user)
    
    # Commit dos usuários primeiro para obter os IDs
    db.session.commit()
    
    # Sistema de pontuação para gamificação
    task_points = {
        'Lavar a louça': 2,
        'Limpar o fogão': 1,
        'Limpar o chão': 1,
        'Lavar o banheiro': 3,
        'Estender a roupa': 1,
        'Colocar roupa na máquina': 1,
        'Tirar o lixo': 1,
        'Varrer a casa': 2,
    }
    
    # Criar tarefas iniciais - SEMANA COMPLETA
    tasks_data = [
        # Segunda
        {'day': 'Segunda', 'task_name': 'Lavar a louça', 'assigned_to': 1, 'points': task_points['Lavar a louça']},
        {'day': 'Segunda', 'task_name': 'Limpar o fogão', 'assigned_to': 2, 'points': task_points['Limpar o fogão']},
        {'day': 'Segunda', 'task_name': 'Limpar o chão', 'assigned_to': 3, 'points': task_points['Limpar o chão']},
        {'day': 'Segunda', 'task_name': 'Lavar o banheiro', 'assigned_to': 4, 'points': task_points['Lavar o banheiro']},
        {'day': 'Segunda', 'task_name': 'Estender a roupa', 'assigned_to': 5, 'points': task_points['Estender a roupa']},
        {'day': 'Segunda', 'task_name': 'Colocar roupa na máquina', 'assigned_to': 1, 'points': task_points['Colocar roupa na máquina']},
        {'day': 'Segunda', 'task_name': 'Tirar o lixo', 'assigned_to': 2, 'points': task_points['Tirar o lixo']},
        {'day': 'Segunda', 'task_name': 'Varrer a casa', 'assigned_to': 3, 'points': task_points['Varrer a casa']},
        # Terça
        {'day': 'Terça', 'task_name': 'Lavar a louça', 'assigned_to': 2, 'points': task_points['Lavar a louça']},
        {'day': 'Terça', 'task_name': 'Limpar o fogão', 'assigned_to': 3, 'points': task_points['Limpar o fogão']},
        {'day': 'Terça', 'task_name': 'Limpar o chão', 'assigned_to': 4, 'points': task_points['Limpar o chão']},
        {'day': 'Terça', 'task_name': 'Lavar o banheiro', 'assigned_to': 5, 'points': task_points['Lavar o banheiro']},
        {'day': 'Terça', 'task_name': 'Estender a roupa', 'assigned_to': 1, 'points': task_points['Estender a roupa']},
        {'day': 'Terça', 'task_name': 'Colocar roupa na máquina', 'assigned_to': 2, 'points': task_points['Colocar roupa na máquina']},
        {'day': 'Terça', 'task_name': 'Tirar o lixo', 'assigned_to': 3, 'points': task_points['Tirar o lixo']},
        {'day': 'Terça', 'task_name': 'Varrer a casa', 'assigned_to': 4, 'points': task_points['Varrer a casa']},
        # Quarta
        {'day': 'Quarta', 'task_name': 'Lavar a louça', 'assigned_to': 3, 'points': task_points['Lavar a louça']},
        {'day': 'Quarta', 'task_name': 'Limpar o fogão', 'assigned_to': 4, 'points': task_points['Limpar o fogão']},
        {'day': 'Quarta', 'task_name': 'Limpar o chão', 'assigned_to': 5, 'points': task_points['Limpar o chão']},
        {'day': 'Quarta', 'task_name': 'Lavar o banheiro', 'assigned_to': 1, 'points': task_points['Lavar o banheiro']},
        {'day': 'Quarta', 'task_name': 'Estender a roupa', 'assigned_to': 2, 'points': task_points['Estender a roupa']},
        {'day': 'Quarta', 'task_name': 'Colocar roupa na máquina', 'assigned_to': 3, 'points': task_points['Colocar roupa na máquina']},
        {'day': 'Quarta', 'task_name': 'Tirar o lixo', 'assigned_to': 4, 'points': task_points['Tirar o lixo']},
        {'day': 'Quarta', 'task_name': 'Varrer a casa', 'assigned_to': 5, 'points': task_points['Varrer a casa']},
        # Quinta
        {'day': 'Quinta', 'task_name': 'Lavar a louça', 'assigned_to': 4, 'points': task_points['Lavar a louça']},
        {'day': 'Quinta', 'task_name': 'Limpar o fogão', 'assigned_to': 5, 'points': task_points['Limpar o fogão']},
        {'day': 'Quinta', 'task_name': 'Limpar o chão', 'assigned_to': 1, 'points': task_points['Limpar o chão']},
        {'day': 'Quinta', 'task_name': 'Lavar o banheiro', 'assigned_to': 2, 'points': task_points['Lavar o banheiro']},
        {'day': 'Quinta', 'task_name': 'Estender a roupa', 'assigned_to': 3, 'points': task_points['Estender a roupa']},
        {'day': 'Quinta', 'task_name': 'Colocar roupa na máquina', 'assigned_to': 4, 'points': task_points['Colocar roupa na máquina']},
        {'day': 'Quinta', 'task_name': 'Tirar o lixo', 'assigned_to': 5, 'points': task_points['Tirar o lixo']},
        {'day': 'Quinta', 'task_name': 'Varrer a casa', 'assigned_to': 1, 'points': task_points['Varrer a casa']},
        # Sexta
        {'day': 'Sexta', 'task_name': 'Lavar a louça', 'assigned_to': 5, 'points': task_points['Lavar a louça']},
        {'day': 'Sexta', 'task_name': 'Limpar o fogão', 'assigned_to': 1, 'points': task_points['Limpar o fogão']},
        {'day': 'Sexta', 'task_name': 'Limpar o chão', 'assigned_to': 2, 'points': task_points['Limpar o chão']},
        {'day': 'Sexta', 'task_name': 'Lavar o banheiro', 'assigned_to': 3, 'points': task_points['Lavar o banheiro']},
        {'day': 'Sexta', 'task_name': 'Estender a roupa', 'assigned_to': 4, 'points': task_points['Estender a roupa']},
        {'day': 'Sexta', 'task_name': 'Colocar roupa na máquina', 'assigned_to': 5, 'points': task_points['Colocar roupa na máquina']},
        {'day': 'Sexta', 'task_name': 'Tirar o lixo', 'assigned_to': 1, 'points': task_points['Tirar o lixo']},
        {'day': 'Sexta', 'task_name': 'Varrer a casa', 'assigned_to': 2, 'points': task_points['Varrer a casa']},
        # Sábado
        {'day': 'Sábado', 'task_name': 'Lavar a louça', 'assigned_to': 1, 'points': task_points['Lavar a louça']},
        {'day': 'Sábado', 'task_name': 'Limpar o fogão', 'assigned_to': 2, 'points': task_points['Limpar o fogão']},
        {'day': 'Sábado', 'task_name': 'Limpar o chão', 'assigned_to': 3, 'points': task_points['Limpar o chão']},
        {'day': 'Sábado', 'task_name': 'Lavar o banheiro', 'assigned_to': 4, 'points': task_points['Lavar o banheiro']},
        {'day': 'Sábado', 'task_name': 'Estender a roupa', 'assigned_to': 5, 'points': task_points['Estender a roupa']},
        {'day': 'Sábado', 'task_name': 'Colocar roupa na máquina', 'assigned_to': 1, 'points': task_points['Colocar roupa na máquina']},
        {'day': 'Sábado', 'task_name': 'Tirar o lixo', 'assigned_to': 2, 'points': task_points['Tirar o lixo']},
        {'day': 'Sábado', 'task_name': 'Varrer a casa', 'assigned_to': 3, 'points': task_points['Varrer a casa']},
        # Domingo
        {'day': 'Domingo', 'task_name': 'Lavar a louça', 'assigned_to': 2, 'points': task_points['Lavar a louça']},
        {'day': 'Domingo', 'task_name': 'Limpar o fogão', 'assigned_to': 3, 'points': task_points['Limpar o fogão']},
        {'day': 'Domingo', 'task_name': 'Limpar o chão', 'assigned_to': 4, 'points': task_points['Limpar o chão']},
        {'day': 'Domingo', 'task_name': 'Lavar o banheiro', 'assigned_to': 5, 'points': task_points['Lavar o banheiro']},
        {'day': 'Domingo', 'task_name': 'Estender a roupa', 'assigned_to': 1, 'points': task_points['Estender a roupa']},
        {'day': 'Domingo', 'task_name': 'Colocar roupa na máquina', 'assigned_to': 2, 'points': task_points['Colocar roupa na máquina']},
        {'day': 'Domingo', 'task_name': 'Tirar o lixo', 'assigned_to': 3, 'points': task_points['Tirar o lixo']},
        {'day': 'Domingo', 'task_name': 'Varrer a casa', 'assigned_to': 4, 'points': task_points['Varrer a casa']},
    ]
    
    for task_data in tasks_data:
        task = Task(
            day=task_data['day'],
            task_name=task_data['task_name'],
            points=task_data['points'],
            assigned_user_id=task_data['assigned_to']
        )
        db.session.add(task)
    
    # Commit final
    db.session.commit()
    print("✅ Dados iniciais criados com sucesso!")