#!/usr/bin/env bash
# Install git-commit-helper for AMP Code
# Copies slash commands, Python scripts, and documentation to ~/.config/amp/

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}🚀 Installing git-commit-helper for AMP Code${NC}"
echo ""

# Determine config directory (respect XDG_CONFIG_HOME)
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/amp"

echo -e "${BLUE}📁 Installation directory: $CONFIG_DIR${NC}"
echo ""

# Create directories
echo "Creating directories..."
mkdir -p "$CONFIG_DIR/commands"
mkdir -p "$CONFIG_DIR/scripts"
mkdir -p "$CONFIG_DIR/git-commit-helper"

# Copy slash commands
echo ""
echo "Copying slash commands..."
for cmd in commit-msg pr-restructure pr-create pr-update; do
    if [[ -f "$SCRIPT_DIR/.agents/commands/$cmd" ]]; then
        cp "$SCRIPT_DIR/.agents/commands/$cmd" "$CONFIG_DIR/commands/"
        chmod +x "$CONFIG_DIR/commands/$cmd"
        echo -e "  ${GREEN}✓${NC} /$cmd"
    else
        echo -e "  ${RED}✗${NC} /$cmd (not found at $SCRIPT_DIR/.agents/commands/$cmd)"
        exit 1
    fi
done

# Copy Python scripts
echo ""
echo "Copying Python scripts..."
for script in analyze_diff.py find_base_branch.py; do
    if [[ -f "$SCRIPT_DIR/scripts/$script" ]]; then
        cp "$SCRIPT_DIR/scripts/$script" "$CONFIG_DIR/scripts/"
        chmod +x "$CONFIG_DIR/scripts/$script"
        echo -e "  ${GREEN}✓${NC} $script"
    else
        echo -e "  ${RED}✗${NC} $script (not found)"
        exit 1
    fi
done

# Copy SKILL.md and references for @-mention support
echo ""
echo "Copying reference documentation..."
cp -r "$SCRIPT_DIR/git-commit-helper" "$CONFIG_DIR/"
echo -e "  ${GREEN}✓${NC} git-commit-helper/SKILL.md"
echo -e "  ${GREEN}✓${NC} git-commit-helper/references/"

# Copy AGENTS.md
cp "$SCRIPT_DIR/AGENTS.md" "$CONFIG_DIR/AGENTS.md"
echo -e "  ${GREEN}✓${NC} AGENTS.md"

echo ""
echo -e "${GREEN}✅ Installation complete!${NC}"
echo ""
echo -e "${YELLOW}📋 Available commands in AMP Code:${NC}"
echo "  /commit-msg  - Generate commit message from staged changes"
echo "  /pr-restructure  - Find base branch and prepare for PR analysis"
echo "  /pr-create   - Create pull request with auto-generated description"
echo "  /pr-update   - Update existing PR description"
echo ""
echo -e "${YELLOW}🔧 Requirements:${NC}"
echo "  ✓ Python 3.6+"
echo "  ✓ Git 2.23+"
echo "  ✓ gh CLI (GitHub CLI) for PR commands"
echo ""
echo -e "${BLUE}💡 Quick Start:${NC}"
echo "  1. Stage your changes: ${YELLOW}git add <files>${NC}"
echo "  2. In AMP Code, type: ${YELLOW}/commit-msg${NC}"
echo "  3. AMP will analyze and help you write a commit message"
echo ""
echo -e "${BLUE}📚 Documentation:${NC}"
echo "  - Installed at: $CONFIG_DIR/git-commit-helper/"
echo "  - AGENTS.md: $CONFIG_DIR/AGENTS.md"
echo "  - Chris Beams' rules: https://cbea.ms/git-commit/"
echo "  - AMP Code manual: https://ampcode.com/manual"
