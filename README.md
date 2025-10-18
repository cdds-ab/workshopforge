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

### Design-Grenzen: Was WorkshopForge IST und NICHT IST

**WorkshopForge ist ein Quality Gate, kein Content Creator.**

**✅ Was WorkshopForge leistet:**
- **Struktur-Generierung**: Scaffolding für Workshops (READMEs, CI-Configs, Meta-Slides)
- **Policy Enforcement**: Automatische Qualitätsprüfung gegen definierte Regeln
- **Content Validation**: Evidenzbasierte Prüfung von Slides (Kognitionsforschung)
- **Spec Management**: YAML-basierte Single Source of Truth
- **AI Orchestration**: Unterstützung für spec-getriebene Content-Anpassungen

**❌ Was WorkshopForge NICHT leistet:**
- **KEINE vollautomatische Slide-Generierung**: Detaillierte didaktische Inhalte (z.B. 800+ Zeilen Workshop-Slides) werden von Experten/KI erstellt, nicht von Templates
- **KEIN Ersatz für Fachexpertise**: WorkshopForge validiert Inhalte, erstellt sie aber nicht
- **KEINE AI-Content-Pipeline**: Templates sind für Scaffolding, nicht für didaktisch aufbereitete Lehrinhalte

**Empfohlener Workflow:**
1. **Content Creation**: Experte oder KI-Assistant erstellt detaillierte Slides/Labs
2. **Validation**: WorkshopForge prüft Inhalte gegen Policies (SlideContentRule, etc.)
3. **Scaffolding**: WorkshopForge generiert Struktur-Dateien (README, CI, Meta-Info)

## Features

- ✅ **Deterministische Generierung**: Reproduzierbare Ergebnisse aus Specs
- ✅ **KI-Orchestrierung**: `plan` (ohne Writes) → `apply` (mit Policy-Checks)
- ✅ **Policy Engine**: Konfigurierbare Regeln für Vollständigkeit, Struktur, Qualität
- ✅ **Session-Stabilität**: Spec-Hash verhindert Drift durch Kontext-Verlust
- ✅ **Provider-Abstraktion**: Echo (Test), OpenAI, Anthropic (stubs)
- ✅ **Compliance Reports**: JSON + Markdown Reports nach jedem Apply
- ✅ **Evidenzbasierte Content-Validierung**: Wissenschaftlich fundierte Qualitätsprüfung von Slides basierend auf Kognitionsforschung

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

## Content-Validierung (Wissenschaftlich Fundiert)

WorkshopForge validiert generierte Inhalte gegen **evidenzbasierte kognitionswissenschaftliche Prinzipien**, um optimale Lerneffektivität zu gewährleisten.

### Wissenschaftliche Grundlagen

Die Validierungsregeln basieren auf aktueller Forschung:

- **Working Memory Capacity**: 3-5 Items für Erwachsene (Cowan, 2010)
- **Attention Span**: ~8 Sekunden fokussierte Aufmerksamkeit (2024)
- **Cognitive Load Theory**: Minimierung externer kognitiver Belastung (Sweller et al., 2019)
- **Chunking-Prinzip**: Gruppierung reduziert Arbeitsgedächtnisbelastung
- **Mayer's Multimedia Principles**: Wörter + Bilder besser als Wörter allein

### Slide-Validierung

```bash
# Validiere generierte Slides
uv run workshopforge validate-content out/instructor/slides

# Beispiel-Output:
❌ Found 93 content violations:

out/instructor/slides/day2-modules.md:
  Line 119: [code-block-length] Code block has 20 lines (max 12).
            Split into multiple slides with (1/2), (2/2) notation.
  Line 595: [bullet-count] Slide has 6 bullet points (max 5).
            Split content across multiple slides.
  Line 514: [total-content] Slide has 20 content lines (max 15).
            Split into multiple slides - Cognitive Load Theory suggests less is better.
```

### Validierungsregeln

#### Code-Blöcke (max 12 Zeilen)
**Wissenschaftliche Grundlage**: Chunking-Prinzip für Programmier-Novizen
- Forschung zeigt: Beispiele, die Instruktoren klein erscheinen, überfordern Novizen leicht
- Live-Coding-Studien: Instruktoren können nur 2x so schnell gehen wie Lernende (nicht 10x wie mit Slides)
- **Regel**: Code-Beispiele in verdauliche Stücke aufteilen
- **Lösung**: Split mit (1/2), (2/2) Notation

