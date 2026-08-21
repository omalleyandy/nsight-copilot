nvidia-copilot helper

Purpose

This small helper script displays the Docker Compose self-hosted deployment guide for the NVIDIA Nsight Copilot Blueprint on a single DGX Spark.

Files

- [tools/nvidia-copilot](nvidia-copilot) — executable helper script. Run it to print or page the guide.
- [docs/deploy-docker-self-hosted.md](../docs/deploy-docker-self-hosted.md) — the full deployment guide the helper shows.

Usage

- Show the guide on stdout:

    tools/nvidia-copilot

- Open the guide in a pager (less) if available:

    tools/nvidia-copilot --pager

- Print the absolute path to the guide file:

    tools/nvidia-copilot --path

- Show help:

    tools/nvidia-copilot --help

Use from other repositories

The guide is useful outside this checkout, so put the script on your PATH with a
symlink rather than copying it:

    ln -s "$PWD/tools/nvidia-copilot" ~/.local/bin/nvidia-copilot

Then run `nvidia-copilot` from any directory. The script resolves its own real
path, so the symlink still points it back at this repository's
docs/deploy-docker-self-hosted.md.

Copying the script elsewhere does not work: it looks for the guide under the
parent of whatever directory the copy lives in, and exits with "Guide not found"
when there is no docs/deploy-docker-self-hosted.md there.

Notes

- The script assumes it is located in the repository under tools/ and resolves the repo root relative to its own location.
- Symlink the script onto your PATH to use it from other repositories; do not copy it.
- It is meant to be a lightweight convenience for contributors and operators who want a quick way to view the deployment instructions without hunting through the docs/ directory.
