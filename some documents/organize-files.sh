#!/bin/bash

# Script to organize all documentation and design files into docs/ folder
# Run this from the project root directory

echo "🗂️  Organizing project files..."

# Create docs structure
mkdir -p docs/design/{analysis-class-models,design-class-models,sequence-diagrams,activity-diagrams,state-diagrams,use-case-diagrams,database-erd}
mkdir -p docs/planning
mkdir -p docs/implementation
mkdir -p docs/vrt

# Move UML diagrams to docs/design/
echo "📊 Moving UML diagrams..."

# Analysis class models (root .puml files)
mv 01-core-user-management.puml docs/design/analysis-class-models/ 2>/dev/null
mv 02-organization-types.puml docs/design/analysis-class-models/ 2>/dev/null
mv 03-bug-bounty-core.puml docs/design/analysis-class-models/ 2>/dev/null
mv 04-triage-validation.puml docs/design/analysis-class-models/ 2>/dev/null
mv 05-payment-system.puml docs/design/analysis-class-models/ 2>/dev/null
mv 06-simulation-environment.puml docs/design/analysis-class-models/ 2>/dev/null
mv 07-ptaas-system.puml docs/design/analysis-class-models/ 2>/dev/null
mv 08-code-review.puml docs/design/analysis-class-models/ 2>/dev/null
mv 09-ssdlc-integration.puml docs/design/analysis-class-models/ 2>/dev/null
mv 10-live-hacking-events.puml docs/design/analysis-class-models/ 2>/dev/null
mv 11-ai-red-teaming.puml docs/design/analysis-class-models/ 2>/dev/null
mv 12-communication-system.puml docs/design/analysis-class-models/ 2>/dev/null
mv 13-analytics-dashboard.puml docs/design/analysis-class-models/ 2>/dev/null
mv 14-audit-logging.puml docs/design/analysis-class-models/ 2>/dev/null
mv 15-researcher-matching.puml docs/design/analysis-class-models/ 2>/dev/null
mv analysis-class-model-complete.puml docs/design/analysis-class-models/ 2>/dev/null
mv analysis-class-model-summary.md docs/design/analysis-class-models/ 2>/dev/null

# Design class models
mv design-model docs/design/design-class-models/ 2>/dev/null
mv design-class-model-complete.puml docs/design/design-class-models/ 2>/dev/null
mv design-model-completion-summary.md docs/design/design-class-models/ 2>/dev/null

# Sequence diagrams
mv sequence-diagrams docs/design/ 2>/dev/null

# Activity diagrams
mv activity-diagrams docs/design/ 2>/dev/null

# State diagrams
mv state-diagrams docs/design/ 2>/dev/null

# Use case diagrams
mv use-case-diagrams docs/design/ 2>/dev/null
mv use-case-diagram.puml docs/design/use-case-diagrams/ 2>/dev/null

# Database ERD
mv database-erd docs/design/ 2>/dev/null
mv database-schema-erd.puml docs/design/database-erd/ 2>/dev/null
mv database-schema-erd-extended.puml docs/design/database-erd/ 2>/dev/null
mv database-schema-README.md docs/design/database-erd/ 2>/dev/null
mv database-schema.sql docs/design/database-erd/ 2>/dev/null

# Architecture diagrams
mv updated-architectural-design.puml docs/design/ 2>/dev/null
mv component-diagram.puml docs/design/ 2>/dev/null
mv deployment-diagram.puml docs/design/ 2>/dev/null
mv deployment-diagram-aws.puml docs/design/ 2>/dev/null
mv authentication-architecture.puml docs/design/ 2>/dev/null
mv multi-platform-navigation.puml docs/design/ 2>/dev/null
mv dashboard-layouts.puml docs/design/ 2>/dev/null

# Move planning documents
echo "📋 Moving planning documents..."
mv RAD-ANALYSIS-SUMMARY.md docs/planning/ 2>/dev/null
mv BUGCROWD-COMPARISON.md docs/planning/ 2>/dev/null
mv README-DIAGRAMS.md docs/planning/ 2>/dev/null
mv authentication-system-design.md docs/planning/ 2>/dev/null

