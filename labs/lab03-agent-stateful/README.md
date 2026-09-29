# Lab 03 — Stateful Agent

## Objective

Lab 03 extends the isolated agent architecture introduced in Lab 02 by giving the agent access to a stateful web application and tools capable of modifying persistent state.

The objective is to study the security implications of an agent that can move beyond network reconnaissance and perform actions with observable side effects.

The lab introduces:

* persistent application state
* an explicit agent identity and execution context
* resources with different authorization levels
* read-only tools
* state-changing tools
* resource ownership
* authorization decisions at the application boundary

The lab is intentionally simple. It does not attempt to model a production authorization system or introduce an agent framework.

The main conceptual transition is:

```text
Lab 02:

LLM
 │
 ▼
Agent
 │
 ▼
Network Tools
 │
 ▼
Network Reachability
```

to:

```text
Lab 03:

LLM
 │
 ▼
Agent
 │
 ▼
Tools
 │
 ▼
Authorization
 │
 ▼
Action
 │
 ▼
Persistent State
```

The purpose of this lab is to provide the capabilities and security boundaries that will later be examined in `lab03-audit`.

---

## Security Context

Lab 02 demonstrated that an agent can have real network capabilities and that network-level isolation is different from application-level resource restrictions.

Lab 03 introduces a different security dimension: **agentic actions against persistent state**.

The agent is no longer limited to observing or reaching resources. It can invoke operations that can change the state of an external system.

This creates a new security boundary:

```text
                 Authorization Boundary
                        │
                        ▼
LLM → Agent → Tool → Target Application → Persistent State
                  │
                  └── action requested
```

The important distinction is between:

1. what the model requests,
2. what the agent is capable of invoking,
3. what the tool actually executes,
4. what the target application authorizes,
5. what state is ultimately changed.

The lab should make these layers observable so that they can be investigated independently during the audit phase.

---

## Scope

Lab 03 focuses on **agent authority over application state**.

The laboratory covers:

* agent identity and context
* resource ownership
* resource classification
* read operations
* state-changing operations
* authorization decisions
* persistent state
* observable side effects
* tool-driven interaction with an external application

The laboratory does not intentionally introduce:

* prompt injection
* indirect prompt injection
* complex multi-agent architectures
* autonomous long-running loops
* external SaaS integrations
* production authentication systems
* production-grade identity management
* complex databases
* an agent construction framework such as LangChain or AutoGen

Those capabilities may be introduced in later laboratories when they are useful for testing additional security properties.

---

## Architecture

The architecture builds on the isolated network model used in Lab 02.

```text
                     ┌───────────────┐
                     │    Ollama     │
                     └───────┬───────┘
                             │
                             ▼
                     ┌───────────────┐
                     │     Agent     │
                     │               │
                     │ identity:     │
                     │ analyst       │
                     └───────┬───────┘
                             │
                             │ HTTP tools
                             ▼
                     ┌───────────────────┐
                     │ Target Web App    │
                     │                   │
                     │ Authorization     │
                     │ Persistent State  │
                     └─────────┬─────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
        Public Data      Analyst Data      Restricted Data
```

The target remains a simple web application rather than introducing a separate database service.

This keeps the laboratory architecture small while still providing persistent state and externally observable side effects.

---

## Agent Identity

The agent executes with an explicit application identity.

The initial execution context is:

```text
user: analyst
role: analyst
```

This identity is part of the laboratory design and provides a basis for authorization decisions.

The identity is intentionally simple. It is not intended to represent a complete authentication or identity-management system.

The relevant security question is whether the identity and associated authorization context are actually respected when the agent performs actions against resources.

---

## Resource Model

The target application contains resources belonging to different security classes.

The initial resource classes are:

| Resource class | Description                                                     |
| -------------- | --------------------------------------------------------------- |
| Public         | Data intended to be readable by any authorized application user |
| Analyst-owned  | Data owned by the `analyst` identity                            |
| Restricted     | Data that the `analyst` identity is not authorized to access    |

The resource model should make ownership and authorization decisions explicit enough that they can be tested during the audit phase.

An example conceptual dataset is:

```text
public/
  record-001
  record-002

analyst/
  record-101
  record-102

restricted/
  record-201
  record-202
```

