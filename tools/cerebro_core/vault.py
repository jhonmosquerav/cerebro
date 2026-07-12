"""Modelo en memoria del vault CEREBRO: páginas, genes, enlaces."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from . import fm as fm_mod
from . import schema

# Carpetas que jamás participan del conocimiento ni de la resolución de enlaces.
EXCLUDED_DIRS = {
    ".git", ".claude", ".obsidian", ".githooks", ".github", ".trash",
    "tests", "worked", "tools", "graphify-out", "node_modules", "__pycache__",
}


@dataclass
class Page:
    path: Path
    rel: str                      # ruta relativa posix
    fm: dict | None
    body: str
    fm_errors: list[str] = field(default_factory=list)
    wikilinks: list[str] = field(default_factory=list)

    @property
    def is_meta(self) -> bool:
        return bool(self.fm) and self.fm.get("type") == "meta"

    @property
    def tier_from_path(self) -> str | None:
        parts = self.rel.split("/")
        if len(parts) >= 2 and parts[0] == "wiki":
            return parts[1]
        return None

    @property
    def basename(self) -> str:
        return Path(self.rel).stem


@dataclass
class Vault:
    root: Path
    pages: list[Page] = field(default_factory=list)   # todos los .md cargados
    _by_rel: dict[str, Page] = field(default_factory=dict)
    _resolve: dict[str, str] = field(default_factory=dict)

    @property
    def wiki_pages(self) -> list[Page]:
        return [p for p in self.pages if p.rel.startswith("wiki/")]

    @property
    def genes(self) -> list[Page]:
        return [p for p in self.pages if p.rel.startswith("genome/genes/")]

    @property
    def capsules(self) -> list[Page]:
        return [p for p in self.pages if p.rel.startswith("genome/capsules/")]

    def page_by_rel(self, rel: str) -> Page | None:
        return self._by_rel.get(rel)

    def resolve_link(self, name: str) -> str | None:
        """Resuelve un destino de [[wikilink]] a ruta relativa (o None)."""
        return self._resolve.get(name.strip().lower())

    def relations_of(self, page: Page) -> list[tuple[str, str]]:
        if not page.fm:
            return []
        return schema.relation_pairs(page.fm.get("relations"))


def _iter_md(root: Path):
    for path in sorted(root.rglob("*.md")):
        rel_parts = path.relative_to(root).parts
        if any(part in EXCLUDED_DIRS or part.startswith(".") for part in rel_parts[:-1]):
            continue
        yield path


def load_vault(root: Path | str) -> Vault:
    root = Path(root)
    v = Vault(root=root)
    for path in _iter_md(root):
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        meta, body, errors = fm_mod.split(text)
        page = Page(
            path=path, rel=rel, fm=meta, body=body,
            fm_errors=errors, wikilinks=fm_mod.wikilinks(body),
        )
        v.pages.append(page)
        v._by_rel[rel] = page
    # Índice de resolución: basename > title > alias (el primero en orden de
    # ruta gana; los empates de basename son colisiones que LINT puede señalar).
    for page in v.pages:
        key = page.basename.lower()
        v._resolve.setdefault(key, page.rel)
    for page in v.pages:
        if page.fm and isinstance(page.fm.get("title"), str):
            v._resolve.setdefault(page.fm["title"].strip().lower(), page.rel)
    for page in v.pages:
        if page.fm and isinstance(page.fm.get("id_alias"), list):
            for alias in page.fm["id_alias"]:
                alias = str(alias).strip().lower()
                if alias:
                    v._resolve.setdefault(alias, page.rel)
                    tail = alias.rsplit("/", 1)[-1]
                    v._resolve.setdefault(tail, page.rel)
    return v
