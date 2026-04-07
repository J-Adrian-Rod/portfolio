#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────
#  Sonic Universe — Project Setup
#  Run once from the project root:  bash setup.sh
# ─────────────────────────────────────────────────────────
set -e

VENV_NAME=".venv"
KERNEL_NAME="sonic_universe"

echo "▶  Creating virtual environment: $VENV_NAME"
python3 -m venv "$VENV_NAME"

echo "▶  Activating and upgrading pip"
source "$VENV_NAME/bin/activate"
pip install --upgrade pip --quiet

echo "▶  Installing dependencies"
pip install -r requirements.txt --quiet

echo "▶  Registering Jupyter kernel: $KERNEL_NAME"
python -m ipykernel install --user --name "$KERNEL_NAME" --display-name "Python ($KERNEL_NAME)"

echo "▶  Creating output directory"
mkdir -p data/processed

echo ""
echo "✅  Setup complete!"
echo ""
echo "To activate the environment:"
echo "  source .venv/bin/activate"
echo ""
echo "To launch JupyterLab:"
echo "  source .venv/bin/activate && jupyter lab"
