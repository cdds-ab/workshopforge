# Anthropic Provider Test Guide

## Setup (Once)

### 1. Get API Key
1. Go to https://console.anthropic.com/settings/keys
2. Click "Create API Key"
3. Name it "WorkshopForge"
4. Copy the key (starts with `sk-ant-...`)
5. Purchase initial credits (e.g. $5, $20, $50)

### 2. Set Environment Variable
```bash
# Add to your ~/.bashrc or ~/.zshrc for persistence
export ANTHROPIC_API_KEY=sk-ant-your-key-here

# Or set for current session only
export ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Verify Setup
```bash
cd ~/git/cdds/workshopforge
uv run workshopforge ai plan --provider anthropic --goal "test" 2>&1 | head -20
```

**Expected:** Should NOT show "ANTHROPIC_API_KEY environment variable not set"

---

## Test 1: Simple Plan Generation

```bash
cd ~/git/cdds/lab-terraform-basics

# Generate plan for theory module
workshopforge ai plan \
  --provider anthropic \
  --goal "Generate Marp slides for terraform-basics module based on spec objectives and legacy slides"
```

**Expected Output:**
- Plan displayed in terminal
- Log created in `ai_logs/<timestamp>-<goal>/`
- Files: `plan.json`, `prelude.txt`, `prompt.txt`, `response.txt`

**Verify:**
```bash
ls -lh ai_logs/
cat ai_logs/*/response.txt | head -50
```

---

## Test 2: Apply Plan (Generate Content)

```bash
cd ~/git/cdds/lab-terraform-basics

# IMPORTANT: Make sure you're in lab-terraform-basics, NOT workshopforge!

# Generate slides
workshopforge ai apply \
  --provider anthropic \
  --goal "Generate Marp slides for terraform-basics module. Create out/instructor/instructor/slides/day1-terraform-basics.md with:
  1. Title slide with module info
  2. Section: What is Infrastructure as Code?
  3. Section: Why Terraform?
  4. Section: HCL Syntax Basics
  5. Section: Terraform Workflow (init/plan/apply/destroy)
  6. Section: State Management Intro
  Use Marp syntax with --- separators. Reference spec/modules.yml objectives."
```

**Expected:**
- Plan generated
- Policy checks run
- Content written to `out/instructor/instructor/slides/day1-terraform-basics.md`
- Compliance report in `reports/compliance.{json,md}`

**Verify:**
```bash
# Check if slide file was created
ls -lh out/instructor/instructor/slides/

# View first 50 lines
head -50 out/instructor/instructor/slides/day1-terraform-basics.md

# Check compliance
cat reports/compliance.md
```

---

## Test 3: Compliance Check

```bash
cd ~/git/cdds/lab-terraform-basics

# Run compliance check
workshopforge ai check --target-dir out/instructor
```

**Expected:**
- Policy engine runs
- Report generated in `reports/compliance.{json,md}`
- Shows any violations (missing deliverables, guideline issues)

**Verify:**
```bash
cat reports/compliance.md
```

---

## Test 4: Generate Lab Content

```bash
cd ~/git/cdds/lab-terraform-basics

# Generate instructor notes for existing lab
workshopforge ai apply \
  --provider anthropic \
  --goal "Generate comprehensive instructor notes for Lab A (dev-sandbox). Create out/instructor/instructor/notes/lab-a-notes.md with:
  - Learning objectives recap
  - Common student mistakes
  - Troubleshooting tips
  - Time management (60min total)
  - Extension ideas for advanced students
  Reference existing lab files in out/instructor/labs/lab-a-dev-sandbox/"
```

**Expected:**
- Notes file created at `out/instructor/instructor/notes/lab-a-notes.md`
- Content references actual lab code
- Follows instructor notes structure

---

## Cost Monitoring

After each test, check your credit usage:
1. Go to https://console.anthropic.com/settings/billing
2. View "Usage" tab

**Estimated costs for tests above:**
- Test 1 (plan only): ~$0.01-0.05
- Test 2 (slide generation): ~$0.20-0.50
- Test 3 (compliance check): Free (local policy engine)
- Test 4 (notes generation): ~$0.30-0.80

**Total for all tests:** ~$0.50-1.50

---

## Troubleshooting

### Error: "ANTHROPIC_API_KEY environment variable not set"
**Fix:** Export the key in your current shell:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

### Error: "anthropic package not installed"
**Fix:** Reinstall WorkshopForge:
```bash
cd ~/git/cdds/workshopforge
uv sync
uv tool uninstall workshopforge
uv tool install .
```

### Error: "401 Unauthorized" or "403 Forbidden"
**Fix:**
- Verify API key is correct
- Check if credits are available at https://console.anthropic.com

### Error: "429 Too Many Requests"
**Fix:** Wait 60 seconds, API rate limit exceeded

### Generation quality issues
**Tips:**
- Be more specific in your goal statement
- Reference spec files explicitly ("based on spec/modules.yml objectives")
- Mention output format (Marp, Markdown, code comments)
- Reference existing files to maintain consistency

---

## Next Steps After Testing

If all tests pass:

1. **Generate remaining theory modules:**
   ```bash
   cd ~/git/cdds/lab-terraform-basics

   # Variables/Outputs/State module
   workshopforge ai apply --provider anthropic --goal "..."

   # Modules module
   workshopforge ai apply --provider anthropic --goal "..."

   # Remote State module
   workshopforge ai apply --provider anthropic --goal "..."

   # Best Practices module
   workshopforge ai apply --provider anthropic --goal "..."
   ```

2. **Generate instructor notes for Labs B-D**

3. **Generate reference materials:**
   - Terraform workflow cheatsheet
   - Variable types reference
   - Backend configuration guide
   - Security checklist
   - Troubleshooting guide
   - Cost optimization tips

4. **Build PDFs:**
   ```bash
   make slides
   ```

5. **Create student version:**
   ```bash
   workshopforge promote out/instructor out/student
   ```

---

## Success Criteria

✅ **WorkshopForge + Anthropic is working if:**
- `ai plan` shows intelligent, context-aware plans
- `ai apply` generates high-quality content
- Generated content follows spec objectives
- Compliance checks pass (or violations are expected)
- Content is usable without major manual editing

---

**Happy Testing!** 🚀

If you encounter issues, check:
1. API key is set correctly
2. Credits are available
3. You're in the correct directory (lab-terraform-basics, not workshopforge)
4. Specs are valid (`workshopforge validate`)