# Move implementation documents
echo "🚀 Moving implementation documents..."
mv IMPLEMENTATION-ROADMAP.md docs/implementation/ 2>/dev/null
mv IMPLEMENTATION-READY.md docs/implementation/ 2>/dev/null
mv PROJECT-STRUCTURE.md docs/implementation/ 2>/dev/null
mv RECOMMENDED-STRUCTURE.md docs/implementation/ 2>/dev/null
mv STRUCTURE-COMPARISON.md docs/implementation/ 2>/dev/null
mv FOLDER-STRUCTURE-VISUAL.md docs/implementation/ 2>/dev/null
mv QUICK-START-GUIDE.md docs/implementation/ 2>/dev/null
mv updated-implementation-methodology.md docs/implementation/ 2>/dev/null

# Move VRT documents
echo "🔍 Moving VRT documents..."
mv VRT-INTEGRATION.md docs/vrt/ 2>/dev/null
mv VRT-REWARD-MAPPING.md docs/vrt/ 2>/dev/null
mv VRT-IMPLEMENTATION-PLAN.md docs/vrt/ 2>/dev/null
mv VRT-DECISION-SUMMARY.md docs/vrt/ 2>/dev/null

# Keep these in root (important for project)
echo "📌 Keeping essential files in root..."
# docker-compose.yml - stays in root
# .env.example - stays in root
# Final year project documentation one.txt - stays in root (RAD)

# Create a README in docs/
cat > docs/README.md << 'EOF'
# Documentation

This folder contains all project documentation organized by category.

## 📁 Structure

### design/
Complete UML diagrams and design models:
- `analysis-class-models/` - 15 analysis class models
- `design-class-models/` - 16 design class models
- `sequence-diagrams/` - 8 sequence diagrams
- `activity-diagrams/` - 13 activity diagrams
- `state-diagrams/` - 12 state diagrams
- `use-case-diagrams/` - 5 use case diagrams
- `database-erd/` - Database schema and ERD

### planning/
Project planning and analysis:
- RAD analysis summary
- Bugcrowd comparison
- Authentication system design
- Diagram documentation

### implementation/
Implementation guides and structure:
- Implementation roadmap (16 weeks)
- Project structure documentation
- Folder structure guides
- Quick start guide
- Structure comparison

### vrt/
Bugcrowd VRT integration:
- VRT integration guide
- Reward tier mapping
- Implementation plan
- Decision summary

## 📊 Diagram Count

- **Total UML Diagrams**: 80+
- **Analysis Models**: 15
- **Design Models**: 16
- **Behavioral Diagrams**: 38
- **Structural Diagrams**: 11+

## 🎯 Key Documents

1. **RAD Document**: `../Final year project documentation one.txt`
2. **Implementation Roadmap**: `implementation/IMPLEMENTATION-ROADMAP.md`
3. **Recommended Structure**: `implementation/RECOMMENDED-STRUCTURE.md`
4. **VRT Integration**: `vrt/VRT-INTEGRATION.md`

---

**Team**: Niway Tadesse, Abraham Asimamaw, Melkamu Tesfa  
**Advisor**: Yosef Worku  
**Institution**: Bahir Dar University
EOF

echo ""
echo "✅ Organization complete!"
echo ""
echo "📁 New structure:"
echo "   docs/"
echo "   ├── design/           (All UML diagrams)"
echo "   ├── planning/         (Analysis & planning docs)"
echo "   ├── implementation/   (Implementation guides)"
echo "   └── vrt/              (VRT integration docs)"
echo ""
echo "📌 Files kept in root:"
echo "   - docker-compose.yml"
echo "   - .env.example"
echo "   - Final year project documentation one.txt (RAD)"
echo ""
echo "🎉 Done! Your workspace is now organized."
