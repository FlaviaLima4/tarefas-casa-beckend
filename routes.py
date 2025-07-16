from flask import Blueprint, request, jsonify
from datetime import datetime
from database import db, User, Task

# Criar blueprint para as rotas
api = Blueprint('api', __name__)

# --- ROTAS DE AUTENTICAÇÃO ---

@api.route('/login', methods=['POST'])
def login():
    """Endpoint para login do usuário"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username e password são obrigatórios'}), 400
        
        username = data['username'].lower().strip()
        password = data['password']
        
        # Buscar usuário
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            return jsonify({
                'success': True,
                'message': 'Login realizado com sucesso',
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Credenciais inválidas'}), 401
            
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

# --- ROTAS DE USUÁRIOS ---

@api.route('/users', methods=['GET'])
def get_users():
    """Retorna todos os usuários"""
    try:
        users = User.query.all()
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar usuários: {str(e)}'}), 500

@api.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Retorna um usuário específico"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar usuário: {str(e)}'}), 500

# --- ROTAS DE TAREFAS ---

@api.route('/tasks', methods=['GET'])
def get_tasks():
    """Retorna todas as tarefas ou filtradas por dia"""
    try:
        day = request.args.get('day')  # Parâmetro opcional para filtrar por dia
        
        if day:
            tasks = Task.query.filter_by(day=day).all()
        else:
            tasks = Task.query.all()
        
        return jsonify({
            'tasks': [task.to_dict() for task in tasks]
        }), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar tarefas: {str(e)}'}), 500

@api.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Retorna uma tarefa específica"""
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Tarefa não encontrada'}), 404
        
        return jsonify({'task': task.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar tarefa: {str(e)}'}), 500

@api.route('/tasks/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    """Marca/desmarca uma tarefa como concluída"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id é obrigatório'}), 400
        
        # Verificar se o usuário existe
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Buscar a tarefa
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Tarefa não encontrada'}), 404
        
        # Toggle da tarefa
        if task.is_completed:
            # Desmarcar como concluída
            task.is_completed = False
            task.completed_by_user_id = None
            task.completed_at = None
            message = 'Tarefa desmarcada como concluída'
        else:
            # Marcar como concluída
            task.is_completed = True
            task.completed_by_user_id = user_id
            task.completed_at = datetime.utcnow()
            message = 'Tarefa marcada como concluída'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message,
            'task': task.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao atualizar tarefa: {str(e)}'}), 500

@api.route('/tasks', methods=['POST'])
def create_task():
    """Cria uma nova tarefa"""
    try:
        data = request.get_json()
        
        required_fields = ['day', 'task_name', 'assigned_user_id']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({'error': f'{field} é obrigatório'}), 400
        
        # Verificar se o usuário existe
        user = User.query.get(data['assigned_user_id'])
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Criar nova tarefa
        task = Task(
            day=data['day'],
            task_name=data['task_name'],
            assigned_user_id=data['assigned_user_id']
        )
        
        db.session.add(task)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tarefa criada com sucesso',
            'task': task.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao criar tarefa: {str(e)}'}), 500

@api.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Atualiza uma tarefa existente"""
    try:
        data = request.get_json()
        
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Tarefa não encontrada'}), 404
        
        # Atualizar campos se fornecidos
        if 'day' in data:
            task.day = data['day']
        if 'task_name' in data:
            task.task_name = data['task_name']
        if 'assigned_user_id' in data:
            # Verificar se o usuário existe
            user = User.query.get(data['assigned_user_id'])
            if not user:
                return jsonify({'error': 'Usuário não encontrado'}), 404
            task.assigned_user_id = data['assigned_user_id']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tarefa atualizada com sucesso',
            'task': task.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao atualizar tarefa: {str(e)}'}), 500

@api.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Deleta uma tarefa"""
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Tarefa não encontrada'}), 404
        
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tarefa deletada com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao deletar tarefa: {str(e)}'}), 500

# --- ROTAS DE ESTATÍSTICAS ---

@api.route('/ranking', methods=['GET'])
def get_ranking():
    """Retorna o ranking de usuários por pontuação"""
    try:
        # Buscar todas as tarefas concluídas
        completed_tasks = Task.query.filter_by(is_completed=True).all()
        
        # Calcular pontos por usuário
        user_points = {}
        user_tasks_count = {}
        
        for task in completed_tasks:
            completed_by_id = task.completed_by_user_id
            if completed_by_id:
                user_points[completed_by_id] = user_points.get(completed_by_id, 0) + task.points
                user_tasks_count[completed_by_id] = user_tasks_count.get(completed_by_id, 0) + 1
        
        # Buscar dados dos usuários e criar ranking
        users = User.query.all()
        ranking = []
        
        for user in users:
            points = user_points.get(user.id, 0)
            tasks_completed = user_tasks_count.get(user.id, 0)
            
            ranking.append({
                'user_id': user.id,
                'name': user.name,
                'username': user.username,
                'avatar_color': user.avatar_color,
                'points': points,
                'tasks_completed': tasks_completed
            })
        
        # Ordenar por pontos (decrescente)
        ranking.sort(key=lambda x: x['points'], reverse=True)
        
        # Adicionar posição no ranking
        for i, user_rank in enumerate(ranking):
            user_rank['position'] = i + 1
        
        return jsonify({
            'ranking': ranking,
            'total_users': len(ranking)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar ranking: {str(e)}'}), 500

@api.route('/stats', methods=['GET'])
def get_stats():
    """Retorna estatísticas gerais"""
    try:
        total_tasks = Task.query.count()
        completed_tasks = Task.query.filter_by(is_completed=True).count()
        total_users = User.query.count()
        
        # Estatísticas por dia
        days = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        stats_by_day = {}
        
        for day in days:
            day_tasks = Task.query.filter_by(day=day).count()
            day_completed = Task.query.filter_by(day=day, is_completed=True).count()
            stats_by_day[day] = {
                'total': day_tasks,
                'completed': day_completed,
                'progress': (day_completed / day_tasks * 100) if day_tasks > 0 else 0
            }
        
        return jsonify({
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'total_users': total_users,
            'overall_progress': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'stats_by_day': stats_by_day
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar estatísticas: {str(e)}'}), 500

# --- ROTA DE SAÚDE ---

@api.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se a API está funcionando"""
    return jsonify({
        'status': 'OK',
        'message': 'API do Lar Doce App funcionando!',
        'timestamp': datetime.utcnow().isoformat()
    }), 200