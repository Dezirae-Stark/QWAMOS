# AI Governor Architecture

## Decision-Making Pipeline

```
[System Metrics Collection]
    ↓
[ML Workload Classifier] → Predict: Idle, Browsing, Crypto, Gaming
    ↓
[Threat Intelligence Feed] ← Phase 7 ML Threat Detection
    ↓
[RL Policy Network] → Output: Resource allocation decisions
    ↓
[Resource Controller] → Execute: vCPU, Memory, I/O, Power adjustments
```

## Reinforcement Learning Approach

**State Space**:
- VM CPU usage (8 dimensions: 1 per core)
- VM memory usage (per VM)
- Battery level and charge rate
- CPU temperature
- Active threat level (from Phase 7)
- Time of day and user activity

**Action Space**:
- vCPU affinity adjustments (assign VMs to big/little cores)
- Memory balloon inflation/deflation
- I/O priority changes
- DVFS (frequency scaling)
- Display brightness adjustment

**Reward Function**:
```
R = α * (battery_life) - β * (user_latency) + γ * (security_score) - δ * (temperature_penalty)
```

Where:
- α = battery weight (optimize for long runtime)
- β = latency weight (minimize UI lag)
- γ = security weight (boost during threats)
- δ = thermal weight (prevent overheating)

## Model Architecture

**TensorFlow Lite Model**:
- Input: 32-dimensional state vector
- Hidden layers: 2 layers (128 units, 64 units) with ReLU
- Output: 16-dimensional action probabilities
- Model size: <5 MB (quantized INT8)
- Inference time: <10ms on Snapdragon AI Engine

---

**Last Updated:** 2025-11-17
