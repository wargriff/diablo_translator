# Changelog

Toutes les modifications notables de **Diablo Translator** sont documentées ici.

Format basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).

## [2.1.1] — 2026-06-09

### Corrigé

- **Web companion** : détection Node.js dans `C:\src`, `DT_NODE_HOME` et emplacements Windows courants.
- **Web companion** : `npm install` automatique au premier lancement si `web/node_modules` absent.
- **API** : vérification santé Diablo (`status: ok`) au lieu d’un simple HTTP 200 sur le port 8000.
- **API** : libération du port 8000 si occupé par un autre programme.
- **Hub** : badges API/Web basés sur la vraie réponse de l’API Diablo.
- **Installation** : `backend/requirements.txt` inclus dans `build/install_dependencies.py`.

### Ajouté

- Lanceur unique `START.bat` (gui, hub, web, build).
- `Build-Pro.bat` à la racine pour construire `DiabloTranslator.exe`.
- Modules `launcher/nodejs.py` et `launcher/api_probe.py`.
- CI GitHub Actions (vérification dépendances + tests).

### Changé

- Commande par défaut : `gui` au lieu de `menu`.
- Spec PyInstaller allégée (desktop uniquement).

## [2.1.0] — versions antérieures

Voir l’historique Git pour Hub Sanctuaire, Live web et plateforme unifiée.

[2.1.1]: https://github.com/wargriff/diablo_translator/compare/de2a2ff...main
