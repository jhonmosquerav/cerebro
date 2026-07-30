#!/usr/bin/env python3
"""CLI del núcleo mecánico de CEREBRO.

    python tools/cerebro.py <comando> [opciones]

Comandos: lint · mirror · events · hash · onboard · consolidate · health ·
xray · graph · verify. Todos aceptan --vault DIR (default: la raíz de este repo).
Cero dependencias: cualquier Python ≥ 3.10.
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cerebro_core import consolidate_scan as cs_mod
from cerebro_core import events as events_mod
from cerebro_core import graph as graph_mod
from cerebro_core import health as health_mod
from cerebro_core import lint as lint_mod
from cerebro_core import manifest as mf
from cerebro_core import mirror as mirror_mod
from cerebro_core import onboard as onboard_mod
from cerebro_core import statehash
from cerebro_core import xray as xray_mod
from cerebro_core.findings import has_errors
from cerebro_core.vault import load_vault

REPO_ROOT = Path(__file__).resolve().parent.parent


def _as_of(value: str | None) -> datetime.date:
    if value is None:
        return datetime.date.today()
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        raise SystemExit(f"--as-of inválido (YYYY-MM-DD): {value!r}")


def _exclude_set(value: str | None) -> set[str]:
    if not value:
        return set()
    if value == "temporales":
        return set(lint_mod.CODIGOS_TEMPORALES)
    return {c.strip().upper() for c in value.split(",") if c.strip()}


def cmd_lint(args) -> int:
    report = lint_mod.run(args.vault, as_of=_as_of(args.as_of),
                          exclude=_exclude_set(args.exclude))
    sys.stdout.write(report.render_json() if args.json else report.render_text())
    return report.exit_code(strict=args.strict)


def cmd_mirror(args) -> int:
    problema = mirror_mod.check(args.vault)
    if problema and args.fix:
        mirror_mod.fix(args.vault)
        print("espejo re-sincronizado: CLAUDE.md → AGENTS.md")
        return 0
    if problema:
        print(f"[ERROR] {problema}")
        return 1
    print("espejo en verde: AGENTS.md ≡ CLAUDE.md")
    return 0


def cmd_events(args) -> int:
    ledger = Path(args.vault) / "genome" / "events.jsonl"
    if args.events_cmd == "verify":
        findings = events_mod.verify_file(ledger)
        findings += events_mod.verify_append_only(args.vault, "genome/events.jsonl")
        for f in findings:
            print(f.render())
        if not findings:
            print("ledger en verde: esquema válido, historia append-only")
        return 1 if has_errors(findings) else 0
    if args.events_cmd == "append":
        evento = {
            "ts": args.ts or datetime.date.today().isoformat(),
            "type": args.type,
            "target": args.target,
            "signal": args.signal,
            "diff": args.diff,
            "approved_by": args.approved_by,
            "status": args.status,
        }
        try:
            line = events_mod.append_line(ledger, evento)
        except events_mod.EventError as e:
            print(f"[ERROR] {e}")
            return 2
        print(f"evento añadido con hash-chain: {line}")
        return 0
    return 2


def cmd_hash(args) -> int:
    if args.detail:
        sys.stdout.write(statehash.manifest_lines(args.vault, args.scope))
    print(f"{args.scope} {statehash.tree_hash(args.vault, args.scope)}")
    return 0


def cmd_onboard(args) -> int:
    manifest_path = Path(args.manifest) if args.manifest else Path(args.vault) / "onboard" / "company.yaml"
    date = args.date or datetime.date.today().isoformat()
    try:
        res = onboard_mod.apply(manifest_path, args.vault, date=date, dry_run=args.dry_run)
    except onboard_mod.OnboardError as e:
        print(f"[ERROR] ONBOARD abortado sin escribir nada:\n{e}")
        return 1
    modo = "PLAN (dry-run)" if args.dry_run else "APLICADO"
    print(f"ONBOARD {modo} · manifiesto {manifest_path} · fecha {date}")
    if not res.actions:
        print("sin acciones: el vault ya refleja este manifiesto (idempotencia)")
    for a in res.actions:
        print(f"  - {a}")
    for av in res.avisos:
        print(f"  [AVISO] {av}")
    if res.state_hash:
        print(f"hash de estado (all): {res.state_hash}")
        print("recuerda: 1 commit por esta corrida + línea ya registrada en events.jsonl")
    return 0


def cmd_consolidate(args) -> int:
    report = cs_mod.run(args.vault, as_of=_as_of(args.as_of))
    sys.stdout.write(report.render_json() if args.json else report.render_text())
    return 0


def cmd_health(args) -> int:
    report = health_mod.run(args.vault, as_of=_as_of(args.as_of))
    sys.stdout.write(report.render_json() if args.json else report.render_text())
    if args.write:
        path = health_mod.write_dashboard(args.vault, report)
        print(f"tablero escrito: {Path(path).name} (dashboards/)")
    return 0


def cmd_xray(args) -> int:
    report = xray_mod.run(args.vault, as_of=_as_of(args.as_of),
                          inferred_path=args.inferred, min_co=args.min_co)
    sys.stdout.write(report.render_json() if args.json else report.render_md())
    if args.write:
        destino = xray_mod.write_report(args.vault, report)
        print(f"corrida persistida: {destino}")
    return 0


def cmd_graph(args) -> int:
    vault = Path(args.vault)
    v = load_vault(vault)
    if getattr(args, "origen", None):
        g = graph_mod.build(v, args.scope)
        origen = _resolver_pagina(v, args.origen)
        destino = _resolver_pagina(v, args.destino)
        if origen is None or destino is None:
            falta = args.origen if origen is None else args.destino
            print(f"no resuelve a ninguna página: {falta!r}")
            return 1
        camino = graph_mod.camino_mas_corto(g, origen, destino)
        if camino is None:
            print(f"sin ruta entre {origen} y {destino} "
                  f"(scope {args.scope}: están en componentes distintas)")
            return 1
        print(f"CAMINO ({len(camino) - 1} salto(s)):")
        for i, rel in enumerate(camino):
            print(f"  {'  ' * i}{'└─ ' if i else ''}{rel}")
        return 0
    m = lint_mod._load_manifest(vault)
    umbral = m.hub_umbral if m else 7
    rep = graph_mod.reporte(v, scope=args.scope, hub_umbral=umbral)
    sys.stdout.write(json.dumps(rep, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
                     if args.json else graph_mod.render_text(rep))
    return 0


def _resolver_pagina(v, nombre: str) -> str | None:
    """Acepta ruta relativa exacta o nombre de wikilink."""
    if v.page_by_rel(nombre):
        return nombre
    return v.resolve_link(nombre)


def cmd_verify(args) -> int:
    vault = Path(args.vault)
    ok = True

    def paso(nombre: str, findings_o_error) -> None:
        nonlocal ok
        if isinstance(findings_o_error, str):
            print(f"  ✘ {nombre}: {findings_o_error}")
            ok = False
        elif findings_o_error:
            errores = [f for f in findings_o_error if f.severity == "error"]
            for f in findings_o_error:
                print(f"    {f.render()}")
            if errores:
                print(f"  ✘ {nombre}: {len(errores)} error(es)")
                ok = False
            else:
                print(f"  ✔ {nombre} (solo avisos/info)")
        else:
            print(f"  ✔ {nombre}")

    print(f"VERIFY · vault {vault}")
    paso("espejo AGENTS.md ≡ CLAUDE.md", mirror_mod.check(vault))
    ledger = vault / "genome" / "events.jsonl"
    paso("events.jsonl (esquema + hash-chain)", events_mod.verify_file(ledger))
    paso("events.jsonl (append-only vs git)",
         events_mod.verify_append_only(vault, "genome/events.jsonl"))
    if not args.quick:
        excl = _exclude_set(getattr(args, "exclude", None))
        report = lint_mod.run(vault, as_of=_as_of(args.as_of), exclude=excl)
        etiqueta = f"lint mecánico ({report.pages_total} páginas)"
        if excl:
            etiqueta += f" [sin {', '.join(sorted(excl))}]"
        paso(etiqueta, report.findings)
        ejemplo = vault / "onboard" / "company.example.yaml"
        if ejemplo.is_file():
            try:
                errs = mf.validate(mf.load(ejemplo))
                paso("manifiesto de ejemplo", "; ".join(errs) if errs else [])
            except Exception as e:
                paso("manifiesto de ejemplo", str(e))
    print("VERIFY: " + ("EN VERDE ✔" if ok else "EN ROJO ✘"))
    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="cerebro", description=__doc__)
    p.add_argument("--vault", default=str(REPO_ROOT),
                   help="raíz del vault (default: este repo)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("lint", help="detectores mecánicos de gen-lint")
    sp.add_argument("--as-of", default=None, help="fecha de corte YYYY-MM-DD (default: hoy)")
    sp.add_argument("--strict", action="store_true", help="avisos también fallan")
    sp.add_argument("--exclude", default=None, metavar="CODIGOS",
                    help="códigos a silenciar, separados por coma (p. ej. VIG-01,VIG-02); "
                         "'temporales' = los que dependen del calendario, no del commit")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(fn=cmd_lint)

    sp = sub.add_parser("mirror", help="espejo AGENTS.md ≡ CLAUDE.md (C-02)")
    sp.add_argument("--fix", action="store_true", help="copia CLAUDE.md → AGENTS.md")
    sp.set_defaults(fn=cmd_mirror)

    sp = sub.add_parser("events", help="integridad del ledger (C-03)")
    ev = sp.add_subparsers(dest="events_cmd", required=True)
    ev_v = ev.add_parser("verify")
    ev_v.set_defaults(fn=cmd_events)
    ev_a = ev.add_parser("append", help="añade un evento con hash-chain")
    for campo in ("type", "target", "signal", "diff"):
        ev_a.add_argument(f"--{campo}", required=True)
    ev_a.add_argument("--approved-by", dest="approved_by", default="user")
    ev_a.add_argument("--status", default="applied",
                      choices=sorted(events_mod.VALID_STATUS))
    ev_a.add_argument("--ts", default=None, help="YYYY-MM-DD (default: hoy)")
    ev_a.set_defaults(fn=cmd_events)

    sp = sub.add_parser("hash", help="hash de estado determinista")
    sp.add_argument("--scope", default="genome", choices=sorted(statehash.SCOPES))
    sp.add_argument("--detail", action="store_true", help="línea por archivo")
    sp.set_defaults(fn=cmd_hash)

    sp = sub.add_parser("onboard", help="aplicado mecánico del manifiesto")
    ob = sp.add_subparsers(dest="onboard_cmd", required=True)
    ob_a = ob.add_parser("apply")
    ob_a.add_argument("--manifest", default=None,
                      help="ruta del company.yaml (default: <vault>/onboard/company.yaml)")
    ob_a.add_argument("--date", default=None,
                      help="fecha determinista YYYY-MM-DD (default: hoy; fíjala para reproducir)")
    ob_a.add_argument("--dry-run", action="store_true")
    ob_a.set_defaults(fn=cmd_onboard)

    sp = sub.add_parser("consolidate", help="scanner mecánico de consolidate")
    co = sp.add_subparsers(dest="consolidate_cmd", required=True)
    co_s = co.add_parser("scan")
    co_s.add_argument("--as-of", default=None)
    co_s.add_argument("--json", action="store_true")
    co_s.set_defaults(fn=cmd_consolidate)

    sp = sub.add_parser("health", help="score de salud determinista")
    sp.add_argument("--as-of", default=None)
    sp.add_argument("--json", action="store_true")
    sp.add_argument("--write", action="store_true",
                    help="escribe dashboards/salud-mecanica.md")
    sp.set_defaults(fn=cmd_health)

    sp = sub.add_parser("xray", help="deriva declarado vs inferido (propone, no aplica)")
    sp.add_argument("--as-of", default=None)
    sp.add_argument("--inferred", default=None,
                    help="graph.json externo (p. ej. de graphify) como evidencia extra")
    sp.add_argument("--min-co", type=int, default=2,
                    help="co-menciones mínimas para proponer arista (default 2)")
    sp.add_argument("--json", action="store_true")
    sp.add_argument("--write", action="store_true",
                    help="persiste la corrida en audit/xray/<as-of>-<sha8>/")
    sp.set_defaults(fn=cmd_xray)

    sp = sub.add_parser(
        "graph",
        help="señales estructurales del grafo (subconjunto sin backend externo de GRAPH)")
    sp.add_argument("--scope", choices=sorted(graph_mod.SCOPES), default="all",
                    help="ámbito analizado (default: all = wiki + genome + index)")
    sp.add_argument("origen", nargs="?", help="camino más corto: página de origen")
    sp.add_argument("destino", nargs="?", help="camino más corto: página de destino")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(fn=cmd_graph)

    sp = sub.add_parser("verify", help="todos los invariantes mecánicos de una vez")
    sp.add_argument("--quick", action="store_true", help="solo espejo + ledger")
    sp.add_argument("--exclude", default=None, metavar="CODIGOS",
                    help="códigos de lint a silenciar; 'temporales' excluye los que "
                         "dependen del calendario (uso típico: pre-commit)")
    sp.add_argument("--as-of", default=None)
    sp.set_defaults(fn=cmd_verify)
    return p


def _force_utf8_io() -> None:
    """La salida de la CLI es UTF-8 en TODA plataforma. Windows canaliza en
    cp1252 por defecto, lo que corrompe '·', '≡', '→', '✔' y los acentos
    (y hace fallar al consumidor que lee UTF-8, p. ej. el CI o un pipe)."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def main(argv: list[str] | None = None) -> int:
    _force_utf8_io()
    args = build_parser().parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
