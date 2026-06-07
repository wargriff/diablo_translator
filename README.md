
# Diablo III Translator

OCR temps réel + traduction automatique.

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
python launcher.py game                  # détecter Diablo III
python launcher.py stats                 # statistiques
python launcher.py export                # export JSON
python launcher.py export --format csv   # export CSV
```
