# Lab 03 — Stateful Agent

## Objective

Lab 03 extends the isolated, network-capable agent from Lab 02 into a stateful agent that can perform actions with persistent security-relevant side effects.

The main objective is to introduce a new security dimension:

> The agent is no longer limited to observing reachable resources. It can now read and modify application state through tools.

The laboratory therefore introduces:

* agent identity and execution context;
* resource ownership and classification;
* authorization decisions;
* read-only and state-changing tools;
* persistent application state;
* observable side effects.

The laboratory is intentionally implemented without an agent framework so that the authority exercised by the LLM, the tools, and the target application remains explicit and inspectable.

---

## Security Context

Lab 02 established that an agent may have:

* network-capable tools;
* model-controlled tool parameters;
* network reachability to resources;
* application-level access to resources outside an intended target.

Lab 03 builds on that foundation.

The central question changes from:

> Can the agent reach a resource?

to:

> What can the agent do once it can act on a resource?

and:

> Can the agent perform actions outside the authority it is supposed to have?

The progression is therefore:

```text
Lab 01
Basic agent
    │
    ▼
Lab 02
Network-capable agent
    │
    ├── capability
    ├── parameter control
    ├── network boundary
    └── reachable resources
    │
    ▼
Lab 03
Stateful agent
    │
    ├── identity
    ├── authorization
    ├── state
    └── side effects
```

---

## Architecture

```text
                         ┌──────────────┐
                         │    Ollama    │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │    Agent     │
                         │              │
                         │ user=analyst │
                         └──────┬───────┘
                                │
                         Agent tools
                                │
                                ▼
                     ┌────────────────────┐
                     │ Target Web         │
                     │ Application        │
                     │                    │
                     │ ┌────────────────┐ │
                     │ │ Authorization  │ │
                     │ └───────┬────────┘ │
                     │         │          │
                     │ ┌───────▼────────┐ │
                     │ │ Stateful       │ │
                     │ │ records        │ │
                     │ └────────────────┘ │
                     └────────────────────┘
```

The network topology remains based on Lab 02:

```text
ai-llm-network
      │
    Agent
      │
      │ target-network
      │
    Target
```

The target remains isolated on the internal `target-network`.

---

## Agent Identity

The agent executes with the following configured identity:

```text
AGENT_USER=analyst
```

The identity is provided by the agent container environment.

It is not a parameter exposed to the LLM through the record tools.

The record tools automatically include the configured identity in requests to the target using:

```http
X-Agent-User: analyst
```

This header represents the agent execution context in the laboratory.

It is **not intended to represent a strong authentication mechanism**. The laboratory uses it to make identity and authorization semantics explicit and observable.

Authorization is enforced by the target application, not by the LLM.

---

## Resource Model

The target application contains three resource classes.

| Resource class | Example      | Owner      | Analyst read | Analyst modify |
| -------------- | ------------ | ---------- | -----------: | -------------: |
| Public         | `record-001` | None       |          Yes |             No |
| Analyst-owned  | `record-101` | `analyst`  |          Yes |            Yes |
| Restricted     | `record-201` | `security` |           No |             No |

Initial records include:

### Public records

```text
record-001
record-002
```

These records are publicly readable.

### Analyst-owned records

```text
record-101
record-102
```

These records belong to the `analyst` identity.

The analyst can read and modify them.

### Restricted records

```text
record-201
record-202
```

These records belong to the `security` context.

The `analyst` identity cannot read or modify them.

---

## Authorization Model

The target application performs authorization checks based on the resource classification and the requesting identity.

Conceptually:

```text
                    analyst
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
     public         analyst        restricted
        │             │              │
      READ       READ / MODIFY       DENY
```

The authorization logic is deliberately located in the target application.

The agent tools do not independently decide whether a resource is authorized.

This separation is important for later security experiments because it allows the laboratory to distinguish:

```text
LLM decision
     │
     ▼
Tool capability
     │
     ▼
Agent identity
     │
     ▼
Target authorization
     │
     ▼
State-changing action
```

---

## Stateful Target

The target is a small HTTP application implemented with Python's standard library.

It exposes a record-oriented API:

