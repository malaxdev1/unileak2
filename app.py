from flask import Flask, render_template, request, redirect, url_for, flash, make_response, jsonify, send_file, session
import csv
import json
import base64
import os
import hashlib
import random
from datetime import datetime

# Cargar variables de entorno desde .env (solo en desarrollo local)
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = 'univ_medellin_2026_secret'

# Configuración de Upstash Redis REST API
KV_URL = os.environ.get('KV_REST_API_URL', '')
KV_TOKEN = os.environ.get('KV_REST_API_TOKEN', '')

# Debug: Ver si las variables se cargaron
print(f"[DEBUG] KV_URL cargado: {KV_URL[:30] if KV_URL else 'NO ENCONTRADO'}...")
print(f"[DEBUG] KV_TOKEN cargado: {KV_TOKEN[:20] if KV_TOKEN else 'NO ENCONTRADO'}...")

# Inicializar Upstash Redis (REST API)
kv = None
try:
    if KV_URL and KV_TOKEN:
        from upstash_redis import Redis
        kv = Redis(url=KV_URL, token=KV_TOKEN)
        print(f"[OK] Conectado a Upstash Redis exitosamente!")
        # Test de conexión
        try:
            kv.ping()
            print(f"[OK] PING a Redis exitoso!")
        except Exception as ping_error:
            print(f"[WARNING] PING fallo: {ping_error}")
    else:
        print(f"[ERROR] Variables de entorno no encontradas")
        print(f"   KV_URL existe: {bool(KV_URL)}")
        print(f"   KV_TOKEN existe: {bool(KV_TOKEN)}")
except Exception as e:
    print(f"[ERROR] Error conectando a Upstash Redis: {e}")
    kv = None

