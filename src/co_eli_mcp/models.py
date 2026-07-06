"""Plain dataclasses mirroring the datos.gov.co Socrata dataset row shape."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Sentencia:
    proceso: str | None
    expediente_tipo: str | None
    expediente_numero: str | None
    magistrado_ponente: str | None
    sala: str | None
    sentencia: str
    fecha_sentencia: str | None


@dataclass(frozen=True)
class Citation:
    lex_uri: str
    human_readable_citation: str
    source_url: str
