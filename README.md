# DevFest Bari 2025 - Backend

Backend API per l'evento DevFest Bari 2025, sviluppato con FastAPI e Firebase.

## 🏗️ Architettura del Progetto

Il progetto è strutturato come segue:

```
📦 2025-devfest-bari-be
├── 📁 controllers/          # Logica di business
│   └── users.py            # Logica gestione utenti (esempio)
├── 📁 models/              # Modelli Pydantic
│   └── user.py            # Modello utente (esempio)
├── 📁 routes/              # Router FastAPI
│   └── users.py          # Endpoint utenti (esempio)
├── 📁 secrets/             # Chiavi private
│   └── firebase-keys.json # Chiave privata Firebase (da inserire)
├── app.py                  # Applicazione principale
├── db.py                   # Configurazione Firebase
├── env.py                  # Configurazione ambiente
├── utils.py                # Utilità varie
├── requirements.txt        # Dipendenze Python
├── Dockerfile             # Configurazione Docker
└── compose.yml            # Docker Compose
```

## � Sistema di Router Automatico

Il progetto utilizza un sistema di **caricamento dinamico dei router** che scansiona automaticamente la cartella `routes/`.

### 📋 Requisiti per i File Router

Ogni file nella cartella `routes/` deve rispettare queste regole:

1. **Deve contenere un oggetto `APIRouter`** chiamato esattamente `router` nel contesto globale
2. **Il router verrà automaticamente rilevato e incluso** nell'applicazione all'avvio

### 💡 Esempio di File Router

```python
# routes/example.py
from fastapi import APIRouter

# ✅ OBBLIGATORIO: Il router deve chiamarsi esattamente 'router'
router = APIRouter(prefix="/example", tags=["Example"])

@router.get("/")
async def get_example():
    return {"message": "Hello from example router!"}

@router.post("/create")
async def create_example():
    return {"message": "Example created!"}
```

### ⚠️ Cosa NON fare

```python
# ❌ SBAGLIATO: Nome diverso da 'router'
my_router = APIRouter()  # Non verrà rilevato!

# ❌ SBAGLIATO: Router in una classe o funzione
class MyRoutes:
    router = APIRouter()  # Non è nel contesto globale!

def create_router():
    router = APIRouter()  # Non è nel contesto globale!
    return router
```

### 🔧 Come Funziona

1. All'avvio, `utils.load_routers()` scansiona tutti i file `.py` in `routes/`
2. Per ogni file, cerca un oggetto chiamato `router` di tipo `APIRouter`
3. Se trovato, lo include automaticamente nell'applicazione FastAPI
4. Tutti i router vengono aggiunti al prefix `/api` con autenticazione obbligatoria

## �🔧 Configurazione

### 1. Chiave Privata Firebase

Per far funzionare l'applicazione, devi inserire la chiave privata di Firebase:

1. **Ottieni la chiave privata:**
   - Vai nella [Firebase Console](https://console.firebase.google.com/)
   - Seleziona il tuo progetto
   - Vai su "Impostazioni progetto" > "Account di servizio"
   - Clicca su "Genera nuova chiave privata"
   - Scarica il file JSON

2. **Posiziona la chiave:**
   ```bash
   # Copia il file scaricato nella cartella secrets
   cp /path/to/downloaded/file.json ./secrets/firebase-keys.json
   ```

   **⚠️ IMPORTANTE**: Il file `firebase-keys.json` deve essere posizionato esattamente in `./secrets/firebase-keys.json`

### 2. Variabili d'Ambiente

Puoi configurare l'applicazione tramite variabili d'ambiente:

```bash
export DEBUG=true          # Abilita modalità debug
export NTHREADS=4         # Numero di thread (default: CPU count)
```

Oppure direttamente inline:

```bash
DEBUG=true NTHREADS=4 python3 app.py
```

## 🚀 Avvio con Docker


### Avvio Rapido

1. **Clona il repository:**
   ```bash
   git clone https://github.com/gdgbari/2025-devfest-bari-be.git
   cd 2025-devfest-bari-be
   ```

2. **Configura Firebase:**
   ```bash
   # Posiziona la tua chiave Firebase
   cp /path/to/your/firebase-key.json ./secrets/firebase-keys.json
   ```

3. **Avvia con Docker Compose:**
   ```bash
   docker-compose up --build
   ```

4. **L'applicazione sarà disponibile su:**
   - API: http://localhost:8888
   - Documentazione: http://localhost:8888/api/docs

## 🛠️ Sviluppo Locale

### Prerequisiti
- Python 3.13+
- uv (package manager) o pip

### Setup Ambiente Locale

1. **Installa le dipendenze:**
   ```bash
   # Con uv (consigliato)
   uv pip install -r requirements.txt

   # Con pip
   pip install -r requirements.txt
   ```

2. **Configura Firebase:**
   ```bash
   cp /path/to/your/firebase-key.json ./secrets/firebase-keys.json
   ```

3. **Avvia l'applicazione:**
   ```bash
   # Modalità sviluppo con auto-reload
   DEBUG=true python app.py

   # Modalità produzione
   python app.py
   ```

### Documentazione
- `GET /api/docs` - Swagger UI
- `GET /openapi.json` - Schema OpenAPI

## 🔒 Sicurezza

- Gli endpoint sotto `/api` richiedono autenticazione
- Le chiavi Firebase sono gestite tramite file separati
- CORS abilitato solo in modalità DEBUG

## 🏗️ Tecnologie Utilizzate

- **FastAPI** - Framework web asincrono
- **Firebase Admin SDK** - Database e autenticazione  
- **Uvicorn** - Server ASGI
- **Pydantic** - Validazione dati
- **Docker** - Containerizzazione
