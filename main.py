import functools
import random
from flask import Flask, request, jsonify
import jwt

app = Flask(__name__)
secret_key = "secret"

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.json.get('username')
        password = request.json.get('password')
        
        if not username or not password:
            return jsonify({'message': 'Both username and password are required'}), 400
            
        if username == "admin" and str(password) == "123":
            token = jwt.encode({'username': username}, secret_key, algorithm='HS256')
            return jsonify({'token': token}), 200
        else:
            return jsonify({'message': 'Authentication failed'}), 401
            
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

def verify_token(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization', '')
        if not token:
            return jsonify({'message': 'Token not provided'}), 401
            
        token_parts = token.split(" ")
        if len(token_parts) != 2 or token_parts[0].lower() != 'bearer':
            return jsonify({'message': 'Invalid token format'}), 401
            
        token = token_parts[1]
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            request.username = payload['username']
            return func(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 403
    return wrapper

@app.route('/protected', methods=['GET'])
@verify_token
def protected():
    return jsonify({'message': f'You have access, welcome {request.username}'}), 200

@app.route('/resta', methods=['POST'])
@verify_token
def resta():
    try:
        numero1 = request.json.get('numero1')
        numero2 = request.json.get('numero2')
        
        if numero1 is None or numero2 is None:
            return jsonify({'message': 'Missing numbers'}), 400
            
        resultado = float(numero1) - float(numero2)
        return jsonify({'message': resultado}), 200
    except (ValueError, TypeError):
        return jsonify({'message': 'Invalid numbers provided'}), 400
    
@app.route('/multiplicacion', methods=['POST'])
@verify_token
def multiplicacion():
    try:
        numero1 = request.json.get('numero1')
        numero2 = request.json.get('numero2')
        
        if numero1 is None or numero2 is None:
            return jsonify({'message': 'Missing numbers'}), 400
            
        resultado = float(numero1) * float(numero2)
        return jsonify({'message': resultado}), 200
    except (ValueError, TypeError):
        return jsonify({'message': 'Invalid numbers provided'}), 400

@app.route('/adivinar', methods=['POST'])
@verify_token
def adivinar():
    try:
        intento_usuario = request.json.get('numero')
        
        if intento_usuario is None:
            return jsonify({'message': 'Debes enviar un numero en el campo "numero"'}), 400
        
        intento_usuario = int(intento_usuario)
        
        if intento_usuario < 1 or intento_usuario > 10:
            return jsonify({'message': 'El numero debe estar entre 1 y 10'}), 400
            
        numero_secreto = random.randint(1, 10)
        
        if intento_usuario == numero_secreto:
            return jsonify({
                'ganaste': True,
                'message': f'¡Felicidades! Adivinaste el número secreto ({numero_secreto}).'
            }), 200
        else:
            return jsonify({
                'ganaste': False,
                'message': f'Lo siento, no acertaste. Tu número fue {intento_usuario} y el secreto era {numero_secreto}.'
            }), 200
            
    except (ValueError, TypeError):
        return jsonify({'message': 'Por favor, proporciona un número entero válido'}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
