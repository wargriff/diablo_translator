from __future__ import annotations

from dataclasses import dataclass


REQUIRED_PACKAGES = (
    "PyQt6",
    "deep_translator",
    "mss",
    "PIL",
    "psutil",
)


@dataclass(slots=True)
class DependencyStatus:

    name: str
    installed: bool
    error: str | None = None


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

    return results


def missing_dependencies() -> list[str]:
    return [item.name for item in check_dependencies() if not item.installed]


def print_dependency_report() -> int:
    statuses = check_dependencies()
    missing = [item for item in statuses if not item.installed]

    for item in statuses:
        state = "OK" if item.installed else "MANQUANT"
        print(f"[{state}] {item.name}")

    if missing:
        print("\nInstallez les dépendances : pip install -r requirements.txt")
        return 1

    print("\nToutes les dépendances sont installées.")
    return 0
