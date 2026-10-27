"""Builds wheel-kernel/: a Kaggle script that writes the plagx-cite wheel to its output.

Usage: python make_wheel_kernel.py <wheel file> <kaggle username>
"""
import base64
import json
import sys
from pathlib import Path

wheel, user = Path(sys.argv[1]), sys.argv[2]
data = base64.b64encode(wheel.read_bytes()).decode()

out = Path("wheel-kernel")
out.mkdir(exist_ok=True)
(out / "plagx_cite_wheel.py").write_text(
    "# Writes the plagx-cite wheel from PyPI (MIT) to the output folder,\n"
    "# so the Plagx Research Kit notebook can install it without internet.\n"
    "import base64\n"
    f"open({wheel.name!r}, 'wb').write(base64.b64decode({data!r}))\n"
    f"print('Wrote', {wheel.name!r})\n",
    encoding="utf-8",
)
(out / "kernel-metadata.json").write_text(json.dumps({
    "id": f"{user}/plagx-cite-wheel",
    "title": "plagx-cite wheel",
    "code_file": "plagx_cite_wheel.py",
    "language": "python",
    "kernel_type": "script",
    "is_private": True,
    "enable_gpu": False,
    "enable_tpu": False,
    "enable_internet": False,
    "dataset_sources": [],
    "kernel_sources": [],
    "competition_sources": [],
}, indent=2), encoding="utf-8")
print(f"Wrote {out}/ for {wheel.name}")
