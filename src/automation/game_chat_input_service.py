from __future__ import annotations

import ctypes
import sys
import time
from ctypes import wintypes

from src.capture.game_window_service import GameWindowService
from src.game_detection.game_detection_service import GameDetectionService, GameDetectionStatus

INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
VK_RETURN = 0x0D
VK_CONTROL = 0x11
VK_V = 0x56
SW_RESTORE = 9
FOCUS_ATTEMPTS = 3


class _KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_ulonglong),
    ]


class _INPUT(ctypes.Structure):
    class _INPUTUNION(ctypes.Union):
        _fields_ = [("ki", _KEYBDINPUT)]

    _anonymous_ = ("_input",)
    _fields_ = [
        ("type", wintypes.DWORD),
        ("_input", _INPUTUNION),
    ]


class GameChatInputService:

    @classmethod
    def send_message(
        cls,
        game_detection: GameDetectionService,
        text: str,
        *,
        send_enter: bool = True,
        restore_hwnd: int | None = None,
        status: GameDetectionStatus | None = None,
    ) -> tuple[bool, str]:
        if sys.platform != "win32":
            return False, "Envoi automatique disponible seulement sur Windows."

        cleaned = text.strip()
        if not cleaned:
            return False, "Texte vide."

        game_info = GameWindowService.find_primary_game_info(
            game_detection,
            status=status,
        )
        if game_info is None:
            return False, "Aucune fenêtre Diablo détectée — lancez le jeu."

        previous_clipboard = cls._read_clipboard()
        try:
            cls._write_clipboard(cleaned)

            if not cls._focus_window_with_retry(game_info.hwnd):
                return False, "Impossible de prendre le focus sur Diablo."

            time.sleep(0.06)
            cls._tap_key(VK_RETURN)
            time.sleep(0.08)
            cls._hotkey_ctrl_v()
            time.sleep(0.04)

            if send_enter:
                cls._tap_key(VK_RETURN)

            if restore_hwnd:
                time.sleep(0.04)
                cls._focus_window_with_retry(restore_hwnd, attempts=2)

            return True, ""
        except Exception as exc:
            return False, str(exc)
        finally:
            try:
                cls._write_clipboard(previous_clipboard)
            except Exception:
                pass

    @classmethod
    def _focus_window_with_retry(cls, hwnd: int, *, attempts: int = FOCUS_ATTEMPTS) -> bool:
        for attempt in range(attempts):
            if cls._focus_window(hwnd):
                return True
            time.sleep(0.05 * (attempt + 1))
        return False

    @classmethod
    def _focus_window(cls, hwnd: int) -> bool:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        if not user32.IsWindow(hwnd):
            return False

        if user32.GetForegroundWindow() == hwnd:
            return True

        foreground = user32.GetForegroundWindow()
        foreground_thread = user32.GetWindowThreadProcessId(foreground, None)
        target_thread = user32.GetWindowThreadProcessId(hwnd, None)
        current_thread = kernel32.GetCurrentThreadId()

        attached_foreground = False
        attached_target = False
        try:
            if foreground_thread:
                attached_foreground = bool(
                    user32.AttachThreadInput(current_thread, foreground_thread, True)
                )
            if target_thread:
                attached_target = bool(
                    user32.AttachThreadInput(target_thread, foreground_thread, True)
                )

            user32.ShowWindow(hwnd, SW_RESTORE)
            user32.BringWindowToTop(hwnd)
            user32.SetForegroundWindow(hwnd)
        finally:
            if attached_target and target_thread:
                user32.AttachThreadInput(target_thread, foreground_thread, False)
            if attached_foreground and foreground_thread:
                user32.AttachThreadInput(current_thread, foreground_thread, False)

        time.sleep(0.04)
        return user32.GetForegroundWindow() == hwnd

    @classmethod
    def _tap_key(cls, virtual_key: int) -> None:
        cls._send_input(virtual_key, key_up=False)
        cls._send_input(virtual_key, key_up=True)

    @classmethod
    def _hotkey_ctrl_v(cls) -> None:
        cls._send_input(VK_CONTROL, key_up=False)
        cls._send_input(VK_V, key_up=False)
        cls._send_input(VK_V, key_up=True)
        cls._send_input(VK_CONTROL, key_up=True)

    @staticmethod
    def _send_input(virtual_key: int, *, key_up: bool) -> None:
        flags = KEYEVENTF_KEYUP if key_up else 0
        event = _INPUT(
            type=INPUT_KEYBOARD,
            ki=_KEYBDINPUT(
                wVk=virtual_key,
                wScan=0,
                dwFlags=flags,
                time=0,
                dwExtraInfo=0,
            ),
        )
        sent = ctypes.windll.user32.SendInput(
            1,
            ctypes.byref(event),
            ctypes.sizeof(event),
        )
        if sent != 1:
            raise RuntimeError("SendInput a échoué")

    @staticmethod
    def _read_clipboard() -> str:
        import pyperclip

        try:
            return pyperclip.paste() or ""
        except Exception:
            return ""

    @staticmethod
    def _write_clipboard(value: str) -> None:
        import pyperclip

        pyperclip.copy(value)
