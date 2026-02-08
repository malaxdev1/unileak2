# 🎯 Implementación de Sistema Multi-Usuario con Vercel KV

## 📝 Resumen

Se ha implementado un sistema completo de registro y autenticación que permite a múltiples usuarios interactuar con el laboratorio UniLeak sin interferir entre sí, utilizando Vercel KV (Redis) como almacenamiento persistente.

## ✨ Características Implementadas

### 1. Sistema de Registro
- ✅ Nueva ruta `/register` con formulario de registro
- ✅ Validación de usuarios únicos
- ✅ Creación de perfiles de usuario en KV
- ✅ Interfaz HTML completa (`templates/register.html`)

### 2. Almacenamiento Aislado por Usuario
Cada usuario tiene su propio espacio en KV con las siguientes keys:

```
user:{username}:profile  → Información del usuario (nombre, rol, etc.)
user:{username}:notas    → Notas académicas individuales
user:{username}:deuda    → Estado de deuda financiera
user:{username}:flags    → Flags capturadas (para futuras implementaciones)
```

### 3. Compatibilidad con Datos Base
- Los datos base (materias, usuarios demo) se mantienen en CSV
- Son de **solo lectura** desde el filesystem
- Cada nuevo usuario recibe una copia inicializada de estos datos en su espacio KV

### 4. Endpoints Modificados

Todos los endpoints de modificación ahora trabajan con datos aislados por usuario:

- **`/api/grades/update`** - Modifica notas solo del usuario actual
- **`/api/academic/update`** - Modifica estado académico solo del usuario actual
- **`/api/finance/update`** - Modifica deuda solo del usuario actual

### 5. Autenticación Mejorada

El sistema ahora soporta dos tipos de usuarios:

1. **Usuarios registrados** (en KV)
   - Datos persistentes
   - Progreso individual
   - Sin límite de usuarios*

2. **Usuarios demo** (en CSV)
   - Para demostración o testing
   - Se migran automáticamente a KV al hacer login
   - Mantienen compatibilidad con el sistema anterior

\* *Dentro de los límites del plan de Vercel KV*

## 🏗️ Arquitectura

```
┌─────────────────┐
│   Usuario A     │ → KV: user:A:notas, user:A:deuda
├─────────────────┤
│   Usuario B     │ → KV: user:B:notas, user:B:deuda
├─────────────────┤
│   Usuario C     │ → KV: user:C:notas, user:C:deuda
└─────────────────┘
        ↓
    Aislados entre sí
        ↓
    Sin interferencias
```

### Flujo de Datos

```
1. Registro
   ├─ Validar usuario único
   ├─ Crear profile en KV
   └─ Inicializar datos (notas, deuda)

2. Login
   ├─ Verificar en KV
   ├─ (Fallback: verificar en CSV)
   └─ Crear sesión con cookie

3. Operaciones
   ├─ Obtener user_id de sesión
   ├─ Leer datos de KV (user:{id}:*)
   ├─ Modificar solo datos del usuario
   └─ Guardar en KV (user:{id}:*)
```

## 📦 Archivos Modificados

### Nuevos Archivos
- `templates/register.html` - Formulario de registro
- `vercel.json` - Configuración de Vercel
- `.env.example` - Plantilla de variables de entorno
- `wsgi.py` - Entry point para Vercel
- `SETUP_VERCEL.md` - Guía completa de despliegue
- `IMPLEMENTACION_KV.md` - Este documento

### Archivos Modificados
- `app.py` - Integración completa con KV
- `requirements.txt` - Agregado `redis==5.0.1`
- `templates/login.html` - Enlace a registro

## 🔧 Funciones Principales Agregadas

### `get_user_data(user_id, key)`
Obtiene datos específicos de un usuario desde KV.

```python
notas = get_user_data('user123', 'notas')
# Retorna: [{'materia': 'Criptografía', 'nota': '5', ...}, ...]
```

### `set_user_data(user_id, key, data)`
Guarda datos específicos de un usuario en KV.

```python
set_user_data('user123', 'notas', updated_notas)
# Guarda en: user:user123:notas
```

### `initialize_user_data(user_id)`
Inicializa los datos de un nuevo usuario con valores base.

```python
initialize_user_data('user123')
# Crea: notas base, deuda inicial, flags vacías
```

### `register_user(username, password, nombre)`
Registra un nuevo usuario en el sistema.

```python
if register_user('user123', 'pass123', 'Juan Pérez'):
    # Usuario creado exitosamente
```

### `verify_user(username, password)`
Verifica las credenciales de un usuario.

```python
profile = verify_user('user123', 'pass123')
if profile:
    # Login exitoso
```

## 🔒 Seguridad

### Implementado
- ✅ Aislamiento de datos por usuario
- ✅ Validación de sesión en cada endpoint
- ✅ Variables de entorno para credenciales
- ✅ Usuarios únicos

### Notas de Seguridad
- 🔴 Las contraseñas NO están hasheadas (para simplificar el lab)
- 🔴 La cookie de sesión es JSON plano (vulnerabilidad intencional del lab)
- 🔴 Sin rate limiting en registro/login

**Estas vulnerabilidades son intencionales para mantener el espíritu del CTF.**

## 🚀 Ventajas de Esta Implementación

1. **Sin Base de Datos Tradicional**: Solo Redis/KV
2. **Despliegue Simple**: Todo en Vercel con KV integrado
3. **Escalable**: Soporta múltiples usuarios simultáneos
4. **Aislado**: Cada usuario tiene su sandbox
5. **Gratuito**: Dentro de los límites del free tier
6. **Rápido**: Redis es extremadamente rápido
7. **Mínimos Cambios**: Se mantiene la lógica original del lab

## 📊 Uso de Recursos

### Por Usuario
- **Profile**: ~200 bytes
- **Notas**: ~500 bytes (4 materias)
- **Deuda**: ~100 bytes
- **Flags**: ~200 bytes
- **Total**: ~1 KB por usuario

### Límites del Free Tier
- **Storage**: 256 MB
- **Usuarios posibles**: ~250,000 usuarios teóricos
- **Realista**: 10,000+ usuarios cómodamente

## 🧪 Testing

### Local (sin KV)
```bash
python app.py
```
Funciona con datos CSV (modo legacy).

### Local (con KV)
```bash
# Configurar variables en .env
KV_REST_API_URL=tu_url
KV_REST_API_TOKEN=tu_token

python app.py
```
Funciona con KV real.

### Producción (Vercel)
```bash
vercel --prod
```
KV configurado automáticamente.

## 📚 Próximos Pasos Opcionales

### Mejoras Futuras
- [ ] Hashear contraseñas (bcrypt)
- [ ] Tracking de flags por usuario
- [ ] Leaderboard global
- [ ] Reset de progreso por usuario
- [ ] Panel de administración
- [ ] Rate limiting
- [ ] Logs de actividad por usuario
- [ ] Exportar progreso

### Extensiones
- [ ] Roles adicionales (admin, profesor)
- [ ] Tiempo de completación
- [ ] Hints consumibles
- [ ] Sistema de puntos
- [ ] Certificados al completar

## 🎓 Conclusión

El sistema ahora permite que múltiples usuarios trabajen simultáneamente en el laboratorio UniLeak sin interferir entre sí, manteniendo todo el espíritu del CTF original pero con persistencia y aislamiento real.

Cada usuario tiene su propia "instancia" del laboratorio, puede modificar sus notas y deudas, y progresar a su ritmo sin afectar a otros estudiantes.

---

**Implementado por**: Asistente AI  
**Fecha**: 2026-02-08  
**Stack**: Flask + Vercel + Redis (KV)
