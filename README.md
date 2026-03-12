# My Claude Skills

A collection of custom Claude Code skills for productivity and automation.

## 📦 Available Skills

### twitter-to-feishu

Extract Twitter/X articles and convert to Feishu-compatible Word documents with embedded images.

**Features:**
- ✅ Automatic Twitter/X article extraction
- ✅ Playwright-based image downloading (bypasses CDN restrictions)
- ✅ Generates Word documents with embedded images
- ✅ Direct import to Feishu/Lark

**Installation:**
```bash
npx skills add zzpwestlife/my-claude-skills/twitter-to-feishu
```

[View Documentation](twitter-to-feishu/README.md)

---

## 🚀 Quick Start

### Install from this marketplace

```bash
# Add this marketplace
claude plugin marketplace add zzpwestlife/my-claude-skills

# Install a specific skill
npx skills add twitter-to-feishu@my-claude-skills
```

### Install individual skills

Each skill can also be installed directly:

```bash
npx skills add zzpwestlife/my-claude-skills/twitter-to-feishu
```

## 📁 Repository Structure

```
my-claude-skills/
├── README.md                    # This file
├── twitter-to-feishu/          # Twitter to Feishu converter skill
│   ├── SKILL.md
│   ├── README.md
│   ├── scripts/
│   └── references/
└── [future-skill]/             # More skills coming soon
```

## 🛠️ Development

### Adding a new skill

1. Create a new directory for your skill
2. Follow the Claude Code skill structure:
   ```
   skill-name/
   ├── SKILL.md          # Required: skill definition
   ├── README.md         # Recommended: installation guide
   ├── scripts/          # Optional: executable scripts
   ├── references/       # Optional: reference documentation
   └── assets/           # Optional: templates and resources
   ```
3. Test the skill locally
4. Commit and push to this repository

### Testing locally

```bash
# Link the skill for local testing
cd my-claude-skills/skill-name
claude skill link .
```

## 📝 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

- GitHub: [@your-username](https://github.com/your-username)
- Issues: [Report a bug](https://github.com/your-username/my-claude-skills/issues)

## 🌟 Acknowledgments

Built with [Claude Code](https://claude.ai/code) and inspired by the Claude Skills ecosystem.
