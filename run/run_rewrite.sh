#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"

TRAJ_ROOT="trajectory/conversations-clean"
OUTPUT_ROOT="trajectory/conversations-rewritten"
KEY_INFO_ROOT="data/extra_data"

# Configure tasks directly here. Leave empty to process all discovered tasks.
TASK_LIST=(
    ###### Bioinformatics & Life Sciences
    "dna-frame2-translation"
    "scikit-bio-sequence"
    "scikit-bio-alignment"
    "scikit-survival-cox"
    "population-genetics-hwe"
    "matchms-count-spectra"
    "matchms-similarity"
    "protein-expression-analysis"
    "variant-annotation"
    "vcf-pass-count"
    "medchem-ro5-pass"
    "medchem-lilly-demerit"
    ######## Chemistry & Molecular Sciences
    "molecular-analysis"
    "molecular-dynamics-rmsd"
    "computational-biophysics-dihedral"
    "find-topk-similiar-chemicals"
    "reaction-type"
    "isomer-counting"
    "inorganic-physics-thermo"
    "organic-chemistry-smarts"
    "jax-computing-basics"
    ######## Earth, Climate & Geophysics
    "earthquake-phase-association"
    "earthquake-plate-calculation"
    "seismic-phase-picking"
    "gravitational-wave-detection"
    "fluidsim-pipe-flow"
    "fluidsim-nusselt-number"
    "shock-analysis-demand"
    "shock-analysis-supply"
    "flood-risk-analysis"
    "exoplanet-detection-period"
    "mars-clouds-clustering"
    "lake-warming-attribution"
    "glm-lake-mendota"
    ######## Engineering, Energy & Control
    "energy-ac-optimal-power-flow"
    "grid-dispatch-operator"
    "reserves-at-risk-calc"
    "adaptive-cruise-control"
    "hvac-control"
    "r2r-mpc-control"
    "pymoo-optimization"
    "pymoo-constrained-opt"
    "manufacturing-fjsp-optimization"
    "quantum-bloch-vector"
    "quantum-numerical-simulation"
    "qutip-quantum-state"
    ######### Finance, Economics & Business
    "financial-modeling-qa"
    "sec-financial-report"
    "sales-pivot-analysis"
    "weighted-gdp-calc"
    "invoice-fraud-detection"
    "econ-detrending-correlation"
    "energy-market-pricing"
    "powerlifting-coef-calc"
    "pddl-tpp-planning"
    ########## Document, Media & Web Intelligence
    "court-form-filling"
    "jpg-ocr-stat"
    "latex-formula-extraction"
    "parallel-tfidf-search"
    "taxonomy-tree-merge"
    "lab-unit-harmonization"
    "3d-scan-calc"
    "threejs-structure-parser"
    "threejs-to-obj"
    "dynamic-object-aware-egomotion"
    "multilingual-video-dubbing"
    ########### Software Engineering & Security
    "fix-druid-loophole-cve"
    "fix-erlang-ssh-cve"
    "dapt-intrusion-detection"
    "azure-bgp-oscillation-route-leak"
    "suricata-custom-exfil"
    "syzkaller-ppdev-syzlang"
    "software-dependency-audit"
    "simpo-code-reproduction"
    "lean4-proof"
)

USER_TRUNCATE_TOKENS=300
MAX_ASSISTANT_PER_BATCH=1
MODEL="gpt-5.5"
TEMPERATURE=0.2
MAX_TOKENS=120000
TIMEOUT=120

TASK_ARGS=()
if [ "${#TASK_LIST[@]}" -gt 0 ]; then
    TASK_ARGS=(--task-list "${TASK_LIST[@]}")
fi


"${PYTHON_BIN}" scripts/rewrite_trajectory.py \
    --traj-root "${TRAJ_ROOT}" \
    --output-root "${OUTPUT_ROOT}" \
    --key-info-root "${KEY_INFO_ROOT}" \
    "${TASK_ARGS[@]}" \
    --user-truncate-tokens "${USER_TRUNCATE_TOKENS}" \
    --max-assistant-per-batch "${MAX_ASSISTANT_PER_BATCH}" \
    --model "${MODEL}" \
    --temperature "${TEMPERATURE}" \
    --max-tokens "${MAX_TOKENS}" \
    --timeout "${TIMEOUT}" \
    "$@"
