## Diablo Translator v1.1.0

Traduction chat live pour **Diablo III**, **Diablo IV** et **Diablo Immortal**.

### Nouveautés

- **Hub Sanctuaire** — interface PyQt6 épurée, traduction style DeepL, menus complets
- **Live web** — démarrage automatique API + Next.js avant ouverture de `/live`
- **WebSocket live** — flux temps réel entre OCR, API et interface web
- **Traduction bidirectionnelle** — FR ↔ EN corrigée (détection langue + paramètres explicites)
- **Web companion** — pages Traduction, Historique, Paramètres, Live, Statistiques
- **Build PyInstaller** — exe autonome avec hub, backend et lanceurs intégrés

### Installation

1. Téléchargez `DiabloTranslator.exe` ci-dessous (~347 Mo)
2. Double-cliquez pour lancer le **Hub Sanctuaire**
3. Au premier lancement Windows peut afficher Smart App Control — utilisez `build\Lancer.bat` ou autorisez l’application

### Prérequis optionnels

- **Node.js LTS** — pour le web companion (menu Services → Web)
- Connexion Internet — traduction Google/DeepL et OCR EasyOCR

### Jeux supportés

| Jeu | Processus |
|-----|-----------|
| Diablo III | `Diablo III64.exe` |
| Diablo IV | `Diablo IV.exe` |
| Diablo Immortal | `DiabloImmortal.exe` |

### Commit

`4bc5dd7` — Hub Sanctuaire, Live web auto-start et plateforme web unifiée.