The identifiers and exact implementation are implementation details. The security properties of the resource classes are the important part.

---

## Authorization Model

The initial authorization model is intentionally small.

For the `analyst` identity:

| Resource           | Read | Modify | Delete |
| ------------------ | ---: | -----: | -----: |
| Public data        |  Yes |     No |     No |
| Analyst-owned data |  Yes |    Yes |    Yes |
| Restricted data    |   No |     No |     No |

Creating a new record is authorized within the agent's permitted application context.

The authorization model is a design contract for the target application.

It should not be assumed that the existence of a tool or an HTTP endpoint constitutes authorization.

The intended security boundary is:

```text
Agent request
     │
     ▼
Target application
     │
     ├── identify resource
     ├── determine ownership/class
     ├── evaluate authorization
     │
     ▼
Allow / Deny
     │
     ▼
State change
```

The audit phase will determine whether the implemented system actually behaves according to this model.

---

## Agent Tools

The agent receives tools for interacting with the target application.

The initial tool set is divided into read-only and state-changing operations.

### Read-only tools

```text
get_record()
list_records()
```

These tools retrieve application state without modifying it.

### State-changing tools

```text
create_record()
update_record()
delete_record()
```

These tools can produce persistent side effects.

The tools should perform real HTTP requests against the target application rather than modifying local agent state directly.

This preserves the architecture:

```text
LLM
 │
 ▼
Agent
 │
 ▼
Tool
 │
 ▼
HTTP request
 │
 ▼
Target application
 │
 ▼
Persistent state
```

---

## Tool Semantics

The conceptual tool model is:

| Tool            | Side effect | Security relevance                          |
| --------------- | ----------: | ------------------------------------------- |
| `get_record`    |          No | Resource read authorization                 |
| `list_records`  |          No | Resource enumeration and read authorization |
| `create_record` |         Yes | Creation authority                          |
| `update_record` |         Yes | Modification authority and ownership        |
| `delete_record` |         Yes | Destructive authority and ownership         |

The tools should expose enough parameters for the agent to operate on concrete resources.

At the same time, the target application remains responsible for deciding whether the requested operation is authorized.

The laboratory should therefore make it possible to distinguish:

```text
tool availability
        ≠
tool invocation
        ≠
application authorization
        ≠
successful state change
```

---

## Persistent State

Unlike Lab 02, the target application maintains state across requests.

The state should be observable through the application interface.

For example:

```text
Initial state
    │
    ├── record-001
    ├── record-101
    └── record-201
          │
          ▼
      Agent action
          │
          ▼
     Target application
          │
          ▼
    Updated state
```

State-changing operations must have an observable result.

Examples include:

* a new record appearing after `create_record`
* an existing record changing after `update_record`
* a record disappearing after `delete_record`

The implementation should make these changes easy to verify manually and during the audit phase.

---

## Side Effects

Side effects are a central part of this laboratory.

A successful tool invocation is not sufficient evidence that an action occurred.

The laboratory should provide a way to verify the resulting application state.

For example:

```text
Agent
  │
  │ update_record(record-101)
  ▼
Target
  │
  │ authorization
  ▼
State change
  │
  ▼
GET record-101
  │
  ▼
Observed new state
```

This allows later experiments to establish a complete chain of evidence:

```text
model decision
    ↓
tool invocation
    ↓
HTTP request
    ↓
authorization decision
    ↓
application response
    ↓
persistent state change
```

---

## Security Boundaries

Lab 03 introduces several boundaries that should remain conceptually separate.

### Model boundary

The LLM decides which tool to invoke and which parameters to provide.

### Agent boundary

The agent exposes and executes the available tools.

### Tool boundary

The tool translates an agent action into an HTTP request.

### Authorization boundary

The target application decides whether the requested operation is permitted.

### Resource boundary

The target application determines which resources the requesting identity can access or modify.

### State boundary

The target application persists the resulting state.

These boundaries allow later experiments to determine where a security property is enforced and where it is not.

---

## Expected Baseline Behavior

Before beginning the audit phase, the implementation should establish the intended baseline behavior.

For the `analyst` identity:

### Public resources

The agent should be able to read public resources.

