from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración de base de datos
DATABASE_URL = os.environ.get('DATABASE_URL') #or \
#    'postgresql://todouser:tu_password_segura@localhost/todolist_db'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Modelo de datos
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Rutas de la API REST

@app.route('/api/todos', methods=['GET'])
def get_todos():
    """Obtener todas las tareas"""
    todos = Todo.query.all()
    return jsonify([todo.to_dict() for todo in todos])

@app.route('/api/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """Obtener una tarea específica"""
    todo = Todo.query.get_or_404(todo_id)
    return jsonify(todo.to_dict())

@app.route('/api/todos', methods=['POST'])
def create_todo():
    """Crear nueva tarea"""
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    todo = Todo(
        title=data['title'],
        description=data.get('description', ''),
        completed=data.get('completed', False)
    )
    
    try:
        db.session.add(todo)
        db.session.commit()
        return jsonify(todo.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Actualizar tarea existente"""
    todo = Todo.query.get_or_404(todo_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Actualizar campos si están presentes
    if 'title' in data:
        todo.title = data['title']
    if 'description' in data:
        todo.description = data['description']
    if 'completed' in data:
        todo.completed = data['completed']
    
    todo.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify(todo.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Eliminar tarea"""
    todo = Todo.query.get_or_404(todo_id)
    
    try:
        db.session.delete(todo)
        db.session.commit()
        return jsonify({'message': 'Todo deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/todos/completed', methods=['GET'])
def get_completed_todos():
    """Obtener tareas completadas"""
    todos = Todo.query.filter_by(completed=True).all()
    return jsonify([todo.to_dict() for todo in todos])

@app.route('/api/todos/pending', methods=['GET'])
def get_pending_todos():
    """Obtener tareas pendientes"""
    todos = Todo.query.filter_by(completed=False).all()
    return jsonify([todo.to_dict() for todo in todos])

# Ruta para verificar estado de la API
@app.route('/api/health', methods=['GET'])
def health_check():
    """Verificar estado de la API"""
    return jsonify({
        'status': 'healthy',
        'message': 'Todo API is running',
        'timestamp': datetime.utcnow().isoformat()
    })

# Manejo de errores
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)