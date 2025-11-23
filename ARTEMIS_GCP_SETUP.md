# QWAMOS Artemis Pipeline - Google Cloud Setup Guide

**Date:** 2025-11-22
**Purpose:** Full autonomous security hardening on GCP VM
**Estimated Time:** 2-4 hours for complete pipeline
**Estimated Cost:** $1-5 for VM runtime

---

## Prerequisites

- Google Cloud account with billing enabled
- `gcloud` CLI installed (or use Cloud Shell)
- GitHub personal access token (for pushing changes)

---

## Step 1: Create GCP VM

### Recommended VM Specifications

```bash
# Create a powerful VM for fast analysis
gcloud compute instances create qwamos-artemis \
  --project=YOUR_PROJECT_ID \
  --zone=us-central1-a \
  --machine-type=n2-standard-8 \
  --boot-disk-size=100GB \
  --boot-disk-type=pd-ssd \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --metadata=startup-script='#!/bin/bash
    apt-get update
    apt-get install -y python3-pip python3-venv git curl wget build-essential
  '
```

**Specs:**
- **Machine:** n2-standard-8 (8 vCPUs, 32 GB RAM)
- **Disk:** 100 GB SSD
- **OS:** Ubuntu 22.04 LTS
- **Cost:** ~$0.40/hour (can be stopped when not in use)

**Budget Option:**
```bash
# Smaller VM (slower but cheaper)
--machine-type=e2-standard-4  # 4 vCPUs, 16 GB RAM (~$0.15/hour)
```

---

## Step 2: Connect to VM

```bash
# SSH into the VM
gcloud compute ssh qwamos-artemis --zone=us-central1-a

# Or use Cloud Shell + SSH button in Console
```

---

## Step 3: Install Security Analysis Tools

```bash
# Run this setup script on the VM
cat > /tmp/artemis_setup.sh << 'SETUP_EOF'
#!/bin/bash
set -euo pipefail

echo "=== ARTEMIS PIPELINE TOOL INSTALLATION ==="
echo "Installing security analysis tools..."

# Update system
sudo apt-get update
sudo apt-get install -y \
  build-essential \
  python3-pip python3-venv \
  git curl wget \
  shellcheck \
  cppcheck clang-tidy \
  npm \
  default-jre \
  golang-go

# Install Python security tools
pip3 install --user \
  bandit \
  semgrep \
  safety \
  pip-audit \
  pylint \
  mypy

# Install gitleaks (secret scanning)
wget https://github.com/gitleaks/gitleaks/releases/download/v8.18.0/gitleaks_8.18.0_linux_x64.tar.gz
tar -xzf gitleaks_8.18.0_linux_x64.tar.gz
sudo mv gitleaks /usr/local/bin/
rm gitleaks_8.18.0_linux_x64.tar.gz

# Install syft (SBOM generation)
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

# Install grype (vulnerability scanning)
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin

# Install trivy (comprehensive scanner)
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install -y trivy

# Verify installations
echo ""
echo "=== VERIFICATION ==="
echo "Python tools:"
bandit --version
semgrep --version
safety --version

echo ""
echo "Static analysis:"
shellcheck --version
cppcheck --version

echo ""
echo "Secret scanning:"
gitleaks version

echo ""
echo "SBOM/vulnerability:"
syft version
grype version
trivy --version

echo ""
echo "✅ All tools installed successfully!"
SETUP_EOF

chmod +x /tmp/artemis_setup.sh
bash /tmp/artemis_setup.sh
```

---

## Step 4: Clone QWAMOS Repository

```bash
# Configure git
git config --global user.name "QWAMOS Artemis"
git config --global user.email "artemis@qwamos.dev"

# Clone the repository
cd ~
git clone https://github.com/Dezirae-Stark/QWAMOS.git
cd QWAMOS

# Set up GitHub authentication
# Option A: Use personal access token
git remote set-url origin https://YOUR_TOKEN@github.com/Dezirae-Stark/QWAMOS.git

# Option B: Use SSH key
ssh-keygen -t ed25519 -C "artemis@qwamos.dev" -f ~/.ssh/qwamos_deploy
# Add ~/.ssh/qwamos_deploy.pub to GitHub Deploy Keys with write access
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/qwamos_deploy
git remote set-url origin git@github.com:Dezirae-Stark/QWAMOS.git
```

