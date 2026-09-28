# Lab 02 Audit

Security assessment of the frozen `lab02-agent-isolated-target` baseline.

This laboratory is an experimental security audit of an LLM-based agent operating in an isolated target environment. The audit is performed on an independent copy of the completed Lab 02 baseline and does not modify the original laboratory.

## Objective

The objective of this laboratory is to systematically assess the security properties of the Lab 02 agent, with particular attention to:

* agent capabilities and autonomy
* tool access and tool invocation
* trust boundaries
* data flows
* untrusted input handling
* authorization and privilege boundaries
* interaction with the target environment
* observable security impact
* logging and evidence collection
* security controls and their effectiveness

The audit is intentionally incremental. It does not attempt to provide exhaustive coverage of every AI security risk.

The goal is to demonstrate a small number of realistic security assessment techniques end-to-end:

```text
Architecture
    ↓
Threat hypothesis
    ↓
Experiment design
    ↓
Baseline execution
    ↓
Evidence collection
    ↓
Security finding
    ↓
Framework mapping
    ↓
Control
    ↓
Re-test
```

## Baseline

The audit starts from the frozen Lab 02 implementation:

```text
lab02-agent-isolated-target
```

The baseline was copied without modification into:

```text
lab02-audit
```

The original Lab 02 remains unchanged and is considered frozen.

Baseline Git commit:

```text
97f48ae Lab02 clompleted. Closed
```

Audit initialization commit:

```text
5e01a2a Initialize lab02 audit from frozen baseline
```

The initial state of `lab02-audit` was verified against the Lab 02 baseline before starting the audit.

## Scope

The audit covers the security properties of the agent and its interaction with the intentionally isolated laboratory environment.

The initial scope includes:

1. Architecture and component inventory
2. Assets and trust boundaries
3. Agent capabilities
4. Tool inventory and permissions
5. Input and data-flow analysis
6. Attack surface identification
7. Security threat hypotheses
8. Controlled adversarial experiments
9. Evidence collection
10. Security controls
11. Re-testing

The audit is not intended to:

* modify the original Lab 02 baseline
* assess arbitrary external infrastructure
* provide exhaustive OWASP or MITRE coverage
* assume that a suspected vulnerability exists before testing
* treat framework mappings as proof of a vulnerability

## Security Assessment Methodology

Each security hypothesis will be documented and tested using a consistent structure:

```text
Experiment ID
    ↓
Security hypothesis
    ↓
Preconditions
    ↓
Attack / test input
    ↓
Expected secure behavior
    ↓
Observed behavior
    ↓
Evidence
    ↓
Security impact
    ↓
Framework mapping
    ↓
Mitigation
    ↓
Re-test
```

A framework mapping is added only after the observed behavior has been established.

## Security Frameworks

### OWASP GenAI Security Project

OWASP is used as the primary application-level security reference for the audit.

The audit will use the current OWASP GenAI guidance relevant to the laboratory, including:

* OWASP GenAI LLM Top 10 2026
* OWASP Top 10 for Agentic Applications 2026
* OWASP Agentic AI Threats and Mitigations
* OWASP guidance for securing agentic applications

Relevant risks will be mapped only when they are applicable to the observed architecture and experiment.

Initial areas of interest include:

* Prompt Injection / Agent Goal Hijacking
* Tool Misuse
* Identity and Privilege Abuse
* Excessive Agency
* Unexpected Code Execution
* Sensitive Information Disclosure
* Improper Output Handling
* Supply-chain or component trust where applicable

### MITRE ATLAS

MITRE ATLAS is used to describe adversarial behavior specifically involving AI-enabled systems.

ATLAS mappings will be considered when an experiment demonstrates an adversarial behavior against the agent, its AI capabilities, or its AI-specific control boundaries.

The mapping will identify the relevant tactic and technique when the evidence supports it.

### MITRE ATT&CK

MITRE ATT&CK is used only when an observed behavior corresponds to a conventional enterprise, operating-system, network, credential, execution, discovery, collection, or exfiltration technique.