# Helper functions para CSV (solo lectura - datos base)
def read_csv(filename):
    data = []
    filepath = os.path.join('data', filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
    return data

# Funciones para KV (datos por usuario)
def get_user_data(user_id, key):
    """Obtiene datos específicos de un usuario desde KV"""
    if not kv:
        return None
    try:
        data = kv.get(f"user:{user_id}:{key}")
        return json.loads(data) if data else None
    except:
        return None

def set_user_data(user_id, key, data):
    """Guarda datos específicos de un usuario en KV"""
    if not kv:
        return False
    try:
        kv.set(f"user:{user_id}:{key}", json.dumps(data))
        return True
    except:
        return False

def initialize_user_data(user_id):
    """Inicializa los datos de un nuevo usuario con los valores base del laboratorio"""
    # Cada usuario nuevo empieza con el mismo estado inicial del CTF
    # Criptografía PERDIDA para que la cambien durante el laboratorio
    user_notas = [
        {'estudiante_id': user_id, 'materia': 'Criptografía', 'nota': '2.5', 'estado': 'Reprobado'},
        {'estudiante_id': user_id, 'materia': 'Seguridad de Redes', 'nota': '4.2', 'estado': 'Aprobado'},
        {'estudiante_id': user_id, 'materia': 'Programación Web', 'nota': '3.5', 'estado': 'Aprobado'},
        {'estudiante_id': user_id, 'materia': 'Bases de Datos', 'nota': '4.0', 'estado': 'Aprobado'},
    ]
    
    # Deuda inicial que deben eliminar durante el laboratorio
    user_deuda = {'estudiante_id': user_id, 'monto': '4200000', 'concepto': 'Matrícula 2026-1'}
    
    # Guardar en KV
    set_user_data(user_id, 'notas', user_notas)
    set_user_data(user_id, 'deuda', user_deuda)
    set_user_data(user_id, 'flags', [])
    set_user_data(user_id, 'created_at', datetime.now().isoformat())
    
    return True

def check_user_exists(username):
    """Verifica si un usuario ya está registrado"""
    if not kv:
        return False
    return kv.exists(f"user:{username}:profile")

def register_user(username, password, nombre):
    """Registra un nuevo usuario en KV"""
    if not kv:
        return False
    
    if check_user_exists(username):
        return False
    
    # Crear perfil de usuario
    profile = {
        'username': username,
        'password': password,  # En producción deberías hashear esto
        'nombre': nombre,
        'rol': 'student',
        'created_at': datetime.now().isoformat()
    }
    
    set_user_data(username, 'profile', profile)
    initialize_user_data(username)
    
    return True

def verify_user(username, password):
    """Verifica credenciales de usuario"""
    if not kv:
        return None
    
    profile = get_user_data(username, 'profile')
    if profile and profile.get('password') == password:
        return profile
    
    return None

def get_user_role(request):
    cookie = request.cookies.get('session_data')
    if cookie:
        try:
            user_data = json.loads(cookie)
            return user_data.get('role', 'guest')
        except:
            return 'guest'
    return 'guest'

def get_user_id(request):
    cookie = request.cookies.get('session_data')
    if cookie:
        try:
            user_data = json.loads(cookie)
            return user_data.get('user_id', None)
        except:
            return None
    return None

# ACTO 0 - Registro de usuarios
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    nombre = request.form.get('nombre', '').strip()
    
    if not username or not password or not nombre:
        flash('Todos los campos son requeridos', 'error')
        return redirect(url_for('register_page'))
    
    if not kv:
        flash('El sistema de registro no está disponible. Configura Vercel KV.', 'error')
        return redirect(url_for('register_page'))
    
    if check_user_exists(username):
        flash('El nombre de usuario ya está en uso', 'error')
        return redirect(url_for('register_page'))
    
    if register_user(username, password, nombre):
        flash('¡Registro exitoso! Ya puedes iniciar sesión', 'success')
        return redirect(url_for('index'))
    else:
        flash('Error al registrar usuario', 'error')
        return redirect(url_for('register_page'))

# ACTO 1 - Login
@app.route('/login', methods=['POST'])
def login():
    usuario = request.form.get('usuario')
    clave = request.form.get('clave')
    
    # Primero intentar con usuarios registrados en KV
    if kv:
        profile = verify_user(usuario, clave)
        if profile:
            session_data = json.dumps({
                'user_id': usuario,
                'nombre': profile['nombre'],
                'role': profile['rol']
            })
            
            resp = make_response(redirect(url_for('panel_estudiante')))
            resp.set_cookie('session_data', session_data)
            return resp
    
    # Fallback: usuarios demo del CSV (para compatibilidad)
    users = read_csv('usuarios.csv')
    for user in users:
        if user['documento'] == usuario and user['clave'] == clave:
            # Inicializar datos si no existen
            if kv and not check_user_exists(usuario):
                profile = {
                    'username': usuario,
                    'password': clave,
                    'nombre': user['nombre'],
                    'rol': user['rol'],
                    'created_at': datetime.now().isoformat()
                }
                set_user_data(usuario, 'profile', profile)
                initialize_user_data(usuario)
            
            session_data = json.dumps({
                'user_id': user['documento'],
                'nombre': user['nombre'],
                'role': user['rol']
            })
            
            resp = make_response(redirect(url_for('panel_estudiante')))
            resp.set_cookie('session_data', session_data)
            return resp
    
    flash('Usuario o contraseña incorrectos', 'error')
    return redirect(url_for('index'))

# ACTO 1 & 2 - Panel estudiante
@app.route('/estudiante/panel')
def panel_estudiante():
    user_id = get_user_id(request)
    if not user_id:
        return redirect(url_for('index'))
    
    # Cargar datos base
    materias = read_csv('materias.csv')
    
    # Cargar datos específicos del usuario desde KV
    if kv:
        user_notas = get_user_data(user_id, 'notas') or []
        user_deuda = get_user_data(user_id, 'deuda')
        
        # Si no tiene datos, inicializarlos
        if not user_notas:
            initialize_user_data(user_id)
            user_notas = get_user_data(user_id, 'notas') or []
            user_deuda = get_user_data(user_id, 'deuda')
    else:
        # Fallback sin KV (desarrollo local)
        notas = read_csv('notas.csv')
        deudas = read_csv('deudas.csv')
        user_notas = [n for n in notas if n['estudiante_id'] == user_id]
        user_deuda = next((d for d in deudas if d['estudiante_id'] == user_id), None)
    
    return render_template('panel_estudiante.html', 
                         notas=user_notas, 
                         materias=materias,
                         deuda=user_deuda,
                         user_id=user_id)

# ACTO 2 - Imagen con esteganografía
@app.route('/static/uploads/<filename>')
def get_profile_image(filename):
    return send_file(f'static/uploads/{filename}')

# ACTO 3 - Debug endpoint (filtrado de información)
@app.route('/internal/student-status')
def student_status():
    debug = request.args.get('debug', 'false')
    
    if debug == 'true':
        # FLAG{debug_mode_ruins_everything}
        return jsonify({
            'student_id': get_user_id(request) or '20261001',
            'status': 'active',
            'grade_endpoint': '/api/grades/update',
            'financial_endpoint': '/api/finance/update',
            'monitor_panel': '/monitor/revisions',
            'academic_panel': '/academic/management',
            'note': 'frontend validates role access',
            'flag': 'FLAG{debug_mode_ruins_everything}'
        })
    else:
        return jsonify({'status': 'ok'})

# ACTO 4 - Modificación de notas (sin validación backend)
@app.route('/api/grades/update', methods=['POST'])
def update_grades():
    data = request.get_json()
    student_id = data.get('student_id')
    subject = data.get('subject')
    grade = data.get('grade')
    
    if not student_id or not subject or grade is None:
        return jsonify({'error': 'Faltan parámetros requeridos'}), 400
    
    # Usar directamente el student_id del request (sin validación de autenticación)
    # Cargar notas del usuario desde KV
    if kv:
        user_notas = get_user_data(student_id, 'notas') or []
        
        for nota in user_notas:
            if nota['estudiante_id'] == student_id and nota['materia'] == subject:
                nota['nota'] = str(grade)
                break
        
        set_user_data(student_id, 'notas', user_notas)
    
    # FLAG{client_side_validation_is_fake}
    return jsonify({
        'success': True, 
        'message': 'Nota actualizada correctamente',
        'flag': 'FLAG{client_side_validation_is_fake}'
    })

# ACTO 5 - Panel monitor (escalada de privilegios)
@app.route('/monitor/revisions')
def monitor_panel():
    role = get_user_role(request)
    
    # Sin validación real de rol
    if role in ['monitor', 'coordinator', 'admin']:
        revisiones = read_csv('revisiones.csv')
        return render_template('panel_monitor.html', revisiones=revisiones)
    else:
        return "Acceso denegado. Rol actual: " + role, 403

# ACTO 6 - Verificación de token (Base64 editable)
@app.route('/api/verify-token', methods=['POST'])
def verify_token():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not token:
        return jsonify({'error': 'Token requerido'}), 401
    
    try:
        # Decodificar token Base64 (sin validación criptográfica)
        decoded = base64.b64decode(token).decode('utf-8')
        token_data = json.loads(decoded)
        
        # FLAG{base64_is_a_lie}
        return jsonify({
            'valid': True,
            'role': token_data.get('role'),
            'limited': token_data.get('limited', True),
            'flag': 'FLAG{base64_is_a_lie}'
        })
    except:
        return jsonify({'error': 'Token inválido'}), 401

# ACTO 7 - Panel académico (coordinador)
@app.route('/academic/management')
def academic_panel():
    role = get_user_role(request)
    token = request.cookies.get('access_token')
    
    # Verificar token
    if token:
        try:
            decoded = base64.b64decode(token).decode('utf-8')
            token_data = json.loads(decoded)
            
            if token_data.get('role') == 'coordinator' and not token_data.get('limited', True):
                estudiantes = read_csv('usuarios.csv')
                notas = read_csv('notas.csv')
                deudas = read_csv('deudas.csv')
                
                return render_template('panel_academico.html', 
                                     estudiantes=estudiantes,
                                     notas=notas,
                                     deudas=deudas)
        except:
            pass
    
    return "Acceso denegado. Se requiere token de coordinador.", 403

# ACTO 7 - Modificación masiva de estado académico
@app.route('/api/academic/update', methods=['POST'])
def update_academic():
    data = request.get_json()
    student_id = data.get('student_id')
    subject = data.get('subject')
    new_status = data.get('status')
    
    # Obtener el usuario actual
    current_user_id = get_user_id(request)
    if not current_user_id:
        return jsonify({'error': 'No autorizado'}), 401
    
    # Cargar notas del usuario desde KV
    if kv:
        user_notas = get_user_data(current_user_id, 'notas') or []
        
        for nota in user_notas:
            if nota['estudiante_id'] == current_user_id and nota['materia'] == subject:
                nota['estado'] = new_status
                break
        
        set_user_data(current_user_id, 'notas', user_notas)
    
    # FLAG{grades_are_not_sacred}
    return jsonify({
        'success': True,
        'message': 'Cambios aplicados correctamente',
        'flag': 'FLAG{grades_are_not_sacred}'
    })

# ACTO FINAL - Eliminación de deudas
@app.route('/api/finance/update', methods=['POST'])
def update_finance():
    data = request.get_json()
    student_id = data.get('student_id')
    new_debt = data.get('debt', 0)
    
    if not student_id:
        return jsonify({'error': 'Falta student_id'}), 400
    
    # Usar directamente el student_id del request (sin validación de autenticación)
    # Actualizar deuda del usuario en KV
    if kv:
        user_deuda = get_user_data(student_id, 'deuda') or {}
        user_deuda['monto'] = str(new_debt)
        set_user_data(student_id, 'deuda', user_deuda)
    
    # FLAG financiera; siguiente pista: foto del profesor (metadatos)
    return jsonify({
        'success': True,
        'message': 'Estado financiero actualizado',
        'flag': 'FLAG{this_is_why_universities_get_hacked}',
        'next_step': url_for('secreto_profesor')
    })

# FLAG #8: en metadatos de la foto del profesor (usuario la añade en static/uploads/professor.jpg)
FLAG_METADATA = 'FLAG{metadata_is_not_private}'

# Todas las flags en orden alfabético para SHA1 final
ALL_FLAGS = [
    'FLAG{academic_roles_are_just_strings}',
    'FLAG{base64_is_a_lie}',
    'FLAG{client_side_validation_is_fake}',
    'FLAG{debug_mode_ruins_everything}',
    'FLAG{grades_are_not_sacred}',
    'FLAG{images_should_not_talk}',
    FLAG_METADATA,
    'FLAG{this_is_why_universities_get_hacked}',
]
VAULT_HASH = hashlib.sha1('\n'.join(sorted(ALL_FLAGS)).encode()).hexdigest()

# Ruta de la bóveda: alfanumérico largo para que no se pueda adivinar (solo quien tenga la pista en metadatos la conoce)
BOVEDA_PATH = 'Kp9xL2mN7qR4sT6vW8yZ1bC3dF5gH0jM2nP4rS6uV8wX0zA2'

# Página tras eliminar deuda: narrativa + foto del profesor (metadatos con ruta y flag)
@app.route('/el-secreto-del-profesor')
def secreto_profesor():
    return render_template('secreto_profesor.html')

# Bóveda final: introducir SHA1 de las 8 flags en orden alfabético (siempre pide el hash, no se guarda estado)
@app.route('/' + BOVEDA_PATH + '/boveda', methods=['GET', 'POST'])
def boveda():
    unlocked = False
    youtube_regalo = '#'
    if request.method == 'POST':
        hash_ingresado = (request.form.get('hash') or request.form.get('sha1') or '').strip().lower()
        if hash_ingresado == VAULT_HASH:
            # Solo en esta respuesta mostramos celebración; no guardamos en sesión
            unlocked = True
            YOUTUBE_REGALOS = [
                'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                'https://www.youtube.com/watch?v=EH3nK85MAIU',
                'https://www.youtube.com/watch?v=JlqW11vHLtw',
                'https://youtu.be/PNkhLZlsYjQ?si=jBnoxFNAcjBtiLpx',
                'https://youtu.be/jNhgozo9QJY?si=IZOMfUU5ik1vwo33',
                'https://www.youtube.com/watch?v=N5lTRsuUT5o',
                'https://www.youtube.com/watch?v=h69VanYG0Ds',
                'https://youtu.be/FQAcHm7-SoE?si=sJpPWuhufgPslFPG',
                'https://www.youtube.com/watch?v=AXp7ydbqTrw',
                'https://www.youtube.com/watch?v=tjiN9IYFutU',
                'https://www.youtube.com/watch?v=RUorAzaDftg'
            ]
            youtube_regalo = random.choice(YOUTUBE_REGALOS) if YOUTUBE_REGALOS else '#'
        else:
            flash('Hash incorrecto. Verifica que hayas usado las 8 flags en orden alfabético y el SHA1.', 'error')
            return redirect(url_for('boveda'))
    return render_template('boveda.html', unlocked=unlocked, youtube_regalo=youtube_regalo)

# Rutas auxiliares
@app.route('/cambiar-clave')
def cambiar_clave():
    return render_template('cambiar_clave.html')

@app.route('/olvido-clave')
def olvido_clave():
    return render_template('olvido_clave.html')

@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('session_data', '', expires=0)
    resp.set_cookie('access_token', '', expires=0)
    return resp

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