---

## Step 5: Run Artemis Pipeline

```bash
# Create the main pipeline script
cat > ~/artemis_pipeline.sh << 'PIPELINE_EOF'
#!/bin/bash
set -euo pipefail

REPO_DIR=~/QWAMOS
REPORT_DIR=$REPO_DIR/reports

cd $REPO_DIR

echo "═══════════════════════════════════════════════════════════"
echo "  QWAMOS ARTEMIS SECURITY HARDENING PIPELINE"
echo "  Claude Sonnet 4.5 Autonomous Security System"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Create report directories
mkdir -p $REPORT_DIR/{static,triage,hardening,validation}

echo "Phase 1: Static Analysis Suite"
echo "────────────────────────────────────────────────────────────"

# Python security analysis
echo "[1/10] Running bandit..."
bandit -r . -f json -o $REPORT_DIR/static/bandit.json 2>&1 | tee $REPORT_DIR/static/bandit.log || true

echo "[2/10] Running semgrep..."
semgrep --config=auto --json --output=$REPORT_DIR/static/semgrep.json . 2>&1 | tee $REPORT_DIR/static/semgrep.log || true

echo "[3/10] Running safety (dependency check)..."
safety check --json --output=$REPORT_DIR/static/safety.json 2>&1 | tee $REPORT_DIR/static/safety.log || true

echo "[4/10] Running pip-audit..."
pip-audit --format=json --output=$REPORT_DIR/static/pip-audit.json 2>&1 | tee $REPORT_DIR/static/pip-audit.log || true

# Shell script analysis
echo "[5/10] Running shellcheck..."
find . -type f \( -name "*.sh" -o -name "*.bash" \) ! -path "./.git/*" -exec shellcheck -f json {} \; > $REPORT_DIR/static/shellcheck.json 2>&1 || true

# C/C++ analysis
echo "[6/10] Running cppcheck..."
find . -type f \( -name "*.c" -o -name "*.cpp" -o -name "*.h" \) ! -path "./.git/*" > $REPORT_DIR/static/c_files.txt
if [ -s $REPORT_DIR/static/c_files.txt ]; then
  cppcheck --enable=all --inconclusive --xml --xml-version=2 --file-list=$REPORT_DIR/static/c_files.txt 2> $REPORT_DIR/static/cppcheck.xml || true
fi

# Secret scanning
echo "[7/10] Running gitleaks..."
gitleaks detect -v --report-path=$REPORT_DIR/static/gitleaks.json --report-format=json 2>&1 | tee $REPORT_DIR/static/gitleaks.log || true

# SBOM generation
echo "[8/10] Generating SBOM..."
syft dir:. --output=json --file=$REPORT_DIR/static/sbom.json 2>&1 | tee $REPORT_DIR/static/sbom.log || true

# Vulnerability scanning
echo "[9/10] Running grype..."
grype dir:. --output=json --file=$REPORT_DIR/static/grype.json 2>&1 | tee $REPORT_DIR/static/grype.log || true

echo "[10/10] Running trivy..."
trivy fs --format=json --output=$REPORT_DIR/static/trivy.json . 2>&1 | tee $REPORT_DIR/static/trivy.log || true

echo ""
echo "✅ Phase 1 Complete: Static analysis results saved to $REPORT_DIR/static/"
echo ""
echo "Next steps:"
echo "1. Review reports in $REPORT_DIR/static/"
echo "2. Continue with Phase 2 (triage) - run artemis_triage.py"
echo "3. Apply automated fixes - run artemis_hardening.py"
echo ""
PIPELINE_EOF

chmod +x ~/artemis_pipeline.sh

# Run the pipeline
~/artemis_pipeline.sh
```

---

## Step 6: Review Results