It should not be able to modify or delete them.

### Analyst-owned resources

The agent should be able to read and modify resources owned by the `analyst`.

It should also be able to delete resources where the authorization model permits deletion.

### Restricted resources

The agent should not be able to read, modify, or delete restricted resources.

### Creation

The agent should be able to create resources within the authorization context defined by the application.

The exact resource ownership semantics for newly created resources must be explicit in the implementation.

---

## Observability

The laboratory should provide sufficient observability to establish what happened during an experiment.

At minimum, the following should be distinguishable:

```text
User / agent context
Tool selected
Tool parameters
HTTP request
HTTP response
Authorization result
State before action
State after action
```

This is important because an agent may:

* decide to perform an action,
* invoke a tool,
* receive an authorization failure,
* or successfully modify state.

These are different observations and must not be conflated.

---

## Security Questions

Lab 03 is designed to support investigation of questions such as:

1. Can the agent invoke state-changing tools?
2. Can the model select the resource affected by a state-changing operation?
3. Does the target application enforce resource ownership?
4. Are authorization decisions made independently of the model's instructions?
5. Can the agent modify resources outside its intended authorization scope?
6. Can the agent delete resources outside its intended authorization scope?
7. Does tool chaining produce a security-relevant action that individual tools do not reveal in isolation?
8. Is the identity used by the agent consistently enforced by the target application?
9. Does the backend authority exceed the authority intended for the agent?
10. Can an action that is individually permitted be combined with another permitted action to produce an unintended security-relevant result?

These are **audit questions**, not findings.

No security finding should be recorded until the relevant behavior has been demonstrated and its security impact established.

---

## Relationship to Lab 02

Lab 03 builds directly on the lessons from Lab 02 and `lab02-audit`.

Lab 02 focused on network capability and reachability.

The important progression is:

```text
Lab 02

Can the agent reach a resource?

        ↓

Lab 03

What can the agent do once it can interact with a resource?
```

This distinction is important because:

```text
Capability
    ≠
Reachability
    ≠
Authorization
    ≠
Security impact
```

Lab 03 therefore moves the security analysis from network boundaries toward **agent authority and application state**.

---

## Intended Audit Direction

A future `lab03-audit` should be created only after this laboratory is implemented, tested, documented, and frozen.

The audit may investigate areas such as:

* authorization boundary enforcement
* excessive agency
* state-changing tool authority
* resource ownership enforcement
* destructive actions
* tool chaining
* authorization confusion
* confused-deputy behavior
* differences between agent authority and backend authority

The audit should use controlled experiments and reproducible evidence.

Potential findings must not be assumed in advance.

---

## Evidence Standard

A behavior should only become a security finding when the following chain can be demonstrated:

```text
Capability
    ↓
Observed behavior
    ↓
Security-relevant boundary crossed
    ↓
Concrete impact
    ↓
Reproducible evidence
```

The existence of a tool, endpoint, or model capability is not by itself a vulnerability.

Similarly:

```text
"the agent can call update_record"
```

does not establish:

```text
"the agent can update an unauthorized record"
```

The latter requires an experiment demonstrating the unauthorized action and its resulting impact.

---

## Framework Mapping

Security framework mappings should be added only after the underlying behavior has been demonstrated.

Potential mappings may include relevant concepts from:

* OWASP guidance for LLM and agent security
* MITRE ATLAS
* MITRE ATT&CK where applicable

Framework categories are used for traceability and communication.

They are not used as evidence of a vulnerability.

The implementation and experimental evidence remain the primary source of truth.

---

## Implementation Constraints

The laboratory should remain intentionally small and understandable.

The implementation should:

* use Python
* use the existing project tooling
* keep the agent implementation explicit
* keep tool definitions easy to inspect
* use the existing Ollama-based architecture
* keep the target application simple
* avoid unnecessary dependencies
* avoid introducing an agent framework
* keep state and authorization behavior visible
* make security-relevant actions reproducible

The goal is to create an environment where the security behavior can be understood from the source code and reproduced from the documented commands.

---

## Directory Structure

The laboratory follows the structure established by Lab 02:

```text
lab03-agent-stateful/
├── docker-compose.yml
├── Dockerfile
├
```
