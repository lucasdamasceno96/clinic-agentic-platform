# AI Context: Clinic Agentic Platform

## Project Overview
- **Goal**: Create an AI Patient Care Orchestrator for 'LDP Labs Clinic'.
- **Primary Roles**: Appointment scheduling and Clinical Protocol RAG.
- **Framework**: google-agents-cli (v0.1.3) + Google ADK (Agent Development Kit).
- **Platform**: Google Cloud (Vertex AI, Cloud Run, Cloud Logging).

## Technical Architecture
- **Language**: Python 3.11+.
- **Agent Template**: `agentic_rag`.
- **Infrastructure**: Managed via `agents-cli infra` (Terraform/Cloud Run).
- **Security**: Must comply with HIPAA and LGPD (No PII leakage, no medical diagnosis).

## Development Rules
- **Coding Language**: All code, docstrings, variable names, and comments MUST be in English.
- **Communication Language**: Explanations and documentation for the user should be in Portuguese.
- **Standards**: Clean Code, Pydantic for type safety, Conventional Commits.
- **Tooling**: Use `uv` for dependency management.

## Current State
- [x] Project Repository Initialized.
- [x] Project Scaffolded (agent-core).
- [ ] System Instructions defined in agent.yaml.
- [ ] Appointment tools implemented.
- [ ] RAG Datastore provisioned.
