# Deploy with Docker Compose

Use this guide to deploy the NVIDIA Nsight Copilot Blueprint with Docker Compose on a single DGX Spark.

This deployment provides the local backend for the Nsight Copilot Visual Studio Code extension. After required images and model artifacts are available on the DGX Spark, the extension can use the self-hosted backend without sending prompts or code to an external service.

First startup on DGX Spark can take tens of minutes — a one-time cost of pulling the container images and downloading the model weights from NGC into `OFFLINE_INFERENCE_DIR`. Restarts reuse the cached weights and skip the download.

On every start, including restarts, the services load the models one at a time, because the single GPU and 128 GB of unified memory (shared between CPU and GPU) cannot hold them all at once; memory is freed between each load. GPT-OSS is the slowest to load, around 15 minutes (engine initialization, compilation, CUDA graph capture, and KV-cache setup), and the other models are faster.

## Clone the Repository

```bash
git clone https://github.com/NVIDIA-AI-Blueprints/nsight-copilot.git
cd nsight-copilot
```

## Automated Setup

The setup script handles all prerequisites and starts the services:
```
curl -LsSf https://astral.sh/uv/install.sh | UV_INSTALL_DIR=/usr/local/bin sudo -E sh
sudo -E $(which uv) run deploy/compose/setup_nsc_with_offline_inference.py
```

The script is idempotent — safe to re-run if interrupted.

If you prefer to set things up manually, follow the steps below.

## Manual Setup

### Prerequisites

