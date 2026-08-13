#!/bin/bash
# Job Search Pipeline — One-time setup script

set -e

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║     Job Search Pipeline — Setup            ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# 1. Copy profile JSON from template (stays in project root — gitignored)
if [ -f claude-job-profile.json ]; then
  echo "✓ claude-job-profile.json already exists. Skipping copy."
else
  cp claude-job-profile.template.json claude-job-profile.json
  echo "✓ Copied profile template to claude-job-profile.json"
  echo "  → Open it and fill in your details before running /job-search"
fi

# 2. Copy CLAUDE.md from template
if [ -f CLAUDE.md ]; then
  echo "✓ CLAUDE.md already exists. Skipping copy."
else
  cp CLAUDE.template.md CLAUDE.md
  echo "✓ Created CLAUDE.md from template"
fi

# 3. Copy private context files from templates
mkdir -p context
if [ -f context/profile.md ]; then
  echo "✓ context/profile.md already exists. Skipping copy."
else
  cp context/profile.template.md context/profile.md
  echo "✓ Created context/profile.md from template"
  echo "  → Fill in your work experience, metrics, and skills"
fi

if [ -f context/preferences.md ]; then
  echo "✓ context/preferences.md already exists. Skipping copy."
else
  cp context/preferences.template.md context/preferences.md
  echo "✓ Created context/preferences.md from template"
  echo "  → Fill in your target roles, geography, and deal-breakers"
fi

# 4. Copy persona-specific skill templates (populated by /setup Phase 2.4)
for skill in archetypes jd-filter score-rubric; do
  if [ -f "skills/${skill}.md" ]; then
    echo "✓ skills/${skill}.md already exists. Skipping."
  else
    cp "skills/${skill}.template.md" "skills/${skill}.md"
    echo "✓ Created skills/${skill}.md from template"
    echo "  → Run /setup Phase 2.4 to populate with your target roles and background"
  fi
done

if [ -f "skills/star-library.md" ]; then
  echo "✓ skills/star-library.md already exists. Skipping."
else
  cp "skills/star-library.template.md" "skills/star-library.md"
  echo "✓ Created skills/star-library.md from template"
  echo "  → STAR stories build up over time as you run /interview-prep sessions"
fi

if [ -f "portals.yml" ]; then
  echo "✓ portals.yml already exists. Skipping."
else
  cp "portals.template.yml" "portals.yml"
  echo "✓ Created portals.yml from template"
  echo "  → Add your target companies and geography to portals.yml"
fi

# 6. Create working directories
mkdir -p working
echo "✓ working/ folder ready (gitignored — safe for intermediate outputs)"

mkdir -p scripts
echo "✓ scripts/ folder ready"

mkdir -p resumes
echo "✓ resumes/ folder ready (gitignored — temp PDFs go here)"

# 7. Activate pre-commit hook (blocks personal data from git commits)
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit 2>/dev/null || true
echo "✓ Pre-commit hook activated — personal data will be blocked from commits"

# 8. Check Claude Code is installed
if command -v claude &> /dev/null; then
  echo "✓ Claude Code is installed ($(claude --version))"
else
  echo "✗ Claude Code not found."
  echo "  → Install it: https://claude.ai/code"
  echo ""
fi

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║     Setup complete!                        ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "Required next steps (do these before running any commands):"
echo ""
echo "  1. Edit claude-job-profile.json with your API keys and Notion IDs"
echo "     → Adzuna:   https://developer.adzuna.com  (free, 250 req/day)"
echo "     → RapidAPI: https://rapidapi.com          (JSearch + Indeed Scraper, free tier)"
echo "     → Notion:   https://notion.so/profile/integrations  (create Internal Integration)"
echo ""
echo "  2. Set up Notion"
echo "     a. Create a Notion database with the schema in README.md"
echo "     b. Share the database with your Notion integration"
echo "        (Open database → ... → Connections → Add connection → select your integration)"
echo "     c. Copy the database ID from the URL into claude-job-profile.json under notion.database_id"
echo ""
echo "  3. Fill in your profile files"
echo "     → context/profile.md   — your experience, metrics, skills"
echo "     → context/preferences.md — target roles, geography, deal-breakers"
echo ""
echo "  4. Run the pipeline"
echo "     → Open this folder in Claude Code or Cowork: claude"
echo "     → Type: /setup  for an interactive guided walkthrough"
echo "     → Or type: /job-search  if you've already filled in your config"
echo ""
