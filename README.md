<div align="center">

# Diablo Translator

**Traduction en temps réel pour Diablo III, Diablo IV et Diablo Immortal**

OCR du chat en direct · Google & DeepL · Détection automatique des langues · Interface style Diablo IV

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green)](https://www.riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

</div>

---

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Jeux supportés](#jeux-supportés)
- [Démarrage rapide](#démarrage-rapide)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Architecture](#architecture)
- [Structure du projet](#structure-du-projet)
- [Développement](#développement)
- [FAQ](#faq)

---

## Fonctionnalités

| Catégorie | Détail |
|-----------|--------|
| **Chat live** | Lecture OCR de la zone chat du jeu (coin inférieur gauche) |
| **Traduction** | Moteurs **Google** et **DeepL** interchangeables |
| **Langues** | Détection automatique de la langue source |
| **Jeux** | Détection en temps réel de D3, D4 et Immortal |
| **Voix** | Entrée micro + lecture vocale optionnelle |
| **Cache** | Traductions persistées sur disque (`cache/translations/`) |
| **Historique** | Grimoire des traductions + export JSON/CSV |
| **Interface** | Thème sombre inspiré de Diablo IV, icône dorée, raccourci bureau |

---

## Jeux supportés

| Jeu | Processus détectés |
|-----|-------------------|
| Diablo III | `Diablo III64.exe`, `Diablo III.exe` |
| Diablo IV | `Diablo IV.exe`, `DiabloIV.exe` |
| Diablo Immortal | `DiabloImmortal.exe` |

---

## Démarrage rapide

```bash
git clone https://github.com/wargriff/diablo_translator.git
cd diablo_translator
pip install -r requirements.txt
python launcher.py
```

---

## Installation

### Prérequis

- **Windows 10/11**
- **Python 3.12+**
- Connexion Internet (traduction + OCR au premier lancement)

### Dépendances

```bash
pip install -r requirements.txt
```

Pour l'entrée vocale (optionnel) :

```bash
pip install pyaudio
```

### DeepL (optionnel, recommandé)

1. Créez une clé API sur [DeepL Pro API](https://www.deepl.com/pro-api)
2. Copiez le fichier d'exemple :

```bash
copy .env.example .env
```

3. Ajoutez votre clé :

```env
DEEPL_API_KEY=votre_cle_ici
```

Ou renseignez-la directement dans **Paramètres → Clé API DeepL**.

---

## Configuration

Les paramètres sont stockés dans `user_data/settings.json`.

| Option | Description | Défaut |
|--------|-------------|--------|
| `language` | Langue cible | `fr` |
| `translator` | `google` ou `deepl` | `google` |
| `chat_monitor_enabled` | Surveillance OCR du chat | `true` |
| `chat_region_preset` | Zone chat : `auto`, `d3`, `d4`, `immortal` | `auto` |
| `auto_detect_language` | Ignorer si déjà dans la langue cible | `true` |
| `speak_translation` | Lecture vocale des traductions | `false` |

---

## Utilisation

### Interface graphique

```bash
python launcher.py
python launcher.py gui
```

**Workflow recommandé :**

1. Lancez **Diablo III, IV ou Immortal**
2. Ouvrez l'onglet **Gameplay**
3. Cliquez **Surveiller chat**
4. Les messages du chat sont traduits automatiquement

### Raccourcis clavier

| Raccourci | Action |
|-----------|--------|
| `Ctrl + Entrée` | Traduire le message saisi |
| `Ctrl + M` | Activer / désactiver le micro |
| `F5` | Actualiser l'état des jeux |

### Ligne de commande

```bash
python launcher.py check                      # Vérifier les dépendances
python launcher.py game                       # État D3 / D4 / Immortal
python launcher.py translate "looking for group"
python launcher.py stats                      # Statistiques
python launcher.py export                     # Export JSON
python launcher.py export --format csv        # Export CSV
python launcher.py test                       # Tests unitaires
```

---

## Architecture

```
launcher.py
    └── bootstrap/          Point d'entrée application
            ├── infrastructure/   Config, DI, cache, assets
            ├── translation/      Providers Google & DeepL
            ├── chat/             Monitoring OCR du chat
            ├── voice/            Entrée/sortie vocale
            ├── game_detection/   Détection D3 · D4 · Immortal
            └── ui/               Interface PyQt6
```

**Couches principales :**

- `domain/` — Modèles et interfaces (contrats)
- `translation/providers/` — Google, DeepL (extensible)
- `cache/` — Cache persistant JSON
- `assets/` — Thèmes, icônes, polices

---

## Structure du projet

```
Diablo_Translator/
├── assets/
│   ├── fonts/          Polices personnalisées
│   ├── icons/          app.svg, app.ico (Windows), generate_app_icon.py
│   └── themes/         Thème diablo_dark.qss
├── build/              Compilation PyInstaller
├── cache/              Cache traductions & OCR
├── models/             Modèles EasyOCR (auto-téléchargés)
├── src/                Code source
├── tests/              Tests unitaires
├── user_data/          Config & historique utilisateur
└── launcher.py         Point d'entrée unique
```

---

## Développement

### Lancer les tests

```bash
python launcher.py test
# ou
python tests/run_tests.py
```

### Compiler un exécutable

```bash
python assets/icons/generate_app_icon.py   # génère app.ico + app.png
python build/build.py
```

L'exécutable est généré dans `build/dist/` avec l'icône Diablo intégrée.

**Raccourci bureau (Windows) :**

```powershell
powershell -ExecutionPolicy Bypass -File build/create_desktop_shortcut.ps1
```

Ou double-cliquez `build/Lancer Diablo Translator.bat`.

---

## FAQ

**Le programme lit-il le chat en direct ?**  
Oui, via **OCR** sur la zone chat affichée à l'écran (pas d'injection mémoire). Placez le chat en bas à gauche comme en jeu.

**DeepL ne fonctionne pas ?**  
Vérifiez `DEEPL_API_KEY` dans `.env` ou les paramètres. Sans clé, Google est utilisé automatiquement.

**Le micro ne répond pas ?**  
Installez `pyaudio` et autorisez l'accès micro dans Windows.

**Les modèles OCR sont lents au premier lancement ?**  
Normal : EasyOCR télécharge les modèles dans `models/` une seule fois.

---

## Avertissement

Ce projet est un outil communautaire **non affilié** à Blizzard Entertainment.  
Utilisez-le conformément aux conditions d'utilisation de vos jeux.

---

<div align="center">

**Diablo Translator** — traduire le chat, jouer sans barrière de langue.

</div>
