# ⚡ Inicio Rápido - UniLeak Lab con Multi-Usuario

## 🎯 Despliegue Rápido en Vercel (5 minutos)

### Paso 1: Subir a GitHub
```bash
git add .
git commit -m "Sistema multi-usuario con Vercel KV"
git push origin main
```

### Paso 2: Importar en Vercel
1. Ve a [vercel.com/new](https://vercel.com/new)
2. Importa tu repositorio
3. Haz clic en **Deploy**

### Paso 3: Agregar Vercel KV
1. En tu proyecto Vercel, ve a **Storage**
2. Clic en **Create Database** → **KV**
3. Nómbrala `unileak-lab-kv`
4. Clic en **Create & Connect**

### Paso 4: ¡Listo!
1. Espera el redeploy automático (~1 min)
2. Visita tu URL: `https://tu-proyecto.vercel.app`
3. Clic en **"¿No tienes cuenta? Regístrate aquí"**
4. Crea tu usuario y comienza

---

## 🖥️ Prueba Local (Opcional)

### Sin KV (modo legacy)
```bash
pip install -r requirements.txt
python app.py
```
Funciona con CSV (sin persistencia entre sesiones).

### Con KV (modo real)
1. Obtén las credenciales de Vercel:
   - Vercel Dashboard → Storage → tu KV → .env.local
   
2. Crea `.env` con:
```bash
KV_REST_API_URL=tu_url_aqui
KV_REST_API_TOKEN=tu_token_aqui
```

3. Instala dependencia adicional:
```bash
pip install python-dotenv
```

4. Agrega al inicio de `app.py` (línea 1):
```python
from dotenv import load_dotenv
load_dotenv()
```

5. Ejecuta:
```bash
python app.py
```

---

## ✅ Verificar Funcionamiento

### Test 1: Registro
- [ ] Ve a `/register`
- [ ] Crea usuario: `testuser1` / `pass123` / `Test User`
- [ ] Debería redirigir a login con mensaje de éxito

### Test 2: Login
- [ ] Inicia sesión con `testuser1` / `pass123`
- [ ] Debería mostrar panel de estudiante

### Test 3: Aislamiento
- [ ] Modifica notas de `testuser1`
- [ ] Cierra sesión
- [ ] Crea `testuser2`
- [ ] Verifica que tiene notas originales (no las modificadas)

### Test 4: Persistencia
- [ ] Modifica algo como `testuser1`
- [ ] Cierra sesión
- [ ] Inicia sesión de nuevo como `testuser1`
- [ ] Verifica que los cambios persisten

---

## 🐛 Solución de Problemas

### "El sistema de registro no está disponible"
→ KV no está configurado. Sigue el Paso 3 de arriba.

### "Usuario o contraseña incorrectos" después de registrar
→ Espera 10 segundos (propagación de KV) e intenta de nuevo.

### Los cambios no persisten
→ Verifica que KV esté conectado en Vercel Storage.

### Error 500 en producción
→ Ve a Vercel Dashboard → tu proyecto → Functions → Logs

---

## 📚 Más Información

- **Guía completa**: Ver `SETUP_VERCEL.md`
- **Detalles técnicos**: Ver `IMPLEMENTACION_KV.md`
- **Documentación Vercel KV**: [vercel.com/docs/storage/vercel-kv](https://vercel.com/docs/storage/vercel-kv)

---

**¿Problemas?** Revisa los logs en Vercel Dashboard → Functions → Logs
