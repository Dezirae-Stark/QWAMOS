# ARTEMIS Pipeline - Quick Start Guide

**⚡ Get Started in 10 Minutes**

---

## Option 1: Google Cloud VM (Recommended)

### Step 1: Create VM (2 minutes)

```bash
gcloud compute instances create qwamos-artemis \
  --machine-type=n2-standard-8 \
  --boot-disk-size=100GB \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --zone=us-central1-a
```

### Step 2: SSH and Setup (3 minutes)

```bash
# Connect
gcloud compute ssh qwamos-artemis --zone=us-central1-a

# Quick setup
curl -sSL https://raw.githubusercontent.com/Dezirae-Stark/QWAMOS/master/scripts/artemis_quick_setup.sh | bash

# Clone repo
git clone https://github.com/Dezirae-Stark/QWAMOS.git
cd QWAMOS
```

### Step 3: Run Pipeline (5 minutes)

```bash
# Execute full analysis
python3 artemis_full_pipeline.py

# View results
cat reports/artemis_summary.json
```

---

## Option 2: Cloud Shell (Free, No Setup)

```bash
# In GCP Console, click "Activate Cloud Shell"

# Clone and run
git clone https://github.com/Dezirae-Stark/QWAMOS.git
cd QWAMOS
./scripts/artemis_quick_setup.sh
python3 artemis_full_pipeline.py
```

---

## What Happens Next?

The pipeline will:

1. ✅ **Analyze 94 Python files** with bandit + semgrep
2. ✅ **Scan 57 shell scripts** with shellcheck
3. ✅ **Check for secrets** with gitleaks
4. ✅ **Scan dependencies** for vulnerabilities
5. ✅ **Generate SBOM** with syft
6. ✅ **Triage findings** into P0/P1/P2/P3
7. ✅ **Create reports** in `reports/` directory

**Output:**
- `reports/artemis_summary.json` - Complete results
- `reports/triage/p0-critical.md` - Critical issues
- `reports/triage/p1-high.md` - High priority issues
- `reports/static/*.json` - Raw tool outputs

---

## Interpreting Results

```bash
# View summary
jq . reports/artemis_summary.json

# Count critical issues
jq '.findings.p0_critical' reports/artemis_summary.json

# List all P0 issues
cat reports/triage/p0-critical.md
```

---

## Next Steps

Based on findings:

**If P0 > 0:**
→ Immediate action required
→ Review `reports/triage/p0-critical.md`
→ Apply automated fixes

**If P1 > 5:**
→ Schedule hardening sprint
→ Use automated patch generator

**If P2/P3 only:**
→ QWAMOS is in excellent shape!
→ Deploy Continuous Auditor for monitoring

---

## Cost Estimate

**GCP VM (n2-standard-8):**
- Setup: 3 minutes
- Analysis: 5-10 minutes
- Total runtime: ~15 minutes
- Cost: **~$0.10**

**Cloud Shell:**
- FREE (included in GCP free tier)
- Slower but no cost

---

## Support

Questions? Check:
- Full guide: `ARTEMIS_GCP_SETUP.md`
- Pipeline code: `artemis_full_pipeline.py`
- GitHub Issues: https://github.com/Dezirae-Stark/QWAMOS/issues
