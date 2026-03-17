# infra-orchestrator

Self-service AWS infrastructure provisioning orchestrated from GitHub.

This repository hosts:

- A GitHub Pages form for developers to request infrastructure
- A GitHub Actions workflow that creates project repos and provisions AWS resources
- Validation and Terraform generation scripts
- Composable Terraform modules for frontend, database, storage, and compute services

The implementation details live in [implementation-plan.md](implementation-plan.md).