1. Install [Docker Engine](https://docs.docker.com/engine/install/ubuntu/) if it is not installed.

2. [Configure](https://docs.docker.com/engine/install/linux-postinstall/) Docker Engine to run without sudo if it is not configured.

3. Install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#with-apt-ubuntu-debian) if it is not installed.

4. [Configure](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#configuring-docker) NVIDIA Container Toolkit for Docker if it is not configured.

5. Generate an NGC API key if not generated:
   1. Go to [NGC](https://ngc.nvidia.com/setup) and log in.
   2. Select **Setup** > **Generate API Key**.
   3. Copy the key (starts with `nvapi-`).

6. Ensure you have at least **200 GB** of free disk space for Docker images, model weights, caches, and vector database data.

### Start Services

Export the required environment variables:

```bash
export NGC_API_KEY="nvapi-..."
export OFFLINE_INFERENCE_DIR=/some/path/you/like
export USER_ID=$(id -u)
```

- `NGC_API_KEY` is required to download models from NGC and to pull NIM container images.
- `OFFLINE_INFERENCE_DIR` is mounted to the containers and used to store model weights, so they don't need to be re-downloaded on subsequent runs.
- `USER_ID` is passed to the NIM containers so they run as the host user, avoiding permission issues on the mounted cache volumes.

Authenticate Docker with the NGC container registry:

```bash
echo "${NGC_API_KEY}" | docker login nvcr.io -u '$oauthtoken' --password-stdin
```

Start all services:

```bash
docker compose -f deploy/compose/compose.yaml up -d
```

### Verify the Deployment

After all services report healthy, you can verify them with sample requests.

#### Chat (GPT-OSS)

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-oss-120b medium reasoning + CUDA knowledge",
    "messages": [
      {"role": "user", "content": "Write a CUDA kernel that applies ReLU to a float array."}
    ],
    "max_tokens": 1024
  }'
```

### Code Completion

```bash
curl http://localhost:8080/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nvidia/CUDA-autocomplete",
    "prompt": "<|fim_prefix|>__global__ void relu_kernel(float* out, const float* in, int n) {\n    int i = blockIdx.x * blockDim.x + threadIdx.x;\n    if (i < n) {\n        out[i] = <|fim_suffix|>;\n    }\n}\n<|fim_middle|>",
    "max_tokens": 32,
    "temperature": 0.01,
    "stop": ["<|endoftext|>", "<|fim_prefix|>", "<|fim_middle|>", "<|fim_suffix|>"]
  }'
```

#### Reranking

```bash
curl -X POST "http://localhost:8020/v1/ranking" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nvidia/llama-nemotron-rerank-1b-v2",
    "query": {
      "text": "What is the GPU memory bandwidth of H100 SXM?"
    },
    "passages": [
      {
        "text": "Accelerated servers with H100 deliver the compute power along with 3 terabytes per second (TB/s) of memory bandwidth per GPU and scalability with NVLink and NVSwitch."
      },
      {
        "text": "A100 provides up to 20X higher performance over the prior generation and can be partitioned into seven GPU instances to dynamically adjust to shifting demands."
      }
    ]
  }'
```

## Use the Blueprint

Connect a client to the local backend to start using the blueprint.

### Connect from IDE

#### Visual Studio Code
After the services are running on DGX Spark, connect from Visual Studio Code:

1. Install [NVIDIA Sync](https://docs.nvidia.com/dgx/dgx-spark/nvidia-sync.html).
2. Connect [NVIDIA Sync](https://docs.nvidia.com/dgx/dgx-spark/nvidia-sync.html) to DGX Spark.
3. Select **VSCode** from NVIDIA Sync Apps. For more information, see NVIDIA's [Visual Studio Code on DGX Spark](https://build.nvidia.com/spark/vscode/overview)
   guide.
4. After Visual Studio Code starts, install the
   [Nsight Copilot Visual Studio Code extension](https://marketplace.visualstudio.com/items?itemName=NVIDIA.nsight-copilot)
   from the Visual Studio Marketplace.
5. Configure the Nsight Copilot extension to use the self-hosted backend: In Visual Studio Code, click on the Extensions tab -> find Nsight Copilot -> click on its gear icon -> click on Settings -> change `Server Origin` value to `http://localhost:8080`
6. Forward DGX Spark port `8080` to local port `8080`: In Visual Studio Code,
   open **Terminal** > **New Terminal**, switch to the **Ports** tab, and forward port `8080`.
   For more options, see the Visual Studio Code documentation for
   [port forwarding](https://code.visualstudio.com/docs/debugtest/port-forwarding) and
   [Remote SSH](https://code.visualstudio.com/docs/remote/ssh).

#### VS Code-compatible forks

Cursor, Windsurf, and VSCodium may work with additional extension-install and port-forwarding adjustments. These clients may not appear as native NVIDIA Sync apps. If the Visual Studio Marketplace is not available in the client, install the [Nsight Copilot extension from Open VSX](https://open-vsx.org/extension/NVIDIA/nsight-copilot), then configure `Server Origin` to `http://localhost:8080` and forward DGX Spark port `8080` to local port `8080`.

### Model Context Protocol (MCP)

The Nsight Copilot server exposes an MCP endpoint at `http://localhost:8080/mcp/cuda-docs`
(once port `8080` is forwarded from DGX Spark). It provides a single tool,
`search_cuda_docs`, that performs semantic search over a curated corpus of NVIDIA CUDA
documentation and code samples — current through early 2026, including libraries that
post-date most model training cutoffs (such as cuTile). An MCP-capable client can call
it to ground answers in current, authoritative CUDA material.

#### Flow

1. An MCP client (your IDE or agent) connects to `http://localhost:8080/mcp/cuda-docs`.
2. The client calls `search_cuda_docs` with a natural-language query.
3. The server retrieves matching documentation and code samples from the RAG
   backend, reranks them, and returns the context to the client.

## Service Ports

| Service | Host Port | Description |
|---------|-----------|-------------|
| LiteLLM unified proxy | 8000 | OpenAI-compatible gateway for internal services |
| GPT-OSS NIM | 8010 | Direct chat/reasoning NIM endpoint |
| CUDA autocomplete NIM | 8011 | Direct fill-in-the-middle code completion endpoint |
| Rerank NIM | 8020 | Direct reranking endpoint |
| RAG server | 8030 | Direct CUDA document retrieval backend |
| Nsight Copilot server | 8080 | Primary backend API for IDE clients and API users |
| Milvus | 19530, 9091 | Vector database and health endpoint |
| MinIO | 9000, 9001 | Object storage API and console |

## Local Data and Privacy

In the default offline Compose deployment, prompts and code are served by local containers. The stack uses NGC for image and model downloads, and `OFFLINE_INFERENCE_DIR` for local model caches. Do not override the model endpoints to external services unless your deployment policy allows code or prompt data to leave the machine.

## Troubleshooting

| Symptom | Likely cause | What to check |
|---------|--------------|---------------|
| `docker pull` or NIM startup returns unauthorized | NGC key lacks required access | Re-run `docker login nvcr.io` and confirm the NGC key can pull `nvcr.io/nim/*` and `nvcr.io/nvidia/blueprint/*` images. |
| Startup is slow or never completes | Services start one at a time (DGX Spark holds one model at a time), each gated on the previous passing its healthcheck plus a cache flush; first run also pulls model weights from NGC. A NIM that fails to initialize halts the whole chain and the main server never starts. | `docker compose ps` to see which service is currently `starting` or stuck `unhealthy` (or a `cache-flush`/`test-*` step that did not complete); `docker compose logs -f <service>` to follow it. First-run init is budgeted (GPT-OSS up to ~20 minutes) — if it is still progressing, wait; a service past its budget has genuinely failed. |
| Disk fills during setup | Docker images plus model caches exceed available space | Meet the Prerequisites free-disk requirement; move `OFFLINE_INFERENCE_DIR` to a larger disk if needed. |
| NIM reports no compatible profile or memory pressure | Host is not a DGX Spark | This blueprint targets NVIDIA DGX Spark only. Verify the host is a DGX Spark; NIM profile and memory settings are tuned for DGX Spark and are not user-configurable. |
| GPU containers cannot see GPUs | NVIDIA Container Toolkit missing or unconfigured | Run `docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi`. If it fails, see the [NVIDIA Container Toolkit troubleshooting guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/troubleshooting.html). |
| No autocomplete suggestions in the IDE | Backend URL, port forwarding, or autocomplete service issue, or autocomplete toggle is off | Confirm the extension `Server Origin` is `http://localhost:8080`; confirm port `8080` is forwarded from DGX Spark to the client machine; check `docker compose ps autocomplete-nim litellm` shows both as `healthy`; verify autocomplete is enabled — click **Nsight Copilot** in the VS Code status bar (bottom-right) and ensure **Enable autocomplete** is on. |
| Autocomplete suggestions are poor, distracting, or contain stray tokens | File language outside the model's primary training scope (CUDA, C++, Python), or autocomplete is not wanted for this session | The autocomplete model is fine-tuned mainly on CUDA, C++, and Python code; completion quality on other languages is limited. To disable inline suggestions, click **Nsight Copilot** in the VS Code status bar (bottom-right) and toggle **Enable autocomplete** off. The same menu re-enables it. |
| MCP tools unavailable, or `search_cuda_docs` returns no context | The MCP endpoint is not reachable, or the RAG backend has no data | Confirm the MCP client points at `http://localhost:8080/mcp/cuda-docs` and that port `8080` is forwarded from DGX Spark to the client machine; confirm `docker compose ps rag-server-offline` is `healthy` and check its logs for retrieval errors. |
| Port already in use | Another service is bound to the same port — either the published Compose port on DGX Spark, or the forwarded local port on the client | Identify which side collides. **On DGX Spark:** run `sudo ss -ltnp 'sport = :8080'` (or `sudo lsof -i :8080`) to find the pre-existing process holding the port; stop that process (recommended — DGX Spark resources are limited, so avoid a competing service) or, if it must keep running, change the published port in `deploy/compose/compose.yaml`. **On the client:** in the VS Code **Ports** tab, stop the process using the local port and re-forward, or edit the **Local Address** to a free port (for example `8081`) and update the extension `Server Origin` to match (`http://localhost:8081`). |
