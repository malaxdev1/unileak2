# Guía de Despliegue en Vercel con KV

Esta guía te ayudará a desplegar el laboratorio UniLeak en Vercel con almacenamiento persistente usando Vercel KV (Redis).

## Requisitos Previos

- Cuenta de Vercel (gratuita)
- Cuenta de GitHub (gratuita)
- Repositorio Git con el código del laboratorio

## Paso 1: Preparar el Repositorio

1. Asegúrate de que todos los cambios estén commiteados:

```bash
git add .
git commit -m "Preparar para despliegue en Vercel con KV"
git push origin main
```

## Paso 2: Crear Proyecto en Vercel

1. Ve a [vercel.com](https://vercel.com) e inicia sesión
2. Haz clic en **"Add New Project"**
3. Importa tu repositorio de GitHub
4. Configura el proyecto:
   - **Framework Preset**: Other
   - **Build Command**: (déjalo vacío)
   - **Output Directory**: (déjalo vacío)
   - **Install Command**: `pip install -r requirements.txt`

## Paso 3: Configurar Vercel KV

### 3.1 Crear una Base de Datos KV

1. En el dashboard de tu proyecto en Vercel, ve a la pestaña **"Storage"**
2. Haz clic en **"Create Database"**
3. Selecciona **"KV" (Key-Value Database)**
4. Dale un nombre: `unileak-lab-kv`
5. Selecciona la región más cercana a tu audiencia
6. Haz clic en **"Create"**

### 3.2 Conectar KV al Proyecto

1. Después de crear la base de datos, Vercel te preguntará a qué proyectos conectarla
2. Selecciona tu proyecto `unileak-lab`
3. Haz clic en **"Connect"**

Las variables de entorno `KV_REST_API_URL` y `KV_REST_API_TOKEN` se configurarán automáticamente.

## Paso 4: Verificar Variables de Entorno

1. Ve a tu proyecto en Vercel
2. Ve a **Settings** → **Environment Variables**
3. Deberías ver:
   - `KV_REST_API_URL`
   - `KV_REST_API_TOKEN`
   - `KV_REST_API_READ_ONLY_TOKEN`

Si no están, puedes copiarlas desde la página de tu base de datos KV en la sección Storage.

## Paso 5: Desplegar

1. Vercel desplegará automáticamente tu aplicación
2. Espera a que termine el despliegue (1-2 minutos)
3. Haz clic en **"Visit"** para ver tu aplicación en vivo

## Paso 6: Probar el Sistema

1. Ve a tu URL de Vercel (ej: `https://tu-proyecto.vercel.app`)
2. Haz clic en **"¿No tienes cuenta? Regístrate aquí"**
3. Crea un usuario de prueba
4. Inicia sesión y verifica que todo funcione

## Redeploys Automáticos

Cada vez que hagas push a tu repositorio, Vercel desplegará automáticamente los cambios.

```bash
git add .
git commit -m "Actualización"
git push origin main
```

## Límites del Plan Gratuito

Vercel KV incluye en el plan gratuito:

- **256 MB** de almacenamiento
- **10,000 comandos/día**
- **30 conexiones simultáneas**

Suficiente para un laboratorio con múltiples usuarios.

## Desarrollo Local con KV

Si quieres probar localmente con KV:

1. Copia las variables de entorno desde Vercel:
   - Ve a Settings → Environment Variables
   - Copia `KV_REST_API_URL` y `KV_REST_API_TOKEN`

2. Crea un archivo `.env` (no lo subas a Git):

```bash
KV_REST_API_URL=tu_url_aqui
KV_REST_API_TOKEN=tu_token_aqui
```

3. Instala python-dotenv:

```bash
pip install python-dotenv
```

4. El proyecto ya carga `.env` en `app.py` mediante `load_dotenv()`.

## Seguridad

- Las variables de entorno de KV se manejan automáticamente por Vercel
- Nunca subas credenciales a Git
- El archivo `.env` está en `.gitignore`

## Troubleshooting

### Error: "KV no disponible"

- Verifica que KV esté conectado al proyecto en Vercel
- Revisa que las variables de entorno estén configuradas
- Haz un redeploy desde Vercel

### Usuarios no se guardan

- Verifica en Vercel Dashboard → Storage → tu KV → Data
- Deberías ver las keys `user:username:profile`

### Error en despliegue

- Revisa los logs en Vercel
- Verifica que `requirements.txt` esté completo
- Asegúrate de que `vercel.json` esté en la raíz del repositorio

## Monitorear Uso

1. Ve a Vercel Dashboard → Storage
2. Selecciona tu base de datos KV
3. Ve a **"Monitoring"** para ver:
   - Comandos ejecutados
   - Uso de memoria
   - Conexiones activas

## Características Implementadas

- Registro de usuarios (dentro del storage disponible)
- Aislamiento total entre usuarios
- Persistencia de progreso individual
- Sin interferencias entre estudiantes
- Datos base en CSV (solo lectura)
- Progreso personal en KV (lectura/escritura)

## Soporte

Si tienes problemas:

1. Revisa los logs en Vercel
2. Consulta la documentación de [Vercel KV](https://vercel.com/docs/storage/vercel-kv)
3. Revisa que todas las dependencias estén en `requirements.txt`
