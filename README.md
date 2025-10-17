# WorkshopForge

**Spec-first Workshop-Generator mit KI-Orchestrierung und Session-übergreifender Stabilität**

WorkshopForge ist ein Tool zur Erstellung und Pflege von Workshop-Materialien aus versionierten Spezifikationen. Es nutzt KI-Assistenz mit Policy-Enforcement, um sicherzustellen, dass generierte Inhalte konsistent bleiben – selbst über mehrere LLM-Sessions hinweg.

## Kernkonzept

### Das Problem
LLMs "vergessen" Kontext zwischen Sessions. Workshop-Materialien driften auseinander. Inkonsistenzen entstehen. Manuelle Korrekturen sind zeitaufwendig.

### Die Lösung
**WorkshopForge macht die Spezifikation zur Single Source of Truth:**

1. **Spec-first**: Alle Inhalte werden aus YAML-Specs (workshop.yml, modules.yml, profile.yml) abgeleitet
2. **Stable Prelude**: Jede KI-Operation erhält ein deterministisches, hashbares Spec-Prelude als Kontext
3. **Policy Gates**: Generierte Inhalte werden vor dem Schreiben gegen Compliance-Regeln geprüft
4. **Auditierbar**: Alle KI-Operationen werden mit Prompts, Preludes und Diffs protokolliert

## Features

- ✅ **Deterministische Generierung**: Reproduzierbare Ergebnisse aus Specs
- ✅ **KI-Orchestrierung**: `plan` (ohne Writes) → `apply` (mit Policy-Checks)
- ✅ **Policy Engine**: Konfigurierbare Regeln für Vollständigkeit, Struktur, Qualität
- ✅ **Session-Stabilität**: Spec-Hash verhindert Drift durch Kontext-Verlust
- ✅ **Provider-Abstraktion**: Echo (Test), OpenAI, Anthropic (stubs)
- ✅ **Compliance Reports**: JSON + Markdown Reports nach jedem Apply

## Installation

### Schnell-Installation (empfohlen)

```bash
# Installiert workshopforge mit einem Befehl
curl -sSL https://raw.githubusercontent.com/cdds-ab/workshopforge/main/install.sh | bash
```

Danach verfügbar als: `workshopforge`

### Alternative Installationsmethoden

```bash
# Mit uv (empfohlen)
uv tool install git+https://github.com/cdds-ab/workshopforge.git

# Mit pip direkt von GitHub
pip install git+https://github.com/cdds-ab/workshopforge.git

# Für Entwicklung: Repository klonen
git clone https://github.com/cdds-ab/workshopforge.git
cd workshopforge
make install
make hooks  # Installiert pre-commit hooks
```

### Voraussetzungen
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) wird automatisch installiert (wenn nicht vorhanden)
- Keine externen API-Keys für Echo-Provider (Test-Modus)

## Schnellstart

### 1. Workshop initialisieren

```bash
uv run workshopforge init my-workshop
cd my-workshop
```

Dies erstellt:
```
my-workshop/
  spec/
    workshop.yml       # Kern-Metadaten
    modules.yml        # Lernmodule mit Objectives
    profile.yml        # Generierungs-Profil
    project.md         # Storyline & Didaktik
    ai_guidelines.md   # KI-Generierungs-Richtlinien
```

### 2. Specs anpassen

Bearbeite `spec/workshop.yml`:

```yaml
id: docker-intro
title: Docker für Einsteiger
version: 1.0.0
audience: Entwickler ohne Container-Erfahrung
duration:
  groups: 1
  sessions_per_group: 3
  session_minutes: 120
policy:
  student_ai_usage: allowed
  license: CC-BY-4.0
```

Bearbeite `spec/modules.yml`:

```yaml
modules:
  - id: docker-basics
    title: Docker Grundlagen
    objective: Docker-Container erstellen und ausführen
    deliverables:
      - labs/docker-basics/README.md
      - labs/docker-basics/Dockerfile
    duration_minutes: 60

  - id: docker-compose
    title: Multi-Container Apps
    objective: Mehrere Services mit docker-compose orchestrieren
    deliverables:
      - labs/docker-compose/README.md
      - labs/docker-compose/docker-compose.yml
    duration_minutes: 90
    depends_on:
      - docker-basics
```

### 3. Validieren

```bash
uv run workshopforge validate
```

Prüft alle Specs gegen JSON-Schemas.

### 4. Generieren

```bash
uv run workshopforge generate --target out/instructor
```

Erstellt deterministisch:
```
out/instructor/
  README.md
  COURSE.md
  labs/docker-basics/README.md
  labs/docker-compose/README.md
  instructor/slides/slides.md
  instructor/notes/notes.md
  reference/
  .github/workflows/basic_checks.yml
```

