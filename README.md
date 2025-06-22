<<<<<<< HEAD
# Helix: Agentic RAG Test Automation Platform

## Patent-Pending 10-Layer Element Identification System

A revolutionary test automation platform that uses 10 hierarchical layers to identify UI elements across Salesforce, SAP, Workday, and Oracle with 95%+ accuracy and complete coverage guarantee.

## Core Innovation: 10-Layer Architecture

### Core Layers (1-6)
1. **Semantic Intent Recognition**: Understands WHAT the element does
2. **Contextual Relationship Mapping**: Finds elements by their position relative to others
3. **Visual Fingerprinting**: Uses computer vision to identify elements
4. **Behavioral Pattern Recognition**: Identifies by how elements behave
5. **Structural Pattern Analysis**: Platform-specific DOM patterns
6. **Accessibility Bridge**: Uses ARIA and semantic HTML

### Enhanced Layers (7-10) - NEW
7. **Mutation Observation**: Tracks how elements change over time
8. **Timing Synchronization**: Handles WHEN elements appear/become interactive
9. **State Context Awareness**: Understands application state and user context
10. **ML Confidence Fusion**: Enhanced AI combining all 9 layers intelligently

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Docker Compose
docker-compose up -d

# Start the API server
uvicorn src.api.main:app --reload
```

## Project Structure

```
helix/
├── src/
│   ├── layers/          # 7 identification layers
│   ├── core/           # Universal Locator orchestrator
│   ├── platforms/      # Platform-specific adapters
│   ├── api/           # FastAPI service
│   ├── utils/         # Shared utilities
│   └── models/        # Data models
├── tests/             # Test suites
├── config/            # Configuration files
├── docs/              # Documentation
└── scripts/           # Deployment scripts
```

## Architecture Overview

The Universal Locator Algorithm orchestrates all 7 layers to find elements:

1. Check cache for previous successful strategy
2. Run layers 1-6 in parallel to generate strategies
3. Layer 7 (ML Fusion) combines results and assigns confidence scores
4. Try strategies in order of confidence until one succeeds
5. If all fail, use visual fallback (click at coordinates)
6. Record success/failure for self-learning

## Performance Targets

- Element found rate: >90%
- Time to find element: <2 seconds
- Cache hit rate: >60%
- Handle 1000 concurrent requests

## Supported Platforms

- Salesforce (Lightning & Classic)
- SAP (Fiori & GUI)
- Workday
- Oracle Cloud Applications

## License

Proprietary - Patent Pending
=======
# helix
HELIX: Hierarchical Element Location Intelligence eXpert - A 10-layer dynamic element identification system for cross-platform test automation
Commit
>>>>>>> db5b4880fedd8d10c0144138896abfd421d9100e
