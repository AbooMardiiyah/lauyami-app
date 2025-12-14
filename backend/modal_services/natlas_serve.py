"""Deploy N-ATLaS LLM model on Modal with vLLM.

This service provides an OpenAI-compatible API endpoint for the N-ATLaS causal LLM.
Supports Yoruba, Hausa, Igbo, and Nigerian Accented English.

Deploy: modal deploy modal_services/natlas_serve.py
Usage: https://your-workspace--natlas-vllm-serve.modal.run/v1
"""

import modal
import subprocess


vllm_image = (
    modal.Image.from_registry("nvidia/cuda:12.8.0-devel-ubuntu22.04", add_python="3.12")
    .entrypoint([])
    .uv_pip_install(
        "vllm==0.11.2",
        "huggingface-hub==0.36.0",
        "flashinfer-python==0.5.2",
    )
    .env({"HF_XET_HIGH_PERFORMANCE": "1"})
)

## used deployment guide from https://huggingface.co/tosinamuda/N-ATLaS-FP8/blob/main/deploy-guide.md 

MODEL_NAME = "tosinamuda/N-ATLaS-FP8"
MODEL_REVISION = "360713ddec72a18a3fcb2f3a211e16c1de390930"

hf_cache_vol = modal.Volume.from_name("huggingface-cache", create_if_missing=True)
vllm_cache_vol = modal.Volume.from_name("vllm-cache", create_if_missing=True)

FAST_BOOT = True

app = modal.App("natlas-vllm")

N_GPU = 1
MINUTES = 60
VLLM_PORT = 8000


@app.function(
    image=vllm_image,
    gpu=f"H100:{N_GPU}",
    scaledown_window=15 * MINUTES,
    timeout=10 * MINUTES,
    volumes={
        "/root/.cache/huggingface": hf_cache_vol,
        "/root/.cache/vllm": vllm_cache_vol,
    },
)
@modal.concurrent(max_inputs=32)
@modal.web_server(port=VLLM_PORT, startup_timeout=10 * MINUTES)
def serve():
    
    cmd = [
        "vllm",
        "serve",
        MODEL_NAME,
        "--revision",
        MODEL_REVISION,
        "--served-model-name",
        "n-atlas",
        "--host",
        "0.0.0.0",
        "--port",
        str(VLLM_PORT),
        "--uvicorn-log-level=info",
    ]

    cmd += ["--enforce-eager" if FAST_BOOT else "--no-enforce-eager"]
    cmd += ["--tensor-parallel-size", str(N_GPU)]

    print(cmd)
    subprocess.Popen(" ".join(cmd), shell=True)