### 5. Compliance prüfen

```bash
uv run workshopforge ai check --target-dir out/instructor
```

Erzeugt `reports/compliance.{json,md}` mit Violations.

### 6. Student-Pack erstellen

```bash
uv run workshopforge promote out/instructor out/student
```

Kopiert Materialien, entfernt `instructor/**` und `reference/**`.

## KI-Orchestrierung

### Plan erstellen (ohne Writes)

```bash
uv run workshopforge ai plan "Erweitere Modul docker-basics um Networking-Beispiele"
```

**Output:**
- Rationale (warum diese Änderungen)
- Schritte mit betroffenen Dateien
- Policy-Risiken
- Spec-Hash für Stabilität

Logs → `ai_logs/<timestamp>-<goal>/`

### Plan ausführen (mit Policy Gate)

```bash
uv run workshopforge ai apply "Erweitere Modul docker-basics um Networking-Beispiele"
```

**Pipeline:**
1. Generiere Prelude aus Specs (deterministisch, hashbar)
2. Rufe KI-Provider mit Prelude + Goal
3. Parse Antwort in Changes
4. Führe Policy-Checks auf staged Changes aus
5. **Block** bei Errors, **Warn** bei Warnings
6. Schreibe nur bei Success
7. Log alles: Prompt, Response, Diffs, Policy-Report

**Policy-Checks:**
- Module-Completeness: Alle Module haben Objectives, Deliverables, Duration
- Deliverable-Existence: Deklarierte Deliverables existieren
- Readme-Requirements: README erwähnt Spec-Konzepte
- Instructor-Separation: `instructor/` und `reference/` Directories vorhanden
- Forbidden-Patterns: Keine "TODO", "FIXME" in Student-Materials
- Naming-Convention: Module-IDs folgen `lowercase-with-dashes`

### Violations erlauben (explizit)

```bash
uv run workshopforge ai apply "..." --allow-violations naming-convention,forbidden-patterns
```

### Datei erklären

```bash
uv run workshopforge ai explain labs/docker-basics/README.md
```

Zeigt:
- Deliverable für Modul `docker-basics`
- Spec-Referenz: `modules.yml#docker-basics`
- Objective: ...

## Workflow-Beispiele

### Workflow 1: Neuer Workshop von Grund auf

```bash
# Initialisieren
uv run workshopforge init kubernetes-workshop
cd kubernetes-workshop

# Specs schreiben (editiere YAML-Dateien)
vim spec/workshop.yml
vim spec/modules.yml

# Validieren
uv run workshopforge validate

# Generieren
uv run workshopforge generate --target out/instructor

# Compliance
uv run workshopforge ai check --target-dir out/instructor

# Bei Violations: Specs anpassen, neu generieren
# Kein manuelles Editieren der generierten Dateien!

# Student-Pack
uv run workshopforge promote out/instructor out/student
```

### Workflow 2: Bestehenden Workshop mit KI erweitern

```bash
# Plan ansehen
uv run workshopforge ai plan "Füge ein Modul über Helm hinzu" --provider echo

# Wenn Plan gut aussieht: Apply
uv run workshopforge ai apply "Füge ein Modul über Helm hinzu"

# Compliance-Report prüfen
cat reports/compliance.md

# Bei Policy-Errors: Specs manuell anpassen
vim spec/modules.yml  # Helm-Modul hinzufügen
uv run workshopforge generate --target out/instructor

# Bei Success: Commit
git add spec/ out/ reports/
git commit -m "Add Helm module"
```

### Workflow 3: Spec-Drift verhindern

```bash
# Session 1: Plan erstellen
uv run workshopforge ai plan "Optimiere Lab-Instruktionen" > plan.txt
# Spec-Hash: abc123...

# Session 2 (nächster Tag): Specs wurden manuell geändert
vim spec/modules.yml  # Manuelles Edit

# Apply schlägt fehl mit Spec-Hash-Mismatch
uv run workshopforge ai apply "Optimiere Lab-Instruktionen"
# Error: Spec hash changed since last operation

# Lösung: Neuen Plan mit aktuellem Spec-Hash
uv run workshopforge ai plan "Optimiere Lab-Instruktionen"
uv run workshopforge ai apply "Optimiere Lab-Instruktionen"
```

## Architektur

