# WorkshopForge - AI Usage Guide

This guide helps LLMs (and humans) understand how to effectively use WorkshopForge for creating and maintaining workshop materials.

## ⚠️ CRITICAL: Design Boundaries

**WorkshopForge is a Quality Gate, NOT a Content Creator.**

### What WorkshopForge DOES
- ✅ **Scaffolding**: Generate workshop structure (READMEs, CI configs, meta-slides)
- ✅ **Validation**: Check content against policies (structure, naming, cognitive load)
- ✅ **Policy Enforcement**: Block non-compliant content from being committed
- ✅ **Spec Management**: YAML-driven single source of truth
- ✅ **AI Orchestration**: Support spec-driven content adjustments

### What WorkshopForge DOES NOT DO
- ❌ **Detailed Content Generation**: Does NOT create 800+ line didactic slide decks
- ❌ **Replace Expertise**: Does NOT write pedagogically rich workshop materials
- ❌ **Automatic AI Content Pipeline**: Templates are for structure, not learning content

### Correct Mental Model
```
┌──────────────────────────────────────────────────────────────┐
│  Expert/AI Creates Content                                   │
│  ├── Detailed slides (day1-terraform-basics.md: 800 lines)   │
│  ├── Lab exercises with solutions                            │
│  └── Reference materials with examples                       │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│  WorkshopForge Validates & Scaffolds                         │
│  ├── SlideContentRule checks cognitive load                  │
│  ├── PolicyEngine enforces quality standards                 │
│  ├── Generates READMEs, CI configs, meta-slides              │
│  └── Reports: compliance.md with violations                  │
└──────────────────────────────────────────────────────────────┘
```

### Recommended Workflow
1. **Content Creation**: Expert or AI assistant writes detailed slides/labs
2. **Validation**: `workshopforge validate-content slides/` → finds violations
3. **Quality Gate**: Fix violations before committing
4. **Scaffolding**: `workshopforge generate` → creates structure files

**NEVER expect WorkshopForge templates to generate pedagogically rich content.**

## Core Principles

### 1. Spec-First Approach
**The specification is the single source of truth.**

- All workshop content derives from YAML specs (`workshop.yml`, `modules.yml`, `profile.yml`)
- Never edit generated files directly - always update specs and regenerate
- Specs are version-controlled, generated outputs are ephemeral
- Use `workshopforge validate` before any generation to ensure spec correctness

### 2. Session-Spanning Stability
**Prevent context drift between AI sessions.**

- Every AI operation receives a **stable prelude** (deterministic spec context)
- Spec hash tracking prevents divergence when LLM "forgets" previous context
- Always check `.workshopforge/state.json` for last operation and spec hash
- If spec changed, previous AI plans may be invalid - regenerate plan

### 3. Policy-Driven Compliance
**Generated content must pass compliance gates.**

- Use `workshopforge ai plan` first (read-only, safe)
- Review plan output before applying
- Run `workshopforge ai apply` only after plan approval
- Check `reports/compliance.md` after apply for violations
- Fix policy errors before committing changes

### 4. Deterministic Generation
**Templates ensure reproducible outputs.**

- `workshopforge generate` always produces identical results from same specs
- Jinja2 templates define structure, specs provide content
- Use this for initial scaffolding and structure updates
- AI operations enhance content within generated structure

## Workflow Patterns

### Pattern 1: New Workshop Creation
```bash
# 1. Initialize
workshopforge init my-workshop
cd my-workshop

# 2. Customize specs
# Edit spec/workshop.yml, spec/modules.yml, spec/profile.yml

# 3. Validate
workshopforge validate

# 4. Generate structure
workshopforge generate --target out/instructor

# 5. AI-enhance content (optional)
workshopforge ai plan --goal "Add detailed examples to intro module"
workshopforge ai apply  # After reviewing plan

# 6. Compliance check
workshopforge ai check --target-dir out/instructor

# 7. Create student version
workshopforge promote out/instructor out/student
```

### Pattern 2: Iterative Content Enhancement
```bash
# 1. Always start with validation
workshopforge validate

# 2. Plan changes (read-only)
workshopforge ai plan --goal "Improve slide deck with diagrams"

# 3. Review plan output in ai_logs/

# 4. Apply if satisfied
workshopforge ai apply

# 5. Check compliance
workshopforge ai check --target-dir out/instructor

# 6. Fix violations if any (update specs or AI guidelines)
# Edit spec/ai_guidelines.md to guide future AI operations

# 7. Regenerate if needed
workshopforge generate --target out/instructor --force
```

