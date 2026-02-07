from flask import Flask, render_template, request, redirect, url_for, flash, make_response, jsonify, send_file, session
import csv
import json
import base64
import os
import hashlib
import random

app = Flask(__name__)
app.secret_key = 'univ_medellin_2026_secret'

# Helper functions para CSV
def read_csv(filename):
    data = []
    filepath = os.path.join('data', filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
    return data

def write_csv(filename, data, fieldnames):
    filepath = os.path.join('data', filename)
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

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

# ACTO 1 - Login inicial
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form.get('usuario')
    clave = request.form.get('clave')
    
    # Validación básica (insegura a propósito)
    users = read_csv('usuarios.csv')
    
    for user in users:
        if user['documento'] == usuario and user['clave'] == clave:
            # Crear cookie de sesión (JSON en texto plano)
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
    
    # Cargar datos del estudiante
    notas = read_csv('notas.csv')
    materias = read_csv('materias.csv')
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
    
    # Sin validación de permisos ni de lógica de negocio
    notas = read_csv('notas.csv')
    
    for nota in notas:
        if nota['estudiante_id'] == student_id and nota['materia'] == subject:
            nota['nota'] = str(grade)
            break
    
    write_csv('notas.csv', notas, ['estudiante_id', 'materia', 'nota', 'estado'])
    
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
    
    # Sin validaciones
    notas = read_csv('notas.csv')
    
    for nota in notas:
        if nota['estudiante_id'] == student_id and nota['materia'] == subject:
            nota['estado'] = new_status
            break
    
    write_csv('notas.csv', notas, ['estudiante_id', 'materia', 'nota', 'estado'])
    
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
    
    # Sin validaciones ni auditoría
    deudas = read_csv('deudas.csv')
    
    for deuda in deudas:
        if deuda['estudiante_id'] == student_id:
            deuda['monto'] = str(new_debt)
            break
    
    write_csv('deudas.csv', deudas, ['estudiante_id', 'monto', 'concepto'])
    
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

# Página tras eliminar deuda: narrativa + foto del profesor (metadatos con ruta y flag)
@app.route('/el-secreto-del-profesor')
def secreto_profesor():
    return render_template('secreto_profesor.html')

# Bóveda final: introducir SHA1 de las 8 flags en orden alfabético
@app.route('/boveda', methods=['GET', 'POST'])
def boveda():
    if request.method == 'POST':
        hash_ingresado = (request.form.get('hash') or request.form.get('sha1') or '').strip().lower()
        if hash_ingresado == VAULT_HASH:
            session['vault_unlocked'] = True
            return redirect(url_for('boveda'))
        flash('Hash incorrecto. Verifica que hayas usado las 8 flags en orden alfabético y el SHA1.', 'error')
        return redirect(url_for('boveda'))
    unlocked = session.get('vault_unlocked', False)
    # Lista de enlaces de YouTube para el regalo; el botón elige uno al azar
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
    session.pop('vault_unlocked', None)
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('session_data', '', expires=0)
    resp.set_cookie('access_token', '', expires=0)
    return resp

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
