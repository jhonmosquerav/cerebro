"""ONBOARD mecánico — el aplicado determinista del manifiesto (gen-onboard v4).

La entrevista que GENERA `company.yaml` es juicio del agente. Aplicarlo no:
mismo manifiesto + misma fecha ⇒ mismos bytes, y re-aplicar es no-op.
Semántica valida-todo-luego-escribe: si algo está mal (placeholders sin
rellenar, gen en conflicto, lente sin backend), NADA se escribe.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from . import events as events_mod
from . import manifest as mf
from . import statehash
from .schema import is_iso_date
from .slug import slugify

WIKI_TIERS = ("working", "episodic", "semantic", "procedural", "archive")


class OnboardError(ValueError):
    pass


@dataclass
class ApplyResult:
    actions: list[str] = field(default_factory=list)
    state_hash: str | None = None
    seeded_genes: list[str] = field(default_factory=list)
    # Avisos que NO abortan (gen-onboard v6): p. ej. la taxonomía no cubre un tipo de
    # página que el genoma declara. Se ven al aplicar, cuando corregirlo es gratis.
    avisos: list[str] = field(default_factory=list)


def _yaml_quote(text: str, campo: str) -> str:
    if '"' not in text:
        return f'"{text}"'
    if "'" not in text:
        return f"'{text}'"
    raise OnboardError(
        f"{campo} mezcla comillas dobles y simples; simplifícalo en el manifiesto")


def _render_gene(g: dict, date: str) -> str:
    trigger = " ".join(str(g["trigger"]).split())
    rule = str(g["rule"]).strip()
    trigger_yaml = _yaml_quote(trigger, f"seed_genes.{g['id']}.trigger")
    return (
        "---\n"
        f"id: {g['id']}\n"
        f"trigger: {trigger_yaml}\n"
        "status: active\n"
        "version: 1\n"
        "---\n"
        "\n"
        f"{rule}\n"
        "\n"
        f"> Gen de sector sembrado mecánicamente por ONBOARD desde `onboard/company.yaml` ({date}).\n"
        "> Mutarlo pasa por [[gen-compuerta-mutacion]] como cualquier gen.\n"
    )


def _render_profile(m: mf.Manifest, date: str) -> str:
    def lista(xs) -> str:
        return ", ".join(str(x) for x in xs) if xs else "—"

    entidades = (
        " · ".join(
            f"{cat} ({len(items or [])} declaradas)" for cat, items in m.entities.items()
        ) or "—"
    )
    glosario = (
        "\n".join(f"  - **{k}**: {v}" for k, v in sorted(m.glossary.items())) or "  - —"
    )
    genes = ", ".join(f"[[{g['id']}]]" for g in m.seed_genes) or "—"
    lens = m.graph_lens
    if lens.get("enable"):
        lente = f"habilitada (backend: {lens.get('backend')})"
    else:
        lente = "deshabilitada"
    trust = ", ".join(f"{k} {v}" for k, v in sorted(m.source_trust.items())) or "—"
    return (
        "---\n"
        "title: Perfil de la empresa\n"
        "type: meta\n"
        "status: configurado\n"
        f"updated: {date}\n"
        "---\n"
        "\n"
        "# Perfil de la empresa\n"
        "\n"
        f"> Generado mecánicamente por ONBOARD desde `onboard/company.yaml` el {date}.\n"
        "> Mismo manifiesto → mismo perfil. No editar a mano: re-corre ONBOARD.\n"
        "\n"
        "## Identidad\n"
        f"- Nombre: **{m.company_name}**\n"
        f"- Sector / industria: {m.sector or '—'}\n"
        f"- Idioma principal: {m.language}\n"
        f"- Sitio / dominios: {lista(m.company.get('domains'))}\n"
        "\n"
        "## Conocimiento que maneja\n"
        f"- Tipos de documento: {lista(m.document_types)}\n"
        f"- Entidades clave: {entidades}\n"
        "- Glosario / siglas internas:\n"
        f"{glosario}\n"
        "\n"
        "## Roles y equipo\n"
        f"- Roles que consultan/alimentan: {lista(m.roles.get('contributors'))}\n"
        f"- Aprueba mutaciones del genoma: {m.roles.get('mutation_approver') or '—'}\n"
        "\n"
        "## Configuración sembrada\n"
        f"- Verbos de dominio (`relation_types`): {lista(m.relation_types)}\n"
        f"- Sensibilidad por defecto: `{m.default_sensibilidad}`\n"
        f"- Confianza por fuente (`source_trust`): {trust}\n"
        f"- Umbrales: síntesis {m.sintesis_umbral} · hub {m.hub_umbral}\n"
        f"- Genes de sector sembrados: {genes}\n"
        f"- Lente de grafo: {lente}\n"
    )


def _render_estado(m: mf.Manifest, date: str) -> str:
    return (
        "## Estado\n"
        f"- Fase: **configurado** — ONBOARD aplicado mecánicamente el {date}.\n"
        f"- Empresa: **{m.company_name}** ({m.sector or 'sector sin declarar'})\n"
    )


def _replace_estado(index_text: str, nuevo: str) -> str:
    lines = index_text.split("\n")
    try:
        ini = next(i for i, l in enumerate(lines) if l.strip() == "## Estado")
    except StopIteration:
        raise OnboardError(
            "index.md no tiene sección '## Estado'; el índice no sigue la plantilla")
    fin = next(
        (i for i in range(ini + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    nuevas = nuevo.rstrip("\n").split("\n")
    if fin < len(lines):
        return "\n".join(lines[:ini] + nuevas + [""] + lines[fin:])
    return "\n".join(lines[:ini] + nuevas)


def apply(manifest_path: Path | str, vault_root: Path | str, *,
          date: str, dry_run: bool = False) -> ApplyResult:
    root = Path(vault_root)
    if not is_iso_date(date):
        raise OnboardError(f"fecha inválida (usa YYYY-MM-DD): {date!r}")
    # 1) VALIDAR TODO ────────────────────────────────────────────────────────
    try:
        m = mf.load(manifest_path)
    except Exception as e:
        raise OnboardError(f"manifiesto ilegible: {e}") from e
    errores = mf.validate(m)
    if errores:
        raise OnboardError("manifiesto inválido:\n  - " + "\n  - ".join(errores))
    if mf.has_placeholders(m):
        raise OnboardError(
            "el manifiesto conserva placeholders <...> de blueprint sin rellenar; "
            "complétalo antes de aplicar (la entrevista del agente sirve para esto)")
    lens = m.graph_lens
    if lens.get("enable") and not lens.get("backend"):
        raise OnboardError(
            "graph_lens.enable está activo sin graph_lens.backend: la elección de "
            "backend es del humano (claude|local|structural) — regístrala en el "
            "manifiesto y re-corre (gen-graph-lens: se pregunta UNA vez)")
    index_path = root / "index.md"
    if not index_path.is_file():
        raise OnboardError(f"no existe {index_path.as_posix()}: ¿es un vault CEREBRO?")
    index_text = index_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    nuevo_index = _replace_estado(index_text, _render_estado(m, date))

    escrituras: list[tuple[Path, str, str]] = []   # (path, contenido, acción)
    carpetas: list[tuple[Path, str]] = []
    eventos_nuevos: list[dict] = []
    seeded: list[str] = []

    perfil_path = root / "genome" / "company-profile.md"
    perfil_nuevo = _render_profile(m, date)
    perfil_actual = (perfil_path.read_text(encoding="utf-8").replace("\r\n", "\n")
                     if perfil_path.is_file() else None)
    if perfil_actual != perfil_nuevo:
        escrituras.append((perfil_path, perfil_nuevo,
                           "perfil: genome/company-profile.md renderizado"))

    # taxonomía + categorías de entities
    destinos: list[Path] = []
    for tier, folders in sorted(m.taxonomy.items()):
        for folder in folders or []:
            destinos.append(root / "wiki" / tier / folder)
    for cat in m.entities:
        destinos.append(root / "wiki" / "semantic" / slugify(str(cat)))
    for d in sorted(set(destinos), key=lambda p: p.as_posix()):
        keep = d / ".gitkeep"
        if not keep.is_file():
            carpetas.append((keep, f"carpeta: {keep.relative_to(root).as_posix()}"))

    # seed genes: idéntico ⇒ no-op · distinto ⇒ error · nuevo ⇒ sembrar
    for g in m.seed_genes:
        gen_path = root / "genome" / "genes" / f"{g['id']}.md"
        contenido = _render_gene(g, date)
        if gen_path.is_file():
            actual = gen_path.read_text(encoding="utf-8").replace("\r\n", "\n")
            if actual == contenido:
                continue
            raise OnboardError(
                f"el gen {g['id']} ya existe con contenido DISTINTO: ONBOARD jamás "
                "pisa un gen; resuélvelo por EVOLVE/compuerta o renombra el seed")
        escrituras.append((gen_path, contenido,
                           f"gen sembrado: genome/genes/{g['id']}.md (v1)"))
        seeded.append(g["id"])
        eventos_nuevos.append({
            "ts": date,
            "type": "gene_added",
            "target": g["id"],
            "signal": "ONBOARD: gen de sector sembrado desde onboard/company.yaml",
            "diff": "∅ → v1",
            "approved_by": "user",
            "status": "applied",
        })

    if nuevo_index != index_text:
        escrituras.append((index_path, nuevo_index, "index.md: bloque Estado actualizado"))

    acciones = [a for _, a in carpetas] + [a for _, _, a in escrituras] + [
        f"evento: gene_added {e['target']}" for e in eventos_nuevos
    ]

    # 2) ESCRIBIR (solo si no es dry-run) ────────────────────────────────────
    resultado = ApplyResult(actions=acciones, seeded_genes=seeded, avisos=mf.avisos(m))
    if dry_run:
        return resultado
    for keep, _ in carpetas:
        keep.parent.mkdir(parents=True, exist_ok=True)
        keep.write_text("", encoding="utf-8")
    for path, contenido, _ in escrituras:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="\n") as f:
            f.write(contenido)
    if eventos_nuevos:
        ledger = root / "genome" / "events.jsonl"
        ledger.parent.mkdir(parents=True, exist_ok=True)
        for ev in eventos_nuevos:
            events_mod.append_line(ledger, ev)
    resultado.state_hash = statehash.tree_hash(root, "all")
    return resultado