```text
GET     /records
GET     /records/<id>
POST    /records
PUT     /records/<id>
DELETE  /records/<id>
```

The application maintains its state in:

```text
/tmp/records.json
```

The state is loaded when the target starts and written after state-changing operations.

This provides observable state changes without introducing an external database service.

---

## Implemented Record Tools

The first stateful agent tools are implemented in:

```text
src/lab03_agent_stateful/tools/records.py
```

### `get_record`

Reads an individual record.

```text
get_record(record_id)
```

The `record_id` is controlled by the tool caller, while the agent identity is taken from the environment.

### `list_records`

Lists records visible to the current agent identity.

```text
list_records()
```

### `create_record`

Creates a new analyst-owned record.

```text
create_record(title, content)
```

The target assigns ownership using the requesting identity.

The model does not directly choose the owner.

### `update_record`

Modifies an existing analyst-owned record.

```text
update_record(record_id, title?, content?)
```

The target performs the authorization check before applying the modification.

---

## Tool Authorization Boundary

The current implementation deliberately separates tool parameters from execution identity.

For example:

```text
LLM
 │
 │ record_id = record-101
 ▼
get_record()
 │
 │ X-Agent-User: analyst
 ▼
Target
 │
 ├── resource lookup
 ├── authorization
 └── response
```

The LLM can select the resource identifier.

It cannot select a different identity through the tool arguments.

This is an intentional design decision and will be relevant to future audit experiments.

---

## State-Changing Operations

The target supports state-changing operations.

For example:

```text
analyst
   │
   │ PUT /records/record-101
   ▼
Target
   │
   ├── authorization → allowed
   │
   └── state updated
```

The resulting state can subsequently be observed through another request.

The baseline has been manually verified to demonstrate:

```text
record-101
    │
    ├── GET → 200
    ├── PUT → 200
    └── subsequent GET → modified content
```

A request from `analyst` to the restricted record has also been verified:

```text
GET /records/record-201
X-Agent-User: analyst

→ HTTP 403 Forbidden
```

These observations establish the expected target-side authorization behavior before exposing the functionality to the LLM.

---

## Existing Network Tools

Lab 03 retains the network tools inherited from Lab 02:

```text
resolve_host
check_tcp_port
http_get
```

They remain available in:

```text
src/lab03_agent_stateful/tools/network.py
```

They represent the network reconnaissance capability established in Lab 02.

The new stateful record tools add a different class of authority:

```text
Network tools
├── resolve_host
├── check_tcp_port
└── http_get

Stateful tools
├── get_record
├── list_records
├── create_record
└── update_record
```

The security focus of Lab 03 is the second group.

---

## Current Implementation Status

The following components are currently implemented and independently validated:

| Component                       | Status                           |
| ------------------------------- | -------------------------------- |
| Lab 03 project structure        | Implemented                      |
| Lab 02 network topology         | Retained                         |
| Stateful target                 | Implemented                      |
| Public records                  | Implemented                      |
| Analyst-owned records           | Implemented                      |
| Restricted records              | Implemented                      |
| Target-side authorization       | Implemented                      |
| JSON-backed state               | Implemented                      |
| `get_record`                    | Implemented                      |
| `list_records`                  | Implemented                      |
| `create_record`                 | Implemented                      |
| `update_record`                 | Implemented                      |
| `delete_record`                 | Not yet exposed as an agent tool |
| LLM integration of record tools | Not yet implemented              |
| Agent baseline validation       | Pending                          |
| Security audit                  | Not part of Lab 03               |

The implementation is therefore intentionally incomplete at this checkpoint.

---

## Baseline Validation

The target-side baseline has been independently tested before exposing the functionality to the LLM.

Observed behavior includes:

```text
GET public record
    → 200

GET analyst-owned record as analyst
    → 200

GET restricted record as analyst
    → 403

UPDATE analyst-owned record as analyst
    → 200

GET modified record
    → modified state observed
```

These tests establish the expected application behavior independently from model behavior.

---

## Security Boundaries

Lab 03 introduces several distinct boundaries:

### Network boundary

Inherited from Lab 02.

```text
Agent
  │
  ▼
target-network
  │
  ▼
Target
```

### Identity boundary

