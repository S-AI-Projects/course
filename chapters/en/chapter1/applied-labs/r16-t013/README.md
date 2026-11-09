# Applied Lab R16-T013: Security Scenario Rubric and Dual-Approach Comparison

## Related Lesson
- **Chapter**: Chapter 1 - Transformer models
- **Section**: [Ungraded quiz (7.mdx)](../../7.mdx)

## Objective & Focus
This lab provides a structural rubric checker for cybersecurity risk scenarios tied to machine learning pipelines, model hubs, and dataset risks. It compares two independent evaluation approaches on identical inputs:
1. **Direct Rubric Implementation**: Rule-based completeness and control relevance analysis.
2. **Independent Reference Table**: Benchmark lookup table of explicit ground-truth verdicts.

## Scenario Specifications and Rubric Results

Each scenario is encoded with four required fields: `asset`, `threat`, `control`, and `residual_risk`.

| Scenario ID | Name & Lesson Connection | Asset | Threat | Control | Residual Risk | Completeness | Control Review | Overall Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `model_hub_integrity` | Model Hub Checkpoint Integrity (Question 1) | Pretrained RoBERTa weights on Hugging Face Hub | Unauthorized weight tampering or supply-chain poisoning | Cryptographic hash verification and commit signature enforcement | Compromised maintainer credentials could sign poisoned weights | **PASS** | **MATCH** | `("PASS", "MATCH")` |
| `dataset_demographic_bias` | Pretraining Dataset Bias (Question 11) | *(Omitted / Missing)* | Demographic bias in training data skewing predictions | Demographic auditing and representation filtering | Latent proxy variables in web text may retain subtle bias | **FAIL** | **MATCH** | `("FAIL", "MATCH")` |
| `inference_pipeline_ddos` | Pipeline Inference Service (Questions 2 & 4) | Production NER inference API endpoint | DDoS request flooding saturating transformer inference queue | Enforcing code comment formatting and docstring style | Inference queue remains vulnerable to volumetric saturation | **PASS** | **REVIEW** | `("PASS", "REVIEW")` |

## Human Review vs. Automated Checker Limits
- **Automated Checker**: Strictly validates the structural rubric (presence of all 4 fields and keyword heuristics indicating whether a control relates to the threat).
- **Human Review**: Evaluates the qualitative soundness of the control, contextual appropriateness of the residual risk, and domain-specific justification.

## Approach Comparison
Both evaluation methods process identical scenario inputs:
- Direct implementation computes `(completeness_status, control_verdict)` on the fly.
- Reference implementation retrieves pre-established ground truth from `REFERENCE_RESULTS`.
- `compare_both_approaches()` asserts agreement across all test fixtures.

## Running the Lab

### 1. Run the Standalone Comparison
```bash
python3 chapters/en/chapter1/applied-labs/r16-t013/example.py
```

### 2. Run Automated Unit Tests
```bash
python3 -m unittest discover -s chapters/en/chapter1/applied-labs/r16-t013 -p "test_*.py" -v
```

### 3. Run Verification & Comparison Checks
```bash
python3 work/R16-T013/check.py
```

## Scope and Limitations
- **Educational Simulation**: Structural rubric verification and keyword matching implemented in pure Python without requiring live security monitoring tools.
- **Zero External Dependencies**: Operates entirely with the Python 3 standard library.
- **Hardware & Cloud Agnostic**: Makes no claims regarding real-world cloud firewall performance or production server hardening.
