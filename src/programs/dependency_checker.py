from __future__ import annotations

from dataclasses import dataclass


REQUIRED_PACKAGES = (
    "PyQt6",
    "deep_translator",
    "mss",
    "PIL",
    "psutil",
)

VOICE_PACKAGES = (
    ("speech_recognition", "SpeechRecognition"),
    ("sounddevice", "SoundDevice"),
)


@dataclass(slots=True)
class DependencyStatus:

    name: str
    installed: bool
    error: str | None = None
    optional: bool = False


def check_dependencies() -> list[DependencyStatus]:
    results: list[DependencyStatus] = []

    for package in REQUIRED_PACKAGES:
        try:
            __import__(package)
            results.append(DependencyStatus(name=package, installed=True))
        except ModuleNotFoundError as exc:
            results.append(
                DependencyStatus(
                    name=package,
                    installed=False,
                    error=str(exc),
                )
            )

    for import_name, label in VOICE_PACKAGES:
        try:
            __import__(import_name)
            results.append(
                DependencyStatus(name=label, installed=True, optional=True)
            )
        except ModuleNotFoundError as exc:
            results.append(
                DependencyStatus(
                    name=label,
                    installed=False,
                    error=str(exc),
                    optional=True,
                )
            )

    return results


def missing_dependencies() -> list[str]:
    return [
        item.name
        for item in check_dependencies()
        if not item.installed and not item.optional
    ]


def print_dependency_report() -> int:
    statuses = check_dependencies()
    missing = [item for item in statuses if not item.installed and not item.optional]
    voice_missing = [item for item in statuses if not item.installed and item.optional]

    for item in statuses:
        state = "OK" if item.installed else "MANQUANT"
        suffix = " (optionnel · micro)" if item.optional else ""
        print(f"[{state}] {item.name}{suffix}")

    if missing:
        print("\nInstallez les dépendances : pip install -r requirements.txt")
        return 1

    if voice_missing:
        print(
            "\nMicro desactive tant que ces paquets ne sont pas installes : "
            "pip install SpeechRecognition sounddevice"
        )

    print("\nToutes les dépendances principales sont installées.")
    return 0
