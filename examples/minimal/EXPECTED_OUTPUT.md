# Expected Output Structure

When running `workshopforge generate --spec-dir examples/minimal/spec --target examples/minimal/out`,
the following structure should be created:

```
examples/minimal/out/
├── README.md                          # Workshop overview with modules
├── COURSE.md                          # Course guide with schedule
├── labs/                              # Student lab exercises
│   ├── intro-python/
│   │   └── README.md                 # Module-specific instructions
│   └── data-structures/
│       └── README.md
├── instructor/                        # Instructor-only materials
│   ├── slides/
│   │   └── slides.md                 # Slide deck (markdown)
│   └── notes/
│       └── notes.md                  # Teaching notes
├── reference/                         # Reference solutions
│   └── .keep
└── .github/
    └── workflows/
        └── basic_checks.yml          # CI validation workflow
```

## File Characteristics

### Deterministic Generation
All files should be generated identically on repeated runs (sorted traversals, stable timestamps in templates).

### Spec References
Generated files include references to their source specs:
- `modules.yml#intro-python`
- `modules.yml#data-structures`

### Content Alignment
- Module READMEs match objectives from `modules.yml`
- Deliverables listed match spec declarations
- Duration info reflects spec values
- Student AI policy matches spec setting

### Policy Compliance
Generated structure should pass all default policy checks:
- Module completeness
- Instructor/student separation
- README requirements
- Naming conventions
- No forbidden patterns (TODO, FIXME)

## Validation

After generation, run:

```bash
workshopforge validate --spec-dir examples/minimal/spec
workshopforge ai check --spec-dir examples/minimal/spec --target-dir examples/minimal/out
```

Both commands should succeed with no errors.
