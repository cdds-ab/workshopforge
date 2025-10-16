# WorkshopForge Testing Guide

## Manuelle Tests durchgeführt ✅

### 1. Installation
```bash
make install
# ✅ Erfolg: venv mit Python 3.10 erstellt, alle Dependencies installiert
```

### 2. Grundbefehle
```bash
uv run workshopforge --version
# ✅ Output: workshopforge version 0.1.0

uv run workshopforge --help
# ✅ Zeigt alle Commands: init, validate, generate, promote, ai

uv run workshopforge ai --help
# ✅ Zeigt AI-Subcommands: plan, apply, check, explain
```

### 3. Validierung (Minimal-Beispiel)
```bash
uv run workshopforge validate --spec-dir examples/minimal/spec
# ✅ Output: "✓ All specs valid!"
```

### 4. Generierung
```bash
uv run workshopforge generate --spec-dir examples/minimal/spec \
  --target examples/minimal/out/instructor
# ✅ Erstellt vollständige Workshop-Struktur:
#    - README.md, COURSE.md
#    - labs/intro-python/README.md
#    - labs/data-structures/README.md
#    - instructor/slides/slides.md
#    - instructor/notes/notes.md
#    - reference/.keep
#    - .github/workflows/basic_checks.yml
```

### 5. Compliance Check
```bash
uv run workshopforge ai check --spec-dir examples/minimal/spec \
  --target-dir examples/minimal/out/instructor
# ✅ Output: "Violations found: Errors: 3, Warnings: 0"
# ✅ Erstellt reports/compliance.{json,md}
# ✅ Erkannte Violations: Fehlende Deliverables (hello.py, calculator.py, collections.py)
```

**Compliance Report:**
- ✅ JSON-Schema konform
- ✅ Markdown human-readable
- ✅ Korrekte Fehler-Klassifizierung (deliverable-existence)

### 6. AI Plan (Echo Provider)
```bash
uv run workshopforge ai plan "Erstelle ein Modul über fortgeschrittene Python-Konzepte" \
  --spec-dir examples/minimal/spec
# ✅ Generiert deterministischen Plan
# ✅ Extrahiert Module aus Prelude (intro-python, data-structures)
# ✅ Zeigt Rationale, Steps, Policy Risks
# ✅ Gibt Spec-Hash aus (e01762322d551838)
# ✅ Logs in ai_logs/
```

### 7. Explain
```bash
uv run workshopforge ai explain "labs/intro-python/README.md" \
  --spec-dir examples/minimal/spec
# ✅ Zeigt Spec-Referenzen:
#    - Deliverable für Module intro-python & data-structures
#    - Objectives
#    - "Student-facing lab exercise"
```

### 8. Promote (Student Pack)
```bash
uv run workshopforge promote \
  examples/minimal/out/instructor \
  examples/minimal/out/student
# ✅ Kopiert Materialien
# ✅ Entfernt instructor/** und reference/**
# ✅ Student-Pack enthält nur:
#    - README.md, COURSE.md
#    - labs/
#    - .github/workflows/
```

### 9. Init (Neuer Workshop)
```bash
uv run workshopforge init examples/test-workshop
cd examples/test-workshop
uv run workshopforge validate
uv run workshopforge generate --target out/instructor
# ✅ Initialisiert neue Specs mit Beispiel-Daten
# ✅ Validierung erfolgreich
# ✅ Generierung erfolgreich
```

## Akzeptanzkriterien ✅

### Spec-Validierung
- ✅ JSON-Schema Validierung für workshop.yml, modules.yml, profile.yml
- ✅ Fehlermeldungen mit Pfad und Beschreibung

### Deterministische Generierung
- ✅ Wiederholte `generate` Aufrufe erzeugen identische Outputs
- ✅ Templates referenzieren Spec-Quellen (modules.yml#module-id)
- ✅ Module-Objectives, Deliverables, Duration korrekt übernommen

### Policy Engine
- ✅ 6 Default-Regeln implementiert:
  - module-completeness ✅
  - deliverable-existence ✅
  - readme-requirements ✅
  - instructor-separation ✅
  - forbidden-patterns ✅
  - naming-convention ✅
- ✅ Error vs. Warn Klassifizierung
- ✅ JSON + Markdown Reports

### AI Orchestrierung
- ✅ `plan`: Kein Write, nur Analyse
- ✅ `apply`: Mit Policy Gate (stub-only wegen Echo-Provider)
- ✅ `check`: Compliance ohne Writes
- ✅ `explain`: Traceability zu Specs
- ✅ Echo-Provider funktional für Tests
- ✅ OpenAI/Anthropic Stubs vorhanden

### Session-Stabilität
- ✅ Prelude-Generierung deterministisch
- ✅ Spec-Hash Berechnung
- ✅ State-Tracking in .workshopforge/state.json
- ✅ Logs in ai_logs/ mit Timestamps

### Promote
- ✅ Redaction-Patterns konfigurierbar
- ✅ Default: instructor/**, reference/**
- ✅ Student-Pack frei von Instructor-Content

## Bekannte Einschränkungen

1. **AI Providers**: OpenAI und Anthropic sind Stubs (NotImplementedError)
   - Echo-Provider ist vollständig funktional für Testing
   - Produktive AI-Nutzung erfordert Implementierung in `forge/providers/{openai,anthropic}.py`

2. **Apply Command**: Mit Echo-Provider nur Simulations-Änderungen
   - Schreibt keine echten Deliverable-Files
   - Produktive Nutzung erfordert echten AI-Provider

3. **Python Version**: Minimum 3.10 (wegen Type Hints)

## Nächste Schritte für Produktion

1. Implementiere OpenAI Provider:
   - `forge/providers/openai.py` ausbauen
   - Structured Output für Plan/Apply

2. Implementiere Anthropic Provider:
   - `forge/providers/anthropic.py` ausbauen
   - System-Message Handling

3. Erweitere Policy-Regeln:
   - Slide word-count limits
   - Code-Style Checks für Python-Deliverables
   - Link-Validierung in Markdown

4. Unit Tests:
   - pytest für alle Module
   - Policy-Rule Tests
   - Template-Rendering Tests

5. Integration Tests:
   - Full workflow: init → validate → generate → check
   - Multi-module Workshops
   - Error-Handling edge cases

## Ausführung des kompletten Test-Workflows

```bash
# Cleanup
rm -rf examples/test-run examples/minimal/out examples/minimal/reports

# Full workflow
make install
uv run workshopforge init examples/test-run
cd examples/test-run
uv run workshopforge validate
uv run workshopforge generate --target out/instructor
uv run workshopforge ai check --target-dir out/instructor
uv run workshopforge promote out/instructor out/student
cat reports/compliance.md
```

Erwartetes Ergebnis: Alle Commands erfolgreich, Compliance-Report zeigt fehlende Deliverables.
