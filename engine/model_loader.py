import os
import tarfile
import urllib.request
from typing import Dict

DEFAULT_MODEL_NAME = "sherpa-onnx-streaming-zipformer-en-20M-2023-02-17"
DEFAULT_MODEL_URL = f"https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/{DEFAULT_MODEL_NAME}.tar.bz2"

def get_model_paths(model_dir: str) -> Dict[str, str]:
    encoder = os.path.join(model_dir, "encoder-epoch-99-avg-1.onnx")
    decoder = os.path.join(model_dir, "decoder-epoch-99-avg-1.onnx")
    joiner = os.path.join(model_dir, "joiner-epoch-99-avg-1.onnx")
    tokens = os.path.join(model_dir, "tokens.txt")
    return {
        "encoder": encoder,
        "decoder": decoder,
        "joiner": joiner,
        "tokens": tokens
    }

def is_model_complete(model_dir: str) -> bool:
    paths = get_model_paths(model_dir)
    return all(os.path.isfile(p) and os.path.getsize(p) > 0 for p in paths.values())

def download_and_extract_model(
    model_name: str = DEFAULT_MODEL_NAME,
    models_root: str = "models",
    progress_callback = None
) -> Dict[str, str]:
    os.makedirs(models_root, exist_ok=True)
    target_dir = os.path.join(models_root, model_name)
    if is_model_complete(target_dir):
        return get_model_paths(target_dir)

    tar_path = os.path.join(models_root, f"{model_name}.tar.bz2")
    if not os.path.exists(tar_path):
        req = urllib.request.Request(
            DEFAULT_MODEL_URL,
            headers={"User-Agent": "PustaSub-ModelLoader/1.0"}
        )
        with urllib.request.urlopen(req) as response, open(tar_path, "wb") as out_file:
            total_size = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            chunk_size = 1024 * 512
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                out_file.write(chunk)
                downloaded += len(chunk)
                if progress_callback is not None:
                    progress_callback(downloaded, total_size)

    with tarfile.open(tar_path, "r:bz2") as tar:
        tar.extractall(path=models_root)

    if os.path.exists(tar_path):
        try:
            os.remove(tar_path)
        except Exception:
            pass

    if not is_model_complete(target_dir):
        raise RuntimeError(f"Extracted model at {target_dir} is incomplete.")

    return get_model_paths(target_dir)