```
workshopforge/
  forge/
    cli.py              # Typer CLI (init, validate, generate, promote, ai:*)
    loader.py           # Spec-Discovery & Merging
    validator.py        # JSON-Schema Validation
    generator.py        # Jinja2 Template Rendering
    orchestrator.py     # AI Plan/Apply Pipeline
    policies.py         # Policy Engine & Rules
    prelude.py          # Stable Prompt Prelude Generation
    reporters.py        # Compliance Report Generation
    providers/
      base.py           # AIProvider Interface
      echo.py           # Test Provider (deterministic)
      openai.py         # OpenAI Stub
      anthropic.py      # Anthropic Stub
  templates/            # Jinja2 Templates
  schemas/              # JSON Schemas
  examples/minimal/     # Beispiel-Workshop
```

## Provider

### Echo (Default, für Tests)

```bash
uv run workshopforge ai plan "..." --provider echo
```

- Keine API-Keys nötig
- Deterministisch
- Parsed Module aus Prelude
- Generiert Stub-Plans

### OpenAI (Stub)

```bash
export OPENAI_API_KEY=sk-...
uv run workshopforge ai plan "..." --provider openai
```

Implementierung TODO (siehe `forge/providers/openai.py`).

### Anthropic (Stub)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
uv run workshopforge ai plan "..." --provider anthropic
```

Implementierung TODO (siehe `forge/providers/anthropic.py`).

## Policy-Konfiguration

Standard-Policies können überschrieben werden in `spec/profile.yml`:

```yaml
quality:
  rules:
    module-completeness:
      enabled: true
      severity: error
    forbidden-patterns:
      enabled: true
      severity: warn
      patterns:
        - TODO
        - FIXME
```

## Logging & Auditierung

Alle KI-Operationen werden geloggt:

```
ai_logs/2025-10-16T14-30-00Z-add-helm-module/
  prelude.txt       # Spec-derived Prelude
  prompt.json       # User Goal + Operation
  response.txt      # AI Response
  plan.json         # Parsed Plan
  policy.json       # Compliance Check Results
```

State-Tracking in `.workshopforge/state.json`:

```json
{
  "spec_hash": "abc123...",
  "provider": "echo",
  "last_goal": "Add Helm module",
  "updated_at": "2025-10-16T14:30:00Z"
}
```

## Continuous Integration

Generierte Workflows in `.github/workflows/basic_checks.yml`:

```yaml
- run: uv run workshopforge validate --spec-dir spec
- run: uv run workshopforge ai check --spec-dir spec
```

Verhindert defekte Specs im Repository.

## Dokumentation

- **[AI Usage Guide](AI_USAGE_GUIDE.md)** - Umfassende Anleitung für LLMs und Entwickler zur effektiven Nutzung von WorkshopForge
- **[Quick Start](QUICKSTART.md)** - 5-Minuten Schnelleinstieg
- **[Testing Guide](TESTING.md)** - Manuelle Test-Szenarien
- **[Project Summary](PROJECT_SUMMARY.md)** - Architektur-Übersicht
- **[Features](FEATURES.md)** - Feature-Liste und Roadmap

### AI Usage Guide Command

Für AI-Assistenten steht ein spezielles Command zur Verfügung:

```bash
# Im Terminal anzeigen (formatiert)
workshopforge ai usage-prompt

# Als Plain Markdown ausgeben (für .claude/ai-usage-prompt.md)
workshopforge ai usage-prompt --plain

# Direkt in Datei speichern
workshopforge ai usage-prompt --plain > .claude/ai-usage-prompt.md
```

Die Guide wird automatisch aus `AI_USAGE_GUIDE.md` geladen. Bei Code-Änderungen (CLI, Provider, Policies) prüft ein Pre-commit Hook, ob die Dokumentation aktualisiert werden muss.

## FAQ

**Q: Kann ich generierte Dateien manuell editieren?**
A: **Nein!** Manuelle Edits werden beim nächsten `generate` überschrieben. Ändere immer die Specs.

**Q: Wie verhindere ich Drift über Sessions?**
A: Der Spec-Hash im State wird geprüft. Wenn Specs ändern, muss neu geplant werden.

**Q: Was wenn Policy-Checks zu streng sind?**
A: Nutze `--allow-violations RULE_ID` oder passe `spec/profile.yml` an.

**Q: Kann ich mehrere Workshops verwalten?**
A: Ja, jeder Workshop hat eigene `spec/` Directory. Nutze Git-Branches für Varianten.

**Q: Sind die KI-Providers produktionsreif?**
A: Echo-Provider ist vollständig funktional für Tests. OpenAI/Anthropic sind Stubs (TODO).

## Lizenz

MIT License – siehe `LICENSE`.

## Beitragen

Issues und Pull Requests willkommen auf GitHub!

---

**Made with ❤️ by the WorkshopForge Team**

*Tame your LLMs. Keep your workshops consistent.*