### Pattern 3: Troubleshooting Generated Content
```bash
# 1. Find spec reference for problematic file
workshopforge ai explain --file out/instructor/labs/intro/README.md

# 2. Update relevant spec or guideline
# Edit spec/modules.yml or spec/ai_guidelines.md

# 3. Regenerate
workshopforge generate --target out/instructor --force

# 4. Verify compliance
workshopforge ai check --target-dir out/instructor
```

## Best Practices for AI Operations

### Planning Goals
**Be specific and scoped:**

✅ Good:
- "Add code examples with comments to intro-python module labs"
- "Create slide deck for data-structures module covering lists and dicts"
- "Improve instructor notes with common student questions"

❌ Bad:
- "Make workshop better" (too vague)
- "Rewrite everything" (too broad, violates spec-first principle)
- "Add external library examples" (may violate guidelines in spec/ai_guidelines.md)

### Reviewing Plans
**Always review before applying:**

1. Check prelude in `ai_logs/<timestamp>-<goal>/plan.md`
2. Verify spec hash matches current state
3. Ensure plan doesn't contradict spec guidelines
4. Look for policy violations in plan comments
5. Confirm plan scope matches your goal

### Handling Policy Violations

**Error-level violations block apply:**
```
Error: COMPLETENESS_CHECK
  - Missing required instructor notes for module: advanced-topics
  - Fix: Update spec/modules.yml or regenerate
```

**Warning-level violations are informational:**
```
Warning: NAMING_CONVENTIONS
  - File uses non-standard naming: MyLab.md (prefer my_lab.md)
  - Consider: Align with profile naming conventions
```

**Fix strategy:**
1. Update specs to align with policies
2. Adjust policies in code if they're too strict
3. Update AI guidelines to prevent future violations

## Understanding the Spec Files

### workshop.yml
**Core metadata and policies:**
```yaml
id: unique-workshop-id        # Used in generated filenames
title: Workshop Display Name   # Used in headers
version: 1.0.0                 # Semantic versioning
audience: Target learners      # Guides content difficulty
duration:                      # Affects module sizing
  groups: 1
  sessions_per_group: 3
  session_minutes: 120
policy:                        # Compliance rules
  student_ai_usage: allowed    # Affects generate behavior
  license: CC-BY-4.0           # Copyright footer
```

### modules.yml
**Learning modules with objectives:**
```yaml
- id: intro-python             # Used in URLs and paths
  title: Python Introduction   # Display name
  duration_minutes: 90         # Affects content depth
  objectives:                  # Drives lab generation
    - Understand variables
    - Use basic data types
  prerequisites: []            # Dependencies
```

### profile.yml
**Generation settings:**
```yaml
formats:
  labs: markdown               # Output format
  slides: markdown             # Slide format
naming:
  lab_prefix: lab              # File naming
  case: snake_case             # Naming convention
redactions:                    # For promote command
  student:
    - "instructor/*"
    - "**/*_solution.py"
```

### project.md
**Storyline and didactic approach:**

Use this to guide AI operations with narrative context.
Example: "Workshop follows a project-based approach building a REST API."

### ai_guidelines.md
**Rules for AI content generation:**

Define constraints like:
- Code style requirements
- Language level (beginner/advanced)
- Forbidden libraries or patterns
- Expected output formats

## Provider Selection

### Echo Provider (Default)
**For testing and development:**
```bash
# No API key needed, deterministic test output
workshopforge ai plan --provider echo --goal "test plan"
```

**Characteristics:**
- No external API calls
- No API key required
- Parses specs and generates stub plans
- Useful for testing workflows, CI/CD
- Does NOT generate actual content (only plans)

**Use when:**
- Testing WorkshopForge infrastructure
- Validating specs without costs
- CI/CD pipeline testing
- Learning WorkshopForge commands

### Anthropic Provider (Claude)
**Recommended for production content generation:**
```bash
# 1. Get API key: https://console.anthropic.com/settings/keys
export ANTHROPIC_API_KEY=sk-ant-...

# 2. Use with WorkshopForge
workshopforge ai plan --provider anthropic --goal "Generate slides for terraform-basics"
workshopforge ai apply --provider anthropic --goal "Generate slides for terraform-basics"
```

