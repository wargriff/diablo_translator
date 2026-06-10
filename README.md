<div align="center">

# Diablo Translator

**Traduisez le chat Diablo en temps réel — sans barrière de langue en multijoueur**

Application Windows avec OCR du chat en direct, traduction Google & DeepL, interface PyQt6 style Diablo IV, companion web et exécutable portable.

[![Version](https://img.shields.io/badge/version-2.1.1-gold?style=flat-square)](#)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green?style=flat-square)](https://www.riverbankcomputing.com/software/pyqt/)
[![Next.js](https://img.shields.io/badge/Web-Next.js-black?style=flat-square&logo=next.js)](web/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

[Installation](#installation) · [Démarrage rapide](#démarrage-rapide) · [Companion web](#companion-web-optionnel) · [FAQ](#faq) · [Changelog](CHANGELOG.md)

</div>

---

## Présentation

**Diablo Translator** lit le chat affiché à l'écran (OCR, sans injection mémoire), détecte la langue et traduit automatiquement les messages des autres joueurs. Idéal pour jouer à **Diablo III**, **Diablo IV** ou **Diablo Immortal** avec des coéquipiers internationaux.

| Mode | Usage | Commande |
|------|--------|----------|
| **Centre de contrôle** (défaut) | Lance OCR, API, Web, build | `START.bat` ou `Lancer.bat` |
| **Desktop OCR** | Overlay en jeu | `START.bat gui` ou bouton dans le centre |
| **Web companion** | Historique, stats, live | Bouton **Plateforme API+Web** → http://127.0.0.1:3000 |

> Mises à jour et correctifs publiés régulièrement — suivez les [releases](https://github.com/wargriff/diablo_translator/releases) et le [CHANGELOG](CHANGELOG.md).

---

## Fonctionnalités

| Catégorie | Détail |
|-----------|--------|
| **Chat live** | OCR de la zone chat (coin inférieur gauche), surveillance automatique |
| **Traduction** | **Google** et **DeepL**, mode bidirectionnel (chat → FR, vos réponses → langue du joueur) |
| **Langues** | Détection automatique · expressions mixtes conservées (« yo la team ») |
| **Jeux** | Détection en temps réel D3, D4 et Immortal |
| **Voix** | Entrée micro + lecture vocale (optionnel) |
| **Historique** | Grimoire des traductions, export JSON/CSV |
| **Cache** | Traductions persistées (`cache/translations/`) |
| **Interface** | Thème sombre Diablo IV, icône dorée, raccourci bureau |

---

## Jeux supportés

| Jeu | Processus détectés |
|-----|-------------------|
| Diablo III | `Diablo III64.exe`, `Diablo III.exe` |
| Diablo IV | `Diablo IV.exe`, `DiabloIV.exe` |
| Diablo Immortal | `DiabloImmortal.exe` |

---

## Démarrage rapide

### Depuis GitHub

```bash
git clone https://github.com/wargriff/diablo_translator.git
cd diablo_translator
python build/install_dependencies.py
START.bat
```

### Windows (déjà installé)

| Action | Commande |
|--------|----------|
| Lancer l'app | Double-clic `Lancer.bat` ou `START.bat` |
| Menu Sanctuaire | `START.bat hub` |
| Companion web | `START.bat web` |
| Construire l'exe | `Build-Pro.bat` |
| Raccourci bureau | `powershell -File build\create_desktop_shortcut.ps1` |

Exécutable : `build\dist\DiabloTranslator.exe`

---

## Installation

### Prérequis

- **Windows 10/11**
- **Python 3.12+**
- Connexion Internet (traduction + téléchargement modèles OCR au 1er lancement)
- **Node.js** (uniquement pour le companion web — LTS ou binaire dans `C:\src`)

### Dépendances

```bash
pip install -r requirements.txt
pip install -r backend/requirements.txt    # API FastAPI (web companion)
pip install -r requirements-voice.txt      # micro, optionnel
python build/install_dependencies.py       # tout + vérification
```

### DeepL (optionnel, recommandé)

1. Clé API sur [DeepL Pro API](https://www.deepl.com/pro-api)
2. `copy .env.example .env` puis ajoutez `DEEPL_API_KEY=votre_cle`
3. Ou **Paramètres → Clé API DeepL** dans l'app

Sans clé DeepL, Google est utilisé automatiquement.

---

## Companion web (optionnel)

Le web **ne remplace pas** l'app desktop pour l'OCR en jeu. Il sert d'interface complémentaire (historique, live, statistiques).

```bash
START.bat web
```

Ou manuellement :

```bash
python launcher.py server    # API sur :8000
python launcher.py web       # Next.js sur :3000
```

Ouvrir **http://127.0.0.1:3000**

**Node.js introuvable ?** Placez `node.exe` dans `C:\src` ou définissez `DT_NODE_HOME`. Le lanceur détecte aussi Program Files et `%LOCALAPPDATA%\Programs\node`.

---

## Utilisation

### Workflow en jeu

1. Lancez **Diablo III, IV ou Immortal**
2. Ouvrez l'onglet **Gameplay**
3. Cliquez **Surveiller chat**
4. Les messages du chat sont traduits automatiquement

### Raccourcis clavier

| Raccourci | Action |
|-----------|--------|
| `Ctrl + Entrée` | Traduire le message |
| `Ctrl + Shift + M` | Activer / désactiver le micro |
| `Ctrl + Shift + R` | Actualiser l'état des jeux |

Dans le champ chat, **Entrée seule ne traduit pas** — vous pouvez taper librement.

### Ligne de commande

```bash
python launcher.py check
python launcher.py game
python launcher.py translate "looking for group"
python launcher.py stats
python launcher.py export --format csv
python launcher.py test
```

---

## Configuration

Fichier : `user_data/settings.json`

| Option | Description | Défaut |
|--------|-------------|--------|
| `language` | Langue maison | `fr` |
| `bidirectional_mode` | Chat étranger → FR, vos messages → langue du joueur | `true` |
| `default_reply_language` | Langue de réponse initiale | `en` |
| `preserve_mixed_language` | Garder « yo la team » tel quel | `true` |
| `translator` | `google` ou `deepl` | `google` |
| `chat_monitor_enabled` | Surveillance OCR | `true` |
| `chat_region_preset` | `auto`, `d3`, `d4`, `immortal` | `auto` |
| `auto_detect_language` | Ignorer si déjà dans la langue cible | `true` |
| `speak_translation` | Lecture vocale | `false` |

---

## Architecture

```
launcher.py
    ├── src/                  Application desktop (PyQt6, OCR, traduction)
    ├── backend/              API FastAPI (:8000)
    ├── web/                  Companion Next.js (:3000)
    └── launcher/             Scripts de lancement (web, server, hub)
```

Couches principales : `domain/`, `translation/providers/`, `chat/`, `cache/`, `assets/`.

---

## Structure du projet

```
Diablo_Translator/
├── START.bat / Lancer.bat    Lanceurs Windows
├── Build-Pro.bat             Build PyInstaller
├── assets/                   Thèmes, icônes, polices
├── build/                    Compilation exe
├── backend/                  API REST
├── web/                      Interface web
├── src/                      Code source desktop
├── tests/                    Tests unitaires
├── user_data/                Config & historique (local)
└── launcher.py               Point d'entrée unique
```

---

## Développement

```bash
python launcher.py test
python assets/icons/generate_app_icon.py
python build/build.py
```

CI automatique sur chaque push (`/.github/workflows/ci.yml`). Dependabot vérifie les dépendances chaque semaine.

---

## FAQ

**Le programme lit-il le chat en direct ?**  
Oui, via **OCR** sur la zone chat à l'écran. Placez le chat en bas à gauche comme en jeu.

**Le web ne démarre pas ?**  
Installez `backend/requirements.txt`, vérifiez Node.js (`python launcher.py web`), puis `START.bat web`.

**DeepL ne fonctionne pas ?**  
Vérifiez `DEEPL_API_KEY` dans `.env` ou les paramètres.

**Windows bloque l'exe ?**  
Normal pour un `.exe` non signé. Utilisez `Lancer.bat` ou désactivez le Contrôle intelligent des applications.

**Le micro ne répond pas ?**  
`pip install -r requirements-voice.txt` puis `python launcher.py check`.

**Modèles OCR lents au 1er lancement ?**  
EasyOCR télécharge les modèles dans `models/` une seule fois.

---

## Avertissement

Outil communautaire **non affilié** à Blizzard Entertainment. Utilisez-le conformément aux conditions d'utilisation de vos jeux.

---

<div align="center">

**Diablo Translator v2.1.2** — traduire le chat, jouer sans barrière de langue.

[Signaler un bug](https://github.com/wargriff/diablo_translator/issues) · [Voir les mises à jour](CHANGELOG.md)

</div>
