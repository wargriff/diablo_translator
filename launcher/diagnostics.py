"""Diagnostics environnement (Node, API, ports)."""

from __future__ import annotations

from dataclasses import dataclass

from launcher.api_probe import DEFAULT_API_PORT, probe_diablo_api, probe_web_home
from launcher.service_ports import DEFAULT_WEB_PORT, resolve_web_port


@dataclass(slots=True)
class DiagnosticLine:
    label: str
    ok: bool
    detail: str


def collect_diagnostics() -> list[DiagnosticLine]:
    lines: list[DiagnosticLine] = []

    try:
        import uvicorn  # noqa: F401

        lines.append(DiagnosticLine("API FastAPI", True, "uvicorn installe"))
    except ImportError:
        lines.append(
            DiagnosticLine(
                "API FastAPI",
                False,
                "pip install -r backend/requirements.txt",
            )
        )

    from launcher.nodejs import find_npm, npm_hint

    npm = find_npm()
    lines.append(
        DiagnosticLine(
            "Node.js / npm",
            npm is not None,
            npm_hint() if npm else npm_hint(),
        )
    )

    from src.infrastructure.paths import PROJECT_ROOT

    node_modules = PROJECT_ROOT / "web" / "node_modules"
    lines.append(
        DiagnosticLine(
            "web/node_modules",
            node_modules.is_dir(),
            "pret" if node_modules.is_dir() else "npm install au 1er lancement web",
        )
    )

    api_ok = probe_diablo_api(DEFAULT_API_PORT)
    lines.append(
        DiagnosticLine(
            f"API :{DEFAULT_API_PORT}",
            api_ok,
            "en ligne" if api_ok else "arrete",
        )
    )

    web_port = resolve_web_port()
    web_ok = probe_web_home(web_port)
    lines.append(
        DiagnosticLine(
            f"Web :{web_port}",
            web_ok,
            "en ligne" if web_ok else "arrete",
        )
    )

    return lines
