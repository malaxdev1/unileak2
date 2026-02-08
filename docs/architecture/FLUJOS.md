# Flujos del Sistema Multi-Usuario

## Flujo de Registro

```
┌─────────────────────────────────────────────────────────────┐
│                   FLUJO DE REGISTRO                          │
└─────────────────────────────────────────────────────────────┘

1. Usuario visita /register
   │
   ├─> Completa formulario:
   │   ├─ Nombre completo
   │   ├─ Username (único)
   │   └─ Password
   │
2. Submit → POST /register
   │
   ├─> Validaciones:
   │   ├─ Campos completos?
   │   ├─ KV disponible?
   │   └─ Username único?
   │
3. Crear usuario en KV
   │
   ├─> user:{username}:profile
   │   └─ {username, password, nombre, rol, created_at}
   │
   ├─> user:{username}:notas
   │   └─ [{materia, nota, estado}, ...]
   │
   ├─> user:{username}:deuda
   │   └─ {estudiante_id, monto, concepto}
   │
   └─> user:{username}:flags
       └─ []
   │
4. Redirect a /login con mensaje de éxito
```

---

## Flujo de Login

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUJO DE LOGIN                            │
└─────────────────────────────────────────────────────────────┘

1. Usuario visita /
   │
2. Ingresa credenciales
   │
   ├─> Usuario: username
   └─> Clave: password
   │
3. Submit → POST /login
   │
   ├─> Verificar en KV primero
   │   │
   │   ├─> user:{username}:profile existe?
   │   │   │
   │   │   ├─ SÍ → Verificar password
   │   │   │   │
   │   │   │   ├─ Correcto → Login exitoso
   │   │   │   └─ Incorrecto → Error
   │   │   │
   │   │   └─ NO → Intentar con CSV
   │   │
   │   └─> Verificar en CSV (usuarios demo)
   │       │
   │       ├─ Encontrado → Migrar a KV → Login
   │       └─ No encontrado → Error
   │
4. Crear sesión
   │
   ├─> Cookie: session_data
   │   └─ {user_id, nombre, role} (JSON)
   │
5. Redirect a /estudiante/panel
```

---

## Flujo de Panel Estudiante

```
┌─────────────────────────────────────────────────────────────┐
│               FLUJO DE PANEL ESTUDIANTE                      │
└─────────────────────────────────────────────────────────────┘

1. Usuario autenticado accede a /estudiante/panel
   │
2. Obtener user_id de sesión
   │
   ├─> Leer cookie: session_data
   └─> Extraer: user_id
   │
3. Cargar datos del usuario desde KV
   │
   ├─> Datos base (compartidos)
   │   └─> read_csv('materias.csv') → Solo lectura
   │
   └─> Datos del usuario (aislados)
       │
       ├─> user:{user_id}:notas
       │   └─ [{materia, nota, estado}, ...]
       │
       └─> user:{user_id}:deuda
           └─ {estudiante_id, monto, concepto}
   │
4. Si no existen datos → initialize_user_data()
   │
5. Renderizar panel con datos específicos del usuario
```

---

## Flujo de Modificación de Notas

```
1. Usuario en panel hace cambio (DevTools/API)
   │
2. POST /api/grades/update
   │
   ├─> Body: {student_id, subject, grade}
   │
3. Validar sesión
   │
   ├─> Obtener current_user_id de cookie
   └─> No autenticado? → 401
   │
4. Cargar notas del usuario desde KV
   │
   ├─> get_user_data(current_user_id, 'notas')
   └─> user:{current_user_id}:notas
   │
5. Modificar solo si estudiante_id == current_user_id
   │
6. Guardar de vuelta en KV
   │
   ├─> set_user_data(current_user_id, 'notas', notas)
   │
7. Retornar flag y éxito
   │
   └─> {success: true, flag: "FLAG{...}"}

Solo afecta los datos del usuario actual.
```

---

## Flujo de Eliminación de Deudas

```
1. Usuario descubre endpoint /api/finance/update
   │
2. POST /api/finance/update
   │
3. Validar sesión → current_user_id
   │
4. Cargar deuda del usuario desde KV
   │
5. Actualizar monto
   │
6. Guardar en KV
   │
7. Retornar flag final

Solo elimina la deuda del usuario actual.
```

---

## Flujo de Aislamiento

```
Usuario A                   Usuario B                   Usuario C
    │                           │                           │
    ├─ Login                    ├─ Login                    ├─ Login
    │                           │                           │
    ├─ KV:user:A:*              ├─ KV:user:B:*              ├─ KV:user:C:*
    │                           │                           │
    ├─ Modifica notas           ├─ Modifica notas           ├─ Modifica notas
    │  └─ Solo en A             │  └─ Solo en B             │  └─ Solo en C
    │                           │                           │
    └─ Captura flags            └─ Captura flags            └─ Captura flags

       NO HAY INTERFERENCIAS ENTRE USUARIOS
       Cada uno tiene su espacio aislado en KV
```

---

## Estructura de Datos en KV

```
KV (Redis)
│
├─ user:alice:profile
│  └─ {"username": "alice", "nombre": "Alice", "rol": "student", ...}
│
├─ user:alice:notas
│  └─ [{"materia": "Criptografía", "nota": "5", ...}, ...]
│
├─ user:alice:deuda
│  └─ {"estudiante_id": "alice", "monto": "4200000", ...}
│
├─ user:alice:flags
│  └─ ["FLAG{...}", ...]
│
├─ user:bob:profile
│  ...
└─ user:bob:notas, deuda, flags

Patrón: user:{username}:{data_type}
```

---

## Comparación: Antes vs Ahora

**Antes (sistema original)**

- Un solo archivo CSV compartido
- Modificaciones sobrescriben a todos
- Sin aislamiento

**Ahora (sistema nuevo)**

- Cada usuario tiene su espacio en KV
- Sin conflictos
- Modificaciones solo afectan al usuario
- Persistencia individual

---

## Puntos Clave

- **Aislamiento**: Cada operación verifica `current_user_id` y solo modifica `user:{current_user_id}:*`.
- **Persistencia**: Datos en Redis (Vercel KV), sobreviven reinicios y redespliegues.
- **Compatibilidad**: Usuarios demo migran automáticamente; funciona sin KV (modo legacy).
- **Escalabilidad**: Múltiples usuarios simultáneos; Redis maneja concurrencia.
