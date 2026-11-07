"""Historial de la sesión, solo en memoria: se pierde al reiniciar el servidor.

Se guardan métricas, no texto extraído, para no retener contenido de los documentos.
"""

from collections import deque

from .models import HistoryEntry

_entries: deque[HistoryEntry] = deque(maxlen=50)


def add(entry: HistoryEntry) -> None:
    _entries.appendleft(entry)


def all_entries() -> list[HistoryEntry]:
    return list(_entries)


def clear() -> None:
    _entries.clear()