**Characteristics:**
- Model: Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)
- Context window: 200k tokens (can process large specs)
- Excellent code generation quality
- Strong reasoning for complex instructions
- Prepaid credit system (~$3/1M input tokens, ~$15/1M output tokens)

**Use when:**
- Generating workshop content (slides, labs, notes)
- Complex multi-file operations
- Need high-quality code examples
- Working with large specs (multiple modules)

**Costs (estimated):**
- Slide deck (1 module): ~$0.20-0.50
- Lab with README + code: ~$0.30-0.80
- Full workshop (5-10 modules): ~$2-5

### OpenAI Provider
**Alternative production provider (stub - not yet implemented):**
```bash
# Implementation pending
export OPENAI_API_KEY=sk-...
workshopforge ai plan --provider openai --goal "..."
```

**When implemented, use for:**
- Alternative to Anthropic
- GPT-4 Turbo for cost optimization
- Organization with existing OpenAI contracts

### Provider Comparison

| Feature | Echo | Anthropic | OpenAI (stub) |
|---------|------|-----------|---------------|
| **Cost** | Free | ~$3-15/1M tokens | TBD |
| **Setup** | None | API key + credits | API key |
| **Content Quality** | Test only | Excellent | TBD |
| **Context Window** | N/A | 200k tokens | 128k (GPT-4) |
| **Speed** | Instant | 30-60s/module | TBD |
| **Use Case** | Testing | Production | Future |

## Common Mistakes to Avoid

### ❌ Editing Generated Files Directly
**Problem:** Changes are lost on next `generate`
**Solution:** Update specs, then regenerate

### ❌ Skipping Validation
**Problem:** Invalid specs cause cryptic generation errors
**Solution:** Always run `validate` before `generate`

### ❌ Applying Without Planning
**Problem:** Unexpected changes, no review opportunity
**Solution:** Use `plan` → review → `apply` workflow

### ❌ Ignoring Compliance Reports
**Problem:** Policy violations accumulate, content drifts
**Solution:** Review `reports/compliance.md` after every apply

### ❌ Committing Generated Outputs
**Problem:** Large diffs, merge conflicts
**Solution:** Commit specs only, regenerate outputs in CI/CD

### ❌ Using AI to Fix Spec Violations
**Problem:** AI patches symptoms, not root cause
**Solution:** Fix specs directly, then regenerate

## Advanced Usage

### Custom Templates
1. Copy templates from `forge/templates/` to project
2. Edit templates with custom structure
3. Point `generate` to custom template dir:
   ```bash
   workshopforge generate --template-dir custom_templates/
   ```

### Custom Policies
1. Extend `forge/policies.py` with new rules
2. Register in `PolicyEngine.default_policies()`
3. Configure severity in `workshop.yml` (future feature)

### CI/CD Integration
```yaml
# .github/workflows/validate.yml
name: Validate Workshop Specs
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: astral-sh/setup-uv@v1
      - run: uv tool install git+https://github.com/cdds-ab/workshopforge.git
      - run: workshopforge validate
      - run: workshopforge generate --target out/instructor
      - run: workshopforge ai check --target-dir out/instructor
```

## Debugging Tips

### Spec Loading Issues
```bash
# Check which specs are found
workshopforge validate --verbose  # Future feature

# Manually inspect merged spec
python -c "from forge.loader import SpecLoader; l = SpecLoader('spec'); print(l.load())"
```

### Template Rendering Issues
- Check Jinja2 syntax in templates
- Verify spec keys match template variable names
- Use `--force` to overwrite existing outputs

### AI Provider Issues
```bash
# Test provider configuration
export WORKSHOPFORGE_PROVIDER=echo
workshopforge ai plan --goal "test"

# Check logs for API errors
cat ai_logs/latest/plan.md
```

## Getting Help

- **Documentation:** Check README.md, QUICKSTART.md
- **Examples:** See `examples/minimal/` for reference workshop
- **Issues:** https://github.com/cdds-ab/workshopforge/issues
- **Validation:** Run `workshopforge validate` first

## Summary

**Three Golden Rules:**
1. 📋 **Specs are truth** - Always update specs, never generated files
2. 🔍 **Plan before apply** - Review AI operations before execution
3. ✅ **Validate constantly** - Check specs and compliance after changes

**Recommended Flow:**
```
init → edit specs → validate → generate → ai plan → review → ai apply → check → promote
```

This ensures consistent, compliant, and maintainable workshop materials across sessions.