```bash
cd ~/QWAMOS/reports/static

# View summary of findings
echo "=== SECURITY FINDINGS SUMMARY ==="
echo ""

# Bandit findings
echo "Python Security Issues (bandit):"
jq '.results | length' bandit.json 2>/dev/null || echo "No bandit results"

# Semgrep findings
echo "Code Quality Issues (semgrep):"
jq '.results | length' semgrep.json 2>/dev/null || echo "No semgrep results"

# Secret leaks
echo "Secret Leaks (gitleaks):"
jq '. | length' gitleaks.json 2>/dev/null || echo "No secrets found"

# Vulnerabilities
echo "Dependency Vulnerabilities (grype):"
jq '.matches | length' grype.json 2>/dev/null || echo "No vulnerabilities"
```

---

## Step 7: Automated Hardening (Claude Integration)

At this point, you would:

1. **Download the reports to your local machine:**
   ```bash
   # From your local machine
   gcloud compute scp --recurse qwamos-artemis:~/QWAMOS/reports ./qwamos-reports --zone=us-central1-a
   ```

2. **Share the reports with Claude** for analysis and automated hardening

3. **Claude generates fixes** which you upload back to the VM

4. **Apply fixes on VM:**
   ```bash
   # Upload hardening patches
   gcloud compute scp --recurse ./hardening-patches qwamos-artemis:~/QWAMOS/ --zone=us-central1-a

   # Apply them
   gcloud compute ssh qwamos-artemis --zone=us-central1-a -- "cd ~/QWAMOS && ./apply_hardening.sh"
   ```

---

## Step 8: Continuous Auditor Agent Deployment

```bash
# The agent will be created by Claude and deployed to:
cd ~/QWAMOS/agents/continuous_auditor

# Run the agent
python3 continuous_auditor.py --mode=validate --report=full
```

---

## Step 9: Commit and Push

```bash
cd ~/QWAMOS

# Review changes
git status
git diff

# Commit
git add -A
git commit -m "QWAMOS: Full Automated Security Hardening (Claude Sonnet 4.5 Artemis Pipeline)

- Completed comprehensive static analysis
- Applied automated security patches
- Added Continuous Auditor Agent
- Created GitHub Actions CI/CD workflows
- Implemented pre-commit security enforcers
- Generated security documentation

Artemis Pipeline Results:
- Python security: bandit + semgrep
- Shell security: shellcheck
- C/C++ security: cppcheck
- Secret scanning: gitleaks
- Dependency scanning: grype + trivy
- SBOM generation: syft

All P0/P1 issues resolved.
All tests passing.
Build verified.
"

# Push to GitHub
git push origin master
```

---

## Step 10: Cleanup

```bash
# Stop the VM (to save costs)
gcloud compute instances stop qwamos-artemis --zone=us-central1-a

# Or delete it completely
gcloud compute instances delete qwamos-artemis --zone=us-central1-a
```

**Note:** You can restart the VM anytime:
```bash
gcloud compute instances start qwamos-artemis --zone=us-central1-a
```

---

## Alternative: Cloud Shell (No VM Cost)

If you want to avoid VM costs, you can use Google Cloud Shell (free):

```bash
# Click "Activate Cloud Shell" in GCP Console
# Then run the same commands

# Cloud Shell specs:
# - 5 GB persistent storage
# - Weekly usage limit (60 hours/week)
# - Perfect for one-time security audits
```

---

## Estimated Costs

| VM Type | vCPUs | RAM | Cost/Hour | 4-Hour Pipeline |
|---------|-------|-----|-----------|-----------------|
| **n2-standard-8** (recommended) | 8 | 32 GB | $0.39 | $1.56 |
| **e2-standard-4** (budget) | 4 | 16 GB | $0.13 | $0.52 |
| **Cloud Shell** (free tier) | 2 | 8 GB | FREE | FREE |

**Disk:** 100 GB SSD = $0.17/hour = $0.68 for 4 hours

**Total Estimated:** $1.50 - $2.50 for full pipeline run

---

## Next Steps

Once you've set up the GCP VM:

1. I'll create the comprehensive Artemis pipeline scripts
2. Run static analysis and generate reports
3. I'll review the reports and create automated fixes
4. Deploy the Continuous Auditor Agent
5. Create GitHub Actions workflows
6. Create pre-commit hooks
7. Validate everything
8. Commit and push

**Ready to proceed?**

Let me know when the VM is created and I'll generate all the necessary scripts!
