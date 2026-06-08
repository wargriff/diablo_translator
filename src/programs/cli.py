from __future__ import annotations

import argparse
from pathlib import Path


def run_build_verify() -> int:
    """Smoke test pour build PyInstaller (exit 0 = OK)."""
    modules = (
        "PyQt6.QtWidgets",
        "cv2",
        "easyocr",
        "torch",
        "mss",
        "psutil",
        "langdetect",
        "deep_translator",
        "sounddevice",
        "_sounddevice",
        "speech_recognition",
        "src.infrastructure.container",
        "src.infrastructure.application_container",
        "src.application.live_chat_service",
        "src.capture.capture_region_resolver",
    )
    failed: list[str] = []
    for name in modules:
        try:
            __import__(name)
        except Exception as exc:
            failed.append(f"{name}: {exc}")

    if failed:
        print("VERIFY FAILED")
        for line in failed:
            print(f"  - {line}")
        return 1

    try:
        from src.infrastructure.container import Container
        from src.ui.services.ui_thread_bridge import UiThreadBridge

        bridge = UiThreadBridge()
        container = Container(ui_bridge=bridge)
        container.shutdown()
    except Exception as exc:
        print("VERIFY FAILED")
        print(f"  - Container(): {exc}")
        return 1

    print("VERIFY OK — modules critiques + DLL chargeables")
    return 0


def run_translate(text: str) -> int:
    try:
        from src.infrastructure.container import Container

        container = Container()
        result = container.pipeline.process_text(text)
    except ModuleNotFoundError as exc:
        print(f"Dépendance manquante : {exc.name}")
        print("Installez les dépendances : pip install -r requirements.txt")
        return 1

    if result.source_language:
        lang = container.pipeline.translator.language_display_name(result.source_language)
        print(f"[{lang}] {result.source_text}")
    print(result.display_text)
    print(f"(moteur: {result.provider})")
    return 0


def run_game_status() -> int:
    try:
        from src.game_detection import SUPPORTED_GAMES
        from src.infrastructure.container import Container

        container = Container()
        status = container.game_detection.scan()
    except ModuleNotFoundError as exc:
        print(f"Dépendance manquante : {exc.name}")
        print("Installez les dépendances : pip install -r requirements.txt")
        return 1

    for game in SUPPORTED_GAMES:
        if game.key in status.active_processes:
            process = status.active_processes[game.key]
            print(f"[ACTIF] {game.title} ({process})")
        else:
            print(f"[OFF]   {game.title}")

    print()
    print(status.summary())
    return 0 if status.is_any_running else 1


def run_export(fmt: str, output: Path | None) -> int:
    from src.export.export_service import ExportService

    service = ExportService()
    if fmt == "json":
        path = service.export_json(output)
    else:
        path = service.export_csv(output)

    print(f"Export créé : {path}")
    return 0


def run_analytics() -> int:
    from src.analytics.analytics_service import AnalyticsService

    summary = AnalyticsService().get_summary()
    print(f"Total traductions : {summary.total_translations}")
    print(f"Aujourd'hui       : {summary.translations_today}")
    print(f"Textes uniques    : {summary.unique_sources}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="launcher",
        description="Diablo Translator",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("gui", help="Lancer l'interface graphique")
    sub.add_parser("check", help="Vérifier les dépendances")
    sub.add_parser("verify", help="Vérification build exe (modules critiques)")
    sub.add_parser("preset", help="Aperçu preset/config avant build exe")
    sub.add_parser("game", help="Détecter Diablo III, IV ou Immortal")
    sub.add_parser("stats", help="Afficher les statistiques")
    sub.add_parser("test", help="Lancer les tests unitaires")

    server = sub.add_parser("server", help="Lancer l'API FastAPI (mobile / web)")
    server.add_argument("--host", default=None, help="Hôte (défaut 0.0.0.0)")
    server.add_argument("--port", type=int, default=None, help="Port (défaut 8000)")

    web = sub.add_parser("web", help="Lancer le companion web Next.js")
    web.add_argument("--port", type=int, default=3000, help="Port (défaut 3000)")
    web.add_argument("--kill", action="store_true", help="Libérer le port si occupé")

    mobile = sub.add_parser("mobile", help="Lancer l'app Flutter (Android / iOS)")
    mobile.add_argument("-d", "--device", default=None, help="ID appareil Flutter")

    translate = sub.add_parser("translate", help="Traduire un texte")
    translate.add_argument("text", nargs="+", help="Texte à traduire")

    export = sub.add_parser("export", help="Exporter l'historique")
    export.add_argument(
        "--format",
        choices=("json", "csv"),
        default="json",
        help="Format d'export",
    )
    export.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Fichier de destination",
    )

    return parser


def dispatch(args: argparse.Namespace) -> int:
    command = args.command or "gui"

    if command == "check":
        from src.programs.dependency_checker import print_dependency_report

        return print_dependency_report()

    if command == "verify":
        return run_build_verify()

    if command == "preset":
        from src.programs.preset_preview import run_preset_preview

        return run_preset_preview()

    if command == "translate":
        return run_translate(" ".join(args.text))

    if command == "game":
        return run_game_status()

    if command == "export":
        return run_export(args.format, args.output)

    if command == "stats":
        return run_analytics()

    if command == "test":
        from tests.run_tests import run_tests

        return run_tests()

    if command == "server":
        from launcher.server import run_server

        return run_server(host=args.host, port=args.port)

    if command == "web":
        from launcher.web import run_web

        return run_web(port=args.port, kill=args.kill)

    if command == "mobile":
        from launcher.mobile import run_mobile

        return run_mobile(device=args.device)

    if command == "gui":
        missing = []
        try:
            from src.programs.dependency_checker import missing_dependencies

            missing = missing_dependencies()
        except Exception:
            pass

        if missing:
            print("Dépendances manquantes :", ", ".join(missing))
            print("Installez-les avec : pip install -r requirements.txt")
            return 1

        from src.bootstrap.app import Application

        Application().run()
        return 0

    return 1
