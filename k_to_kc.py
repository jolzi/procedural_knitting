import subprocess, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent
backend = ROOT / "external" / "knitout-backend-kniterate" / "knitout-to-kcode.js"

def k_to_kc(k_path: str | pathlib.Path) -> pathlib.Path:
    k_path = pathlib.Path(k_path)
    kc_path = k_path.with_suffix(".kc")
    subprocess.run(
        ["node", str(backend), str(k_path), str(kc_path)],
        check=True
    )
    return kc_path
