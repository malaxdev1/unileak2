# Implementación de Sistema Multi-Usuario con Vercel KV

## Resumen

Sistema de registro y autenticación que permite a múltiples usuarios usar el laboratorio UniLeak sin interferir entre sí, utilizando Vercel KV (Redis) como almacenamiento persistente.

## Características Implementadas

### 1. Sistema de Registro

- Ruta `/register` con formulario de registro
- Validación de usuarios únicos
- Creación de perfiles de usuario en KV
- Interfaz HTML en `templates/register.html`

### 2. Almacenamiento Aislado por Usuario

Cada usuario tiene su propio espacio en KV:

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

Todos los endpoints de modificación trabajan con datos aislados por usuario:

- **`/api/grades/update`** – Modifica notas solo del usuario actual
- **`/api/academic/update`** – Modifica estado académico solo del usuario actual
- **`/api/finance/update`** – Modifica deuda solo del usuario actual

### 5. Autenticación

El sistema soporta dos tipos de usuarios:

1. **Usuarios registrados** (en KV): datos persistentes, progreso individual.
2. **Usuarios demo** (en CSV): se migran automáticamente a KV al hacer login.

Dentro de los límites del plan de Vercel KV.

## Arquitectura

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

## Archivos Relevantes

### Nuevos o de configuración

- `templates/register.html` – Formulario de registro
- `vercel.json` – Configuración de Vercel
- `.env.example` – Plantilla de variables de entorno
- `wsgi.py` – Entry point para Vercel

### Modificados

- `app.py` – Integración con KV
- `requirements.txt` – Inclusión de dependencias Redis/KV
- `templates/login.html` – Enlace a registro

## Funciones Principales

### `get_user_data(user_id, key)`

Obtiene datos específicos de un usuario desde KV.

```python
notas = get_user_data('user123', 'notas')
```

### `set_user_data(user_id, key, data)`

Guarda datos específicos de un usuario en KV.

```python
set_user_data('user123', 'notas', updated_notas)
```

### `initialize_user_data(user_id)`

Inicializa los datos de un nuevo usuario con valores base (notas, deuda, flags).

### `register_user(username, password, nombre)`

Registra un nuevo usuario en el sistema.

### `verify_user(username, password)`

Verifica credenciales (KV y fallback CSV).

## Seguridad

### Implementado

- Aislamiento de datos por usuario
- Validación de sesión en cada endpoint
- Variables de entorno para credenciales
- Usuarios únicos

### Notas (vulnerabilidades intencionales del lab)

- Las contraseñas no están hasheadas (simplificación del lab)
- La cookie de sesión es JSON plano
- Sin rate limiting en registro/login

Estas vulnerabilidades son intencionales para el espíritu del CTF.

## Uso de Recursos

### Por Usuario

- Profile: ~200 bytes
- Notas: ~500 bytes (4 materias)
- Deuda: ~100 bytes
- Flags: ~200 bytes
- Total: ~1 KB por usuario

### Límites del Free Tier

- Storage: 256 MB
- Uso realista: miles de usuarios cómodamente

## Testing

### Local sin KV

```bash
python app.py
```

Funciona con datos CSV (modo legacy).

### Local con KV

Configurar `KV_REST_API_URL` y `KV_REST_API_TOKEN` en `.env` y ejecutar `python app.py`.

### Producción (Vercel)

KV se configura automáticamente al conectar la base de datos al proyecto.
