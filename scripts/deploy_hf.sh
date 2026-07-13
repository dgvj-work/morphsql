#!/usr/bin/env bash
# Deploy MorphSQL Space + model + dataset to Hugging Face Hub
set -euo pipefail

SPACE_ID="${1:-dgvj-work/sqlshift-ai}"
MODEL_ID="${2:-dgvj-work/sqlshift-ai}"
DATASET_ID="${3:-dgvj-work/vertica-snowflake-pairs}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Deploying MorphSQL to Hugging Face..."
echo "  Space:   $SPACE_ID"
echo "  Model:   $MODEL_ID"
echo "  Dataset: $DATASET_ID"
echo ""

python -c "from sqlshift.eval.pairs import ensure_pairs_file; print(ensure_pairs_file())"
python -c "from pathlib import Path; from sqlshift.ai.risk_model import MODEL_PATH, train_and_save; train_and_save() if not Path(MODEL_PATH).exists() else print(MODEL_PATH)"

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

rsync -a \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude '*.egg-info' \
  --exclude 'migration-output' \
  --exclude '.pytest_cache' \
  --exclude 'canvases' \
  --exclude '*.pyc' \
  "$ROOT/" "$STAGE/"

# Space README must be the Hub metadata card
cp README_HF_SPACE.md "$STAGE/README.md"

echo "Uploading Space: $SPACE_ID"
hf upload "$SPACE_ID" "$STAGE" . --repo-type=space

echo "Uploading model: $MODEL_ID"
# Model card lives at MODEL_CARD.md; Hub model README is model/README.md
STAGE_MODEL="$(mktemp -d)"
cp -R "$ROOT/model/." "$STAGE_MODEL/"
cp "$ROOT/MODEL_CARD.md" "$STAGE_MODEL/README.md" 2>/dev/null || true
# Prefer dedicated model README if present
if [[ -f "$ROOT/model/README.md" ]]; then
  cp "$ROOT/model/README.md" "$STAGE_MODEL/README.md"
fi
hf upload "$MODEL_ID" "$STAGE_MODEL" . --repo-type=model || {
  echo "Model upload failed — create https://huggingface.co/models/$MODEL_ID first (or login with write token)."
}
rm -rf "$STAGE_MODEL"

echo "Publishing dataset: $DATASET_ID"
python scripts/publish_dataset.py --repo "$DATASET_ID" || {
  echo "Dataset publish failed (login required). Space upload may still have succeeded."
}

echo ""
echo "Done"
echo "  Space:   https://huggingface.co/spaces/$SPACE_ID"
echo "  Model:   https://huggingface.co/$MODEL_ID"
echo "  Dataset: https://huggingface.co/datasets/$DATASET_ID"
