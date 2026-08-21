nvidia-copilot helper

Purpose

This small helper script displays the Docker Compose self-hosted deployment guide for the NVIDIA Nsight Copilot Blueprint on a single DGX Spark.

Files

- [tools/nvidia-copilot](/home/omalleyandy/projects/nsight-copilot/tools/nvidia-copilot) — executable helper script. Run it to print or page the guide.
- [docs/deploy-docker-self-hosted.md](/home/omalleyandy/projects/nsight-copilot/docs/deploy-docker-self-hosted.md) — the full deployment guide the helper shows.

Usage

- Show the guide on stdout:

    tools/nvidia-copilot

- Open the guide in a pager (less) if available:

    tools/nvidia-copilot --pager

- Print the absolute path to the guide file:

    tools/nvidia-copilot --path

- Show help:

    tools/nvidia-copilot --help

Notes

- The script assumes it is located in the repository under tools/ and resolves the repo root relative to its own location.
- It is meant to be a lightweight convenience for contributors and operators who want a quick way to view the deployment instructions without hunting through the docs/ directory.