ATT&CK is complementary to ATLAS rather than a replacement for it.

For example:

```text
AI-specific manipulation
        ↓
     ATLAS

Traditional host/network behavior
        ↓
     ATT&CK
```

A single experiment may therefore map to ATLAS, ATT&CK, both, or neither.

## Initial Audit Coverage

The audit intentionally starts with a limited set of representative security questions.

| Area                      | Security question                                                         | Planned assessment |
| ------------------------- | ------------------------------------------------------------------------- | ------------------ |
| Agent Goal Hijacking      | Can untrusted input alter the agent's intended objective?                 | Planned            |
| Tool Misuse               | Can the agent invoke or parameterize tools outside their intended use?    | Planned            |
| Agency / Privilege        | Are the agent's capabilities broader than required?                       | Planned            |
| Output Handling           | Can agent-generated output cross a trust boundary unsafely?               | Planned            |
| Information Exposure      | Can the agent access or disclose information outside its intended scope?  | Planned            |
| Traditional System Impact | Does agent behavior result in conventional host/network security actions? | Planned            |

This table is a starting point, not a commitment to test every item.

The final coverage will be determined after architecture and attack-surface analysis.

## Audit Artifacts

Evidence and analysis will be kept separate from the application implementation where practical.

The audit will progressively document:

```text
Architecture
Threat model
Attack surface
Experiment specifications
Experiment results
Evidence
Findings
Framework mappings
Controls
Re-test results
```

Experiments should produce reproducible evidence whenever possible, including:

* agent inputs
* agent outputs
* tool calls
* tool parameters
* application logs
* network observations
* filesystem changes
* target-state changes
* relevant command output
* timestamps
* Git commit references

## Evidence and Reproducibility

Security findings must be supported by observable evidence.

The audit distinguishes between:

```text
Hypothesis
    ≠
Finding
```

A hypothesis becomes a finding only when the experiment produces sufficient evidence to demonstrate the relevant behavior.

Negative results are also valuable and will be recorded when they meaningfully establish that a tested attack path was not reproduced under the documented conditions.

## Controls and Re-testing

Security controls will be introduced only after the relevant baseline behavior has been documented.

The intended lifecycle is:

```text
Baseline
   ↓
Experiment
   ↓
Evidence
   ↓
Finding
   ↓
Control
   ↓
Re-test
   ↓
Residual risk
```

Controls will not be added before the corresponding baseline behavior is understood, since doing so could invalidate the experimental comparison.

## Git Workflow

Git history is part of the audit methodology.

Changes should be kept incremental and logically separated.

Examples:

```text
Initialize lab02 audit from frozen baseline
Document audit scope and methodology
Document architecture and trust boundaries
Add experiment specification
Record experiment results
Add security control
Re-test experiment
Document final findings
```

The frozen Lab 02 baseline must never be modified as part of this audit.

## Planned Audit Structure

The exact directory structure may evolve as the audit progresses, but the project is expected to contain artifacts similar to:

```text
lab02-audit/
├── README.md
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
├── src/
├── target/
└── audit/
    ├── architecture/
    ├── threat-model/
    ├── experiments/
    ├── evidence/
    ├── findings/
    └── controls/
```

Directories will be introduced when they become useful rather than creating empty structure in advance.

## Status

Current status:

```text
[x] Lab 02 baseline frozen
[x] Audit environment copied from baseline
[x] Audit initialized as an independent Git state
[ ] Architecture analysis
[ ] Asset inventory
[ ] Trust boundary analysis
[ ] Data-flow analysis
[ ] Agent capability analysis
[ ] Attack surface analysis
[ ] Threat hypotheses
[ ] Security experiments
[ ] Framework mappings
[ ] Security controls
[ ] Re-testing
[ ] Final audit report
```

## References

* OWASP GenAI Security Project
* OWASP GenAI LLM Top 10 2026
* OWASP Top 10 for Agentic Applications 2026
* OWASP Agentic AI Threats and Mitigations
* OWASP Securing Agentic Applications Guide
* MITRE ATLAS
* MITRE ATT&CK
