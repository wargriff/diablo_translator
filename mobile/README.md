# Diablo Translator — Mobile (Flutter)

Companion iPhone / Android pour consulter l'historique et composer des réponses traduites via l'API FastAPI du PC.

## Prérequis

- Flutter SDK (`C:\src\flutter` ou dans le PATH)
- **iPhone** : un Mac avec Xcode pour compiler et installer sur l'appareil
- **Android** : émulateur ou téléphone USB (testable depuis Windows)

## 1. Lancer l'API sur le PC

```powershell
cd "C:\Users\wargriff\Pycharm_Project_v 3.12\Diablo_Translator"
py -3 launcher.py server
```

L'API écoute sur `0.0.0.0:8000`. Notez l'IP locale du PC (ex. `192.168.1.42`) :

```powershell
ipconfig
```

## 2. Configurer l'app

Dans l'onglet **Réglages**, entrez :

```
http://192.168.1.42:8000
```

(iPhone et PC sur le **même Wi‑Fi** — `127.0.0.1` ne fonctionne pas depuis le téléphone.)

## 3. Lancer l'app

Via le launcher :

```powershell
py -3 launcher.py mobile
```

Ou directement :

```powershell
cd mobile
flutter pub get
flutter run
```

## 4. Build iPhone (sur Mac)

```bash
cd mobile
flutter pub get
flutter build ios
# ou flutter run -d <id-iphone>
```

`ios/Runner/Info.plist` autorise déjà le HTTP local (`NSAllowsLocalNetworking`).

## Fonctions

| Onglet | Description |
|--------|-------------|
| **Live** | Historique des traductions (API `/api/v1/messages`) |
| **Reply** | Composer, aperçu traduit, réponses rapides, copier |
| **Réglages** | URL API + test de connexion |

## Architecture

```
iPhone (Flutter) ──HTTP──► PC FastAPI (:8000) ──► pipeline src/ + SQLite
```

L'OCR reste sur le desktop PyQt6 ; le mobile est un companion distant.
