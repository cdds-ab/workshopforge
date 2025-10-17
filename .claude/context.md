# WorkshopForge - Kontext-Speicherpunkt

**Datum**: 2025-10-16
**Status**: Installation erfolgreich, Package-Data-Fix committed
**Repository**: https://github.com/cdds-ab/workshopforge (PUBLIC)

## Aktueller Stand

### ✅ Vollständig implementiert

1. **Core Features**
   - Spec-Management (loader, validator mit JSON-Schema)
   - Deterministische Generierung (Jinja2 Templates)
   - Policy Engine (6 Default-Regeln)
   - AI Orchestrierung (plan/apply/check/explain)
   - Provider-System (Echo funktional, OpenAI/Anthropic Stubs)
   - CLI mit 8 Commands (Typer-based)

2. **Toolchain**
   - uv-basierte Entwicklungsumgebung
   - Makefile für install/test/lint/format
   - GitHub Actions CI (alle Tests ✅)
   - curl-basiertes Install-Script

3. **Dokumentation**
   - README.md (Deutsch, vollständig)
   - QUICKSTART.md (5-Minuten Start)
   - TESTING.md (Manuelle Tests)
   - PROJECT_SUMMARY.md (Übersicht)
   - FEATURES.md (Feature-Liste mit Roadmap)

### 🔧 Letzter Fix

**Problem**: Schemas und Templates wurden nicht mit installiert
**Lösung**:
- `MANIFEST.in` erstellt (schemas/*.json, templates/*.j2)
- `pyproject.toml` um package-data ergänzt
- Committed in: `655c8cc`

### 📦 Installation

```bash
# One-liner Installation
curl -sSL https://raw.githubusercontent.com/cdds-ab/workshopforge/main/install.sh | bash

# Oder mit uv
uv tool install git+https://github.com/cdds-ab/workshopforge.git
```

### 🧪 Letzter Test-Status

- ✅ CI Pipeline erfolgreich (3.10, 3.11, 3.12)
- ✅ Linting mit ruff
- ✅ Formatting mit black
- ✅ Installation via install.sh
- ⏳ Validate-Command nach Reinstall (noch zu testen)

## Offene TODOs

### Kritisch
- [ ] **Verify Package Installation**: Testen ob schemas/templates nach Install verfügbar sind
- [ ] **Full Workflow Test**: init → validate → generate → check durchlaufen

### Nice-to-Have
- [ ] OpenAI Provider implementieren
- [ ] Anthropic Provider implementieren
- [ ] Unit Tests (pytest)
- [ ] PyPI Publish

## Projekt-Struktur

```
workshopforge/
├── forge/                      # Python Package
│   ├── cli.py                 # 8 CLI Commands
│   ├── loader.py              # Spec Loading
│   ├── validator.py           # JSON-Schema Validation
│   ├── generator.py           # Template Rendering
│   ├── orchestrator.py        # AI Pipeline
│   ├── policies.py            # 6 Policy Rules
│   ├── prelude.py             # Stable Context Gen
│   ├── reporters.py           # JSON/MD Reports
│   ├── utils.py
│   └── providers/
│       ├── base.py
│       ├── echo.py            # ✅ Functional
│       ├── openai.py          # Stub
│       └── anthropic.py       # Stub
├── schemas/                    # JSON Schemas
│   ├── workshop.schema.json
│   ├── modules.schema.json
│   └── profile.schema.json
├── templates/                  # Jinja2 Templates
│   ├── repo/
│   └── docs/
├── examples/minimal/           # Beispiel-Workshop
├── .github/workflows/ci.yml    # CI Pipeline
├── install.sh                  # curl Installation
├── MANIFEST.in                 # Package Data
└── pyproject.toml             # Package Config
```

## Git Commits (letzte 5)

1. `655c8cc` - Fix package data inclusion (schemas/templates)
2. `9c27e3c` - Add curl-based installation script
3. `78e05f8` - Fix CI: Use venv in integration job
4. `cf96774` - Fix linting errors and update ruff config
5. `f8e4535` - Add GitHub Actions CI workflow

## Wichtige Befehle

```bash
# Entwicklung
cd /home/fthiele/git/cdds/workshopforge
make install              # Install editable
uv run workshopforge ...  # Run from project

# Global nutzen
workshopforge init my-workshop
workshopforge validate
workshopforge generate --target out/instructor
workshopforge ai check
workshopforge promote out/instructor out/student

# Tests
make test
make lint
make format
```

## Nächster Schritt

Nach Reinstallation testen:
```bash
cd /tmp/demo-workshop
workshopforge validate
workshopforge generate --target out/instructor
workshopforge ai check --target-dir out/instructor
```

Erwartetes Ergebnis: Schemas sollten jetzt gefunden werden ✅

## Kontakt & Links

- **Repository**: https://github.com/cdds-ab/workshopforge
- **CI Status**: https://github.com/cdds-ab/workshopforge/actions
- **Installation**: `curl -sSL https://raw.githubusercontent.com/cdds-ab/workshopforge/main/install.sh | bash`

---

**Kontext gespeichert**: 2025-10-16 15:45 UTC
**Letzter Commit**: 655c8cc
**Branch**: main
**Python**: 3.10+
**Status**: Production-ready (PoC)
