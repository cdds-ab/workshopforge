# WorkshopForge Quickstart

Du hast **5 Minuten**? Hier ist der schnellste Weg, um mit WorkshopForge zu starten.

## 1. Installation (30 Sekunden)

```bash
# Einfach per curl installieren
curl -sSL https://raw.githubusercontent.com/cdds-ab/workshopforge/main/install.sh | bash
```

Das wars! `workshopforge` ist jetzt verfügbar.

**Alternative:**
```bash
# Mit uv
uv tool install git+https://github.com/cdds-ab/workshopforge.git

# Mit pip
pip install git+https://github.com/cdds-ab/workshopforge.git
```

## 2. Erstelle deinen ersten Workshop (1 Minute)

```bash
workshopforge init mein-workshop
cd mein-workshop
```

Dies erstellt:
- `spec/workshop.yml` – Metadaten (Titel, Version, Audience)
- `spec/modules.yml` – Lernmodule mit Objectives
- `spec/profile.yml` – Generierungs-Einstellungen

## 3. Passe die Specs an (2 Minuten)

Editiere `spec/workshop.yml`:

```yaml
id: docker-basics
title: Docker Crashcourse
version: 1.0.0
audience: Entwickler ohne Container-Erfahrung
```

Editiere `spec/modules.yml`:

```yaml
modules:
  - id: docker-intro
    title: Was ist Docker?
    objective: Container-Konzepte verstehen und erste Images erstellen
    deliverables:
      - labs/docker-intro/README.md
      - labs/docker-intro/Dockerfile
    duration_minutes: 90
```

## 4. Generiere den Workshop (30 Sekunden)

```bash
workshopforge validate
workshopforge generate --target out/instructor
```

Output:
```
out/instructor/
  ├── README.md              # Workshop-Übersicht
  ├── COURSE.md              # Kursplan mit Schedule
  ├── labs/
  │   └── docker-intro/
  │       └── README.md      # Lab-Instruktionen
  ├── instructor/
  │   ├── slides/slides.md   # Slide-Deck
  │   └── notes/notes.md     # Dozenten-Notizen
  └── .github/workflows/     # CI Checks
```

## 5. Prüfe Compliance (30 Sekunden)

```bash
workshopforge ai check --target-dir out/instructor
cat reports/compliance.md
```

Zeigt:
- ✅ Module vollständig?
- ❌ Deliverables fehlen? (z.B. `Dockerfile`)
- ⚠️ Warnings (z.B. "TODO" in Student-Files)

## 6. Erstelle Student-Pack (20 Sekunden)

```bash
workshopforge promote out/instructor out/student
```

Entfernt automatisch:
- `instructor/` Directory
- `reference/` Directory

Student-Pack ist ready für Distribution! 🚀

---

## Was kommt als Nächstes?

### Nutze KI für Anpassungen

```bash
# Plan erstellen (kein Write)
workshopforge ai plan "Füge ein Modul über docker-compose hinzu"

# Plan ausführen (mit Policy-Check)
workshopforge ai apply "Füge ein Modul über docker-compose hinzu"
```

**Wichtig**: Standard-Provider ist `echo` (Test-Modus). Für echte AI-Generierung musst du OpenAI/Anthropic Provider konfigurieren (siehe README).

### Verstehe die Struktur

```bash
# Zeige Spec-Referenzen für File
workshopforge ai explain "labs/docker-intro/README.md"
```

Output:
```
Deliverable für Modul: docker-intro (modules.yml#docker-intro)
Objective: Container-Konzepte verstehen...
```

### Weitere Beispiele

Schau dir `examples/minimal/` an:
```bash
cd examples/minimal
cat spec/modules.yml
workshopforge generate --spec-dir spec --target out/test
```

---

## 💡 Wichtige Konzepte (1 Minute Lesezeit)

### Specs sind die Single Source of Truth
- ✅ Editiere immer nur die Specs, nie die generierten Files
- ✅ Generierte Files werden bei jedem `generate` neu erstellt
- ✅ Versioniere Specs in Git

### Policy Engine schützt vor Fehlern
- ❌ Fehlende Deliverables → Blocking Error
- ⚠️ "TODO" in Student-Files → Warning
- ✅ Alle Checks in `reports/compliance.md`

### AI ist optional
- 👍 `generate` funktioniert ohne AI (nur Templates)
- 🤖 `ai plan/apply` nutzt AI für Content-Generierung
- 🧪 Echo-Provider ist Test-Modus (keine echte AI)

---

## 🆘 Hilfe benötigt?

```bash
workshopforge --help
workshopforge ai --help
workshopforge <command> --help
```

Vollständige Dokumentation: `README.md`

---

**Viel Erfolg mit WorkshopForge!** 🚀

*Tipp: Starte mit dem Minimal-Beispiel (`examples/minimal/`) und passe es Schritt für Schritt an.*
