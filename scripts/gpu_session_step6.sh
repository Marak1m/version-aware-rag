#!/usr/bin/env bash
# GPU session step 6 extras: serving noise and leak audit per model, then the L1 arm.
set -u
cd /home/vansh/code/version-aware-rag
export PATH=$HOME/.local/bin:$PATH
V="uv run varag"
latest() { ls -d runs/*-"$1"-*/ | sort | tail -1 | xargs basename; }
for model in primary vllm_large; do
  $V serve start --model "$model" || exit 1
  $V run --methods all --model "$model" --split dev --user-arm knows --instances configs/noise_subset_dev.txt --fresh-cache | tail -2
  A=$(latest "$model")
  $V run --methods all --model "$model" --split dev --user-arm knows --instances configs/noise_subset_dev.txt --fresh-cache | tail -2
  B=$(latest "$model")
  echo "NOISE $model $A $B"
  $V run --methods all --model "$model" --split dev --user-arm leak_audit | tail -2
  echo "LEAK $model $(latest "$model")"
  $V serve stop --model "$model"
done
$V serve start --model primary_genconfig || exit 1
$V serve check --model primary_genconfig | grep -v "^    |"
$V run --methods plain_rag --model primary_genconfig --split dev --user-arm knows | tail -2
echo "L1 $(latest primary_genconfig)"
$V serve stop --model primary_genconfig
echo STEP6-DONE
