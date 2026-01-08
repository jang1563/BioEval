#!/bin/bash
# BioEval Quick Start Script
# Run this on your local machine

set -e

echo "=============================================="
echo "BioEval Setup & Evaluation"
echo "=============================================="

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: ANTHROPIC_API_KEY not set"
    echo "Run: export ANTHROPIC_API_KEY='your-key-here'"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -e . --quiet

# Run dry-run first to verify setup
echo ""
echo "Verifying setup (dry run)..."
python scripts/run_evaluation.py --dry-run --component all

# Ask user to proceed
echo ""
read -p "Setup verified. Run full evaluation? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Running full evaluation..."
    python scripts/run_evaluation.py --model claude-sonnet-4-20250514 --component all
    
    echo ""
    echo "=============================================="
    echo "Evaluation complete! Results saved in results/"
    echo "Open notebooks/01_results_analysis.ipynb to visualize"
    echo "=============================================="
fi
