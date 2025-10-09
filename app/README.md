# DevFest Bari 2025 - User Management API

API per la gestione degli utenti utilizzando Firebase Auth e Firestore.

## Struttura del Progetto

```
/app
├── core/                   # Configurazioni core
│   ├── config.py          # Configurazioni dell'applicazione
│   ├── firebase_auth.py   # Client Firebase Auth
│   └── firestore.py       # Client Firestore
├── models/                # Modelli di dati
│   └── user.py           # Modello User
├── repositories/          # Repository per accesso ai dati
│   └── users_repository.py # Repository per operazioni Firestore
├── routers/              # Router FastAPI
│   └── users.py          # Endpoint per gestione utenti
├── services/             # Logica di business
│   └── user_service.py   # Service per gestione utenti
├── secrets/              # File di configurazione sensibili
│   └── service_account_key.json # Chiave di servizio Firebase
├── utils/                # Utilità
│   └── include_routers.py # Configurazione router
├── main.py               # Applicazione FastAPI principale
└── requirements.txt      # Dipendenze Python
```

## Configurazione

### 1. Installazione Dipendenze

```bash
pip install -r requirements.txt
```

### 2. Configurazione Firebase

1. Crea un progetto Firebase su [Firebase Console](https://console.firebase.google.com/)
2. Abilita Authentication e Firestore
3. Genera una chiave di servizio e salvala in `/app/secrets/service_account_key.json`
4. Configura le regole di sicurezza Firestore se necessario

### 3. Variabili d'Ambiente (Opzionale)

Crea un file `.env` nella root del progetto:

```env
FIREBASE_SERVICE_ACCOUNT_PATH=/app/secrets/service_account_key.json
FIREBASE_PROJECT_ID=your-project-id
API_ROOT_PATH=/api
```

## API Endpoints

Base URL: `http://localhost:8000/api`

### 1. Creare un Utente

**POST** `/users`

```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "Mario",
  "surname": "Rossi",
  "nickname": "mario_rossi",
  "role": "user"
}
```

**Risposta:**
```json
{
  "uid": "firebase-uid",
  "email": "user@example.com",
  "email_verified": false,
  "disabled": false,
  "created_at": "2024-01-01T00:00:00",
  "firestore_data": {
    "email": "user@example.com"
  }
}
```

### 2. Ottenere Tutti gli Utenti

**GET** `/users`

**Risposta:**
```json
{
  "users": [
    {
      "uid": "firebase-uid",
      "email": "user@example.com",
      "email_verified": false,
      "disabled": false,
      "created_at": "2024-01-01T00:00:00",
      "firestore_data": {
        "email": "user@example.com",
        "name": "Mario",
        "surname": "Rossi",
        "nickname": "mario_rossi",
        "role": "user",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
        "is_active": true
      }
    }
  ],
  "total": 1
}
```

### 3. Ottenere un Utente per UID

**GET** `/users/{uid}`

**Risposta:**
```json
{
  "uid": "firebase-uid",
  "email": "user@example.com",
  "email_verified": false,
  "disabled": false,
  "created_at": "2024-01-01T00:00:00",
  "firestore_data": {
    "email": "user@example.com",
    "name": "Mario",
    "surname": "Rossi",
    "nickname": "mario_rossi",
    "role": "user",
  }
}
```

### 4. Aggiornare un Utente

**PUT** `/users/{uid}`

```json
{
  "email": "newemail@example.com",
  "name": "Luigi",
  "surname": "Verdi",
  "nickname": "luigi_verdi",
  "role": "admin",
  "password": "nuovapassword123"
}
```

**Risposta:**
```json
{
  "uid": "firebase-uid",
  "email": "newemail@example.com",
  "email_verified": false,
  "disabled": false,
  "created_at": "2024-01-01T00:00:00",
  "firestore_data": {
    "email": "newemail@example.com",
    "name": "Luigi",
    "surname": "Verdi",
    "nickname": "luigi_verdi",
    "role": "admin",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T01:00:00",
    "is_active": true
  }
}
```

### 5. Eliminare un Utente

**DELETE** `/users/{uid}`

**Risposta:** 204 No Content

### 6. Eliminare Tutti gli Utenti

**DELETE** `/users`

**Risposta:** 204 No Content

⚠️ **Attenzione:** Questo endpoint elimina tutti gli utenti. Usare con cautela!

## Avvio dell'Applicazione

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

L'API sarà disponibile su: `http://localhost:8000/api`

## Documentazione Interattiva

- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

## Architettura

### Firebase Auth
- Gestisce l'autenticazione degli utenti
- Memorizza email, password
- Genera UID univoci per ogni utente

### Firestore
- Memorizza dati aggiuntivi degli utenti nella collection `users`
- Ogni documento ha come ID l'UID di Firebase Auth
- Contiene: email, name, surname, nickname, role

### Pattern Architetturale
- **Router**: Gestisce le richieste HTTP e la validazione
- **Service**: Contiene la logica di business
- **Repository**: Gestisce l'accesso ai dati Firestore
- **Models**: Modelli Pydantic per validazione e serializzazione dei dati

## Gestione Errori

L'API restituisce codici di stato HTTP appropriati:

- `200`: Successo
- `201`: Creato con successo
- `204`: Eliminato con successo
- `400`: Richiesta non valida
- `404`: Utente non trovato
- `409`: Utente già esistente
- `500`: Errore interno del server

## Sicurezza

- Le password vengono gestite da Firebase Auth
- La chiave di servizio Firebase deve essere protetta
- Configurare le regole di sicurezza Firestore appropriatamente
- Utilizzare HTTPS in produzione
