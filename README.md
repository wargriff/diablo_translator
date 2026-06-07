
# Diablo Translator

OCR temps réel + traduction automatique pour Diablo III, Diablo IV et Diablo Immortal.

## Installation

```bash
pip install -r requirements.txt
```

## Lancement

Interface graphique (par défaut) :

```bash
python launcher.py
python launcher.py gui
```

## Programmes CLI

```bash
python launcher.py check                 # vérifier les dépendances
python launcher.py translate "hello"     # traduire un texte
python launcher.py game                  # détecter D3, D4 ou Immortal
python launcher.py stats                 # statistiques
python launcher.py export                # export JSON
python launcher.py export --format csv   # export CSV
```