The agent operates using:

```text
analyst
```

### Resource boundary

Resources have different ownership and classification:

```text
public
analyst-owned
restricted
```

### Authorization boundary

The target decides whether the current identity can perform the requested operation.

### State boundary

Some tools can change persistent application state.

These boundaries should remain conceptually separate.

---

## Security Questions

The laboratory is designed to support future experiments around questions such as:

1. Does the agent respect resource authorization boundaries?
2. Can the LLM cause a tool to operate on resources outside its intended scope?
3. Can tool chaining produce security-relevant state changes?
4. Does the agent distinguish between information it can read and actions it is authorized to perform?
5. Can user-controlled input influence state-changing actions in unsafe ways?
6. Does the separation between user authority, agent authority, and backend authority remain intact?
7. Can the agent cause state changes without sufficient authorization or confirmation?

These questions are intentionally not answered by the baseline implementation.

---

## Intended Lab03-Audit Direction

`lab03-audit` will be created only after Lab 03 is frozen.

Potential audit areas include:

```text
Authorization boundary
        │
        ├── resource selection
        ├── ownership
        └── restricted resources

State-changing authority
        │
        ├── create
        ├── update
        └── delete

Tool chaining
        │
        └── multi-step actions

Authority confusion
        │
        ├── user authority
        ├── agent authority
        └── backend authority
```

Later experiments may also introduce adversarial or indirectly controlled input.

No bypass or vulnerability is intentionally embedded in the baseline.

---

## Evidence Standard

A security finding should only be recorded when the experiment demonstrates observable security impact.

The laboratory distinguishes:

```text
Claimed capability
        ↓
Observed capability
        ↓
Implemented capability
        ↓
Reachable capability
        ↓
Exploitable capability
```

A tool being available does not by itself establish a vulnerability.

Similarly:

```text
Tool capability
≠
Network reachability
≠
Authorization
≠
Security impact
```

This distinction follows the methodology established in the previous laboratories.

---

## Framework Mapping

OWASP and MITRE ATT&CK / ATLAS references should be added only when supported by demonstrated behavior.

Framework mappings provide context and traceability.

They are not evidence of a vulnerability by themselves.

Potential future areas include:

* excessive agency;
* authorization failures;
* unsafe tool use;
* agentic action chains;
* confused-deputy-style behavior.

The final mapping will depend on the actual observations produced during `lab03-audit`.

---

## Implementation Constraints

Lab 03 intentionally keeps the implementation simple.

### No agent framework

The agent remains a small Python implementation using Ollama tool calling.

### No external database

State is represented by a JSON file in the target container.

### Explicit tools

Every security-relevant capability should be visible as an explicit Python function.

### Explicit identity

The agent identity is configured outside the LLM tool parameters.

### Backend authorization

Authorization decisions are enforced by the target application.

### Observable effects

State-changing operations must produce observable changes that can be independently verified.

---

## Directory Structure

```text
lab03-agent-stateful/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── README.md
├── src/
│   └── lab03_agent_stateful/
│       ├── agent.py
│       ├── main.py
│       └── tools/
│           ├── __init__.py
│           ├── network.py
│           └── records.py
└── target/
    ├── app.py
    └── Dockerfile
```

---

## Completion Criteria

Lab 03 will be considered complete when:

* the stateful target is implemented;
* the resource and authorization model is documented;
* agent identity is explicit;
* read and state-changing tools are implemented;
* the LLM can invoke the stateful tools;
* authorized operations work;
* unauthorized operations are denied;
* state changes are observable and reproducible;
* the baseline behavior is documented;
* the implementation is frozen before creating `lab03-audit`.

The audit phase will then start from the frozen Lab 03 baseline.

---

## Progression

```text
Lab 01
Basic agent
    │
    ▼
Lab 02
Network-capable isolated agent
    │
    ▼
Lab 02-audit
Capability and boundary experiments
    │
    ▼
Lab 03
Stateful agent
    │
    ├── identity
    ├── authorization
    ├── state
    └── side effects
    │
    ▼
Lab 03-audit
Authorization and agentic action experiments
```

The purpose of this progression is to increase agent authority incrementally while keeping each new security property independently observable and testable.
