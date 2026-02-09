# Guide to Documentation

## 📚 Documentation Structure

This guide helps you find the right documentation for your task.

---

## 🏗️ Architecture & Design

### **UPSCALE_ARCHITECTURE_DECISIONS.md**
**When to read:** Understanding what was fixed and why  
**Contains:**
- YAML configuration requirements (scraper_class mapping)
- FilterEngine threshold discovery and solution
- ScraperFactory integration in monitor_engine
- Article model flexibility for multiple source types
- FilterEngine supporting Article objects and dicts
- Configuration loading order patterns

**Best for:**
- Learning why certain architectural patterns exist
- Understanding design decisions made during testing
- Debugging configuration-related issues
- Adding new features that follow established patterns

---

### **UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md**
**When to read:** Adding a new data source  
**Contains:**
- Core Article fields (required) vs optional fields
- Field specifications by source type (Web scraper, RSS, API)
- How different sources provide different metadata
- Field handling best practices for scrapers
- Configuration requirements for sources.yaml
- FilterEngine configuration for different source types
- Testing checklist for new sources
- Troubleshooting guide

**Best for:**
- Adding new scraper (RSS feed, web portal, API)
- Understanding Article model field requirements
- Testing and debugging scrapers
- Configuration tuning for different sources

---

## 🚀 Getting Started

### **For New RSS Feed Integration**
1. Start with: **UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md** - "Type 2: RSS Feed" section
2. Reference: **UPSCALE_ARCHITECTURE_DECISIONS.md** - "Article Model Must Accept Optional Fields"
3. Use: Testing checklist in UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md

### **For New Web Scraper Integration**
1. Start with: **UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md** - "Type 1: Web Scraper" section
2. Reference: **UPSCALE_ARCHITECTURE_DECISIONS.md** - All decisions apply
3. Use: Testing checklist in UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md

### **For Understanding System Architecture**
1. Read: **UPSCALE_ARCHITECTURE_DECISIONS.md** - Overview section
2. Review: **UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md** - Configuration Requirements section
3. Check: README.md - Project structure

---

## 📋 By Task

### **I want to add a new scraper**
→ **UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md**
- Identify source type (Web, RSS, API)
- Follow "Integration Steps" for your type
- Use "Testing New Source" checklist
- Reference "Troubleshooting" if issues

### **I need to understand why something is configured a certain way**
→ **UPSCALE_ARCHITECTURE_DECISIONS.md**
- Find the relevant decision section
- Read "Issue Found" to understand the problem
- Read "Solution" and "Rationale" to understand why

### **Configuration is breaking, articles not filtering**
→ **UPSCALE_ARCHITECTURE_DECISIONS.md** Section 2
- Check: FilterEngine min_confidence threshold
- Check: sources.yaml has scraper_class field
- Reference: UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md - Troubleshooting

### **New scraper finds articles but none pass filters**
→ **UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md**
- Check: Department keywords in filters.yaml match content
- Check: Confidence threshold appropriate for source type
- Reference: UPSCALE_ARCHITECTURE_DECISIONS.md - Section 2 (Confidence Threshold)

### **Getting "unexpected keyword argument" errors**
→ **UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md** - "Field Handling Best Practices"
- Understand: Not all fields go to Article.__init__
- Learn: How to handle source-specific fields
- See: Code examples in parse_article() section

---

## 🔄 Development Workflow

### **Phase 1: New Source Discovery**
```
Your source → UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md
              ↓
              Identify source type (Web/RSS/API)
              ↓
              Review "Type X" section
              ↓
              Plan integration
```

### **Phase 2: Implementation**
```
Create scraper → Reference UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md
                 ↓
                 Handle Article fields properly
                 ↓
                 Add to config/sources.yaml
                 ↓
                 Test isolation
```

### **Phase 3: Debugging Issues**
```
Issue occurs → Check UPSCALE_ARCHITECTURE_DECISIONS.md
              ↓
              Review relevant decision
              ↓
              Check UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md
              ↓
              Troubleshooting section
```

---

## 📖 File Reference

### Core Documentation

| File | Purpose | Audience |
|------|---------|----------|
| **UPSCALE_ARCHITECTURE_DECISIONS.md** | Why system is designed this way | Developers, architects |
| **UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md** | How to add new sources | New developers, integrators |
| **README.md** | Project overview & quick start | Everyone |

### Implementation Files (code examples in docs)

- `UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md` - Complete parse_article() examples
- `UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md` - Date parsing helper
- `UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md` - Testing code snippets

---

## 🎯 Key Concepts Explained Across Docs

### **Article Model Flexibility**
- **Why**: Different sources provide different fields
- **Where explained**: UPSCALE_ARCHITECTURE_DECISIONS.md Section 4
- **Implementation**: UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md - Field Handling

### **FilterEngine Threshold Tuning**
- **Why**: Different sources have different keyword density
- **Where explained**: UPSCALE_ARCHITECTURE_DECISIONS.md Section 2
- **How to apply**: UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md - Confidence Threshold Notes

### **ScraperFactory Pattern**
- **Why**: Scales to unlimited sources without code changes
- **Where explained**: UPSCALE_ARCHITECTURE_DECISIONS.md Section 3
- **Implementation**: UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md - Configuration Requirements

### **Configuration-Driven Design**
- **Why**: Central control, no code redeploys needed
- **Where explained**: All three docs show config examples
- **Files affected**: config/sources.yaml, config/filters.yaml

---

## ✅ Checklist: Before Adding New Source

- [ ] Read: UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md - identify source type
- [ ] Read: UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md - "Integration Steps" for your type
- [ ] Review: UPSCALE_ARCHITECTURE_DECISIONS.md - understand core patterns
- [ ] Check: config/sources.yaml format in examples
- [ ] Prepare: Scraper class with fetch_articles() and parse_article()
- [ ] Plan: Article fields your source will provide
- [ ] Test: Using checklist in UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md

---

## 📝 Contributing to Docs

When you discover a new issue or pattern:

1. **If it's about WHY something is designed a way**
   → Add to UPSCALE_ARCHITECTURE_DECISIONS.md

2. **If it's about HOW to integrate a source**
   → Add to UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md

3. **If it's a common question**
   → Update this guide_to_docs.md with Q&A section

---

## 🔗 Quick Links

- **Understand Article field requirements** → UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md - "Article Model - Core vs Optional Fields"
- **Learn about FilterEngine** → UPSCALE_ARCHITECTURE_DECISIONS.md Section 2 & 5
- **See RSS integration example** → UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md - "Type 2: RSS Feed"
- **Troubleshoot parse errors** → UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md - "Troubleshooting"
- **Test new scraper** → UPSCALE_SOURCE_INTEGRATION_REQUIREMENTS.md - "Testing New Source"

---

**Last Updated:** 2026-02-09  
**Status:** Complete architectural documentation  
**Next Update:** After integration of 3rd source (API example)