#### Bullet Points (max 5)
**Wissenschaftliche Grundlage**: Working Memory Limit
- Miller's 7±2 Regel, verfeinert zu 3-5 Items (Cowan, 2010)
- Studien zeigen: Bei Slides mit vielen Bullet-Points lesen Lernende nur einen Bruchteil
- **Regel**: Maximal 5 Aufzählungspunkte pro Folie
- **Lösung**: Inhalt auf mehrere Folien verteilen

#### Gesamt-Content (max 15 Zeilen)
**Wissenschaftliche Grundlage**: Coherence Principle
- "Je weniger auf einer Folie, desto besser" - insbesondere für Lernoptimierung
- Dual-Channel-Überladung vermeiden: Text nicht vorlesen, der auf Folie steht
- **Regel**: Maximal 15 Content-Zeilen (inkl. Code, Bullets, Text)
- **Lösung**: Komplexe Inhalte über mehrere Folien zeigen

### Best Practices aus der Forschung

✅ **Empfohlen**:
- Live-Coding-Demonstrationen statt statischer Code-Slides
- Ein Konzept pro Folie (single-concept pieces)
- Parsons Problems für Code-Übungen (reduziert Syntax-Recall-Burden)
- Wörter mit relevanten Bildern paaren (Mayer's Multimedia Principle)
- Labels in Diagramme integrieren (vermeidet Split Attention)

❌ **Vermeiden**:
- Folien-Text vorlesen (Dual-Channel-Überladung)
- Dekorative Bilder ohne Lernunterstützung
- Komplexe Diagramme + dichten Text auf gleicher Folie kombinieren

### Konfiguration in ai_guidelines.md

Die Validierungsregeln werden in `spec/ai_guidelines.md` definiert:

```markdown
### Slide Size Constraints (Evidence-Based)

**Mandatory Limits:**
- **Max code block**: 10-12 lines per slide (chunking principle)
- **Max bullet points**: 5 per slide (working memory limit)
- **Max total text lines**: 15 lines including bullets, code, and text
- **Split long examples**: Use numbered slides (1/2, 2/2, 3/3)
```

### Integration in Workflow

```bash
# 1. Workshop generieren
uv run workshopforge generate --target out/instructor

# 2. Content validieren
uv run workshopforge validate-content out/instructor

# 3. Bei Violations: ai_guidelines.md anpassen und regenerieren
vim spec/ai_guidelines.md
uv run workshopforge ai apply "Split oversized slides according to CLT principles"

# 4. Erneut validieren
uv run workshopforge validate-content out/instructor
```

### Wissenschaftliche Referenzen

- Cowan, N. (2010). The Magical Mystery Four: How is Working Memory Capacity Limited, and Why? *Current Directions in Psychological Science*
- Sweller, J., van Merriënboer, J. J. G., & Paas, F. (2019). Cognitive Architecture and Instructional Design: 20 Years Later. *Educational Psychology Review*
- Mayer, R. E. (2021). Multimedia Learning (3rd ed.). Cambridge University Press
- PLOS Computational Biology (2018). Ten quick tips for teaching programming

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

### Anthropic (Claude)

```bash
# 1. Get API Key from https://console.anthropic.com/settings/keys
export ANTHROPIC_API_KEY=sk-ant-...

# 2. Use with WorkshopForge
uv run workshopforge ai plan "..." --provider anthropic
uv run workshopforge ai apply "..." --provider anthropic
```

**Features:**
- Uses Claude 3.5 Sonnet (latest model)
- Excellent code generation quality
- Long context window (200k tokens)
- Prepaid credit system (see https://console.anthropic.com)

**Costs (approximate):**
- Input: ~$3 per 1M tokens
- Output: ~$15 per 1M tokens
- Workshop content generation: ~$0.50-2.00 per module

**Setup:**
1. Create account at https://console.anthropic.com
2. Navigate to API Keys (https://console.anthropic.com/settings/keys)
3. Click "Create API Key"
4. Copy key and set environment variable
5. Purchase initial credits (e.g. $5, $20, $50)

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

- **[AI Usage Guide](forge/AI_USAGE_GUIDE.md)** - Umfassende Anleitung für LLMs und Entwickler zur effektiven Nutzung von WorkshopForge
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

Die Guide wird automatisch aus `forge/AI_USAGE_GUIDE.md` geladen. Bei Code-Änderungen (CLI, Provider, Policies) prüft ein Pre-commit Hook, ob die Dokumentation aktualisiert werden muss.

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
