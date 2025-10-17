# WorkshopForge - Kontext-Speicherpunkt

**Datum**: 2025-10-17
**Status**: Production-ready, AI Usage Guide + Pre-commit Hooks implementiert, Erstes Production Workshop erstellt
**Repository**: https://github.com/cdds-ab/workshopforge (PUBLIC)

## Aktueller Stand

### ✅ Vollständig implementiert

1. **Core Features**
   - Spec-Management (loader, validator mit JSON-Schema)
   - Deterministische Generierung (Jinja2 Templates)
   - Policy Engine (6 Default-Regeln)
   - AI Orchestrierung (plan/apply/check/explain)
   - Provider-System (Echo ✅, Anthropic ✅, OpenAI Stub)
   - CLI mit 9 Commands (Typer-based)

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

### 🔧 Letzte Updates (2025-10-17)

**1. Package Data Fix** (Commit: `ad291be`, `fb574dc`)
- Problem: Schemas, Templates, AI_USAGE_GUIDE.md nicht im installierten Package
- Lösung:
  - Schemas/Templates nach `forge/` verschoben
  - AI_USAGE_GUIDE.md nach `forge/` verschoben
  - MANIFEST.in aktualisiert
  - Pfade in cli.py angepasst (parent.parent → parent)
- Status: ✅ Installation von GitHub funktioniert vollständig

**2. AI Usage Guide + Pre-commit Hooks** (Commits: `1371758`, `508d19f`, `4205fd2`)
- Comprehensive AI_USAGE_GUIDE.md (basierend auf budjira pattern)
- `workshopforge ai usage-prompt` command (--plain flag für file output)
- Pre-commit infrastructure:
  - `.pre-commit-config.yaml` (ruff, hooks, standard checks)
  - `scripts/check_ai_usage_guide.py` (validates guide freshness)
  - Warnt wenn guide veraltet (blockt nicht)
- Integration in README.md dokumentiert
- Status: ✅ Pre-commit hooks funktionieren

**3. Production Workshop Created** (2025-10-17)
- `~/git/cdds/lab-terraform-basics` erfolgreich initialisiert
- Content von `terraform-schulung` migriert
- Erste echte Nutzung von WorkshopForge für Production-Workshop
- Status: ✅ Tool funktioniert end-to-end

**4. Anthropic Provider Implementation** (Commit: `3261457`)
- Vollständige Claude API Integration für Production Content-Generierung
- Implementierung:
  - `forge/providers/anthropic.py` mit complete() Methode
  - Claude 3.5 Sonnet (claude-3-5-sonnet-20241022) als Default-Modell
  - System/User Message Formatting (Anthropic-spezifisch)
  - Error Handling + hilfreiche Error-Messages
  - Default: temperature=0.7, max_tokens=4096
- Dependencies: `anthropic>=0.39.0` zu pyproject.toml hinzugefügt
- Dokumentation:
  - README.md: Setup-Anleitung, Kosten-Schätzungen
  - AI_USAGE_GUIDE.md: Provider-Vergleichstabelle, Use-Case-Empfehlungen
- Status: ✅ Implementiert, getestet (Import), bereit für API-Key

### 📦 Installation

```bash
# One-liner Installation
curl -sSL https://raw.githubusercontent.com/cdds-ab/workshopforge/main/install.sh | bash

# Oder mit uv
uv tool install git+https://github.com/cdds-ab/workshopforge.git
```

### 🧪 Test-Status (2025-10-17)

- ✅ CI Pipeline erfolgreich (3.10, 3.11, 3.12)
- ✅ Linting mit ruff + pre-commit hooks
- ✅ Formatting mit black/ruff-format
- ✅ Installation via GitHub (`uv tool install git+...`)
- ✅ Vollständiger Workflow getestet:
  - init → validate → generate → ai check → promote ✓
  - All commands functional with fresh install ✓
  - Schemas/Templates/AI_USAGE_GUIDE included in package ✓
- ✅ Production usage: lab-terraform-basics Workshop erstellt

## Neue Features (seit letztem Update)

### AI Usage Prompt Command
```bash
# Display in terminal (formatted)
workshopforge ai usage-prompt

# Plain markdown output (for .claude/ai-usage-prompt.md)
workshopforge ai usage-prompt --plain > .claude/ai-usage-prompt.md
```
- Lädt `forge/AI_USAGE_GUIDE.md` und zeigt es an
- Rich-formatiert oder plain markdown
- Perfekt für AI assistants und documentation

### Pre-commit Hooks System
```bash
# Install hooks
uv run pre-commit install
# OR
make hooks

# Run manually
uv run pre-commit run --all-files
```
Hooks:
- **ruff** - Linting + fixing
- **ruff-format** - Code formatting
- **check-ai-usage-guide** - Validates guide freshness when CLI/providers change
- **Standard hooks** - trailing whitespace, yaml/toml checks, etc.

## CLI Commands (aktuell 9)

### Core Commands
1. **init** - Initialize new workshop
2. **validate** - JSON-Schema validation of specs
3. **generate** - Materialize workshop from templates + specs
4. **promote** - Create student pack (remove instructor content)

### AI Commands
5. **ai plan** - Generate plan without writes (with spec-prelude)
6. **ai apply** - Execute plan (with policy gates)
7. **ai check** - Compliance check without writes
8. **ai explain** - Show spec references for file
9. **ai usage-prompt** - Display AI usage guide (NEW)

## Offene TODOs

### Kritisch
- [x] **Verify Package Installation** - ✅ Getestet, funktioniert
- [x] **Full Workflow Test** - ✅ Getestet, funktioniert
- [x] **AI Usage Guide** - ✅ Implementiert
- [x] **Pre-commit Hooks** - ✅ Implementiert
- [x] **Anthropic Provider implementieren** - ✅ Implementiert (Commit 3261457)

### Nice-to-Have (Future)
- [ ] **OpenAI Provider implementieren** - Stubs vorhanden in `forge/providers/openai.py`
- [ ] **Unit Tests (pytest)** - Test-Infrastruktur vorhanden, Tests fehlen
- [ ] **PyPI Publish** - Package ready, nur Publishing fehlt
- [ ] **Dynamic AI Usage Guide** - Template-basiert statt statisch (current: static file)
- [ ] **Marp Integration** - Slides direkt aus specs generieren
- [ ] **End-to-End Test mit Anthropic API** - Benötigt API Key + Credits

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
