import os
import argparse
from pathlib import Path
import subprocess

def generate_artifacts(args):
    # Check if the artifacts exists in the path
    source = Path(args.path)
    if (not source.exists()):
        print("Artifacts path does not exist")
        exit(1)
    
    irpa_path = Path(os.path.join(args.path, "quark_mistral_nemo.irpa"))
    if (not irpa_path.exists()):
        print("irpa file does not exists")
        exit(1)

    output_mlir = "quark_mistral_nemo.mlir"
    output_config = "quark_config.json"
    output_vmfb = "quark_mistral_nemo.vmfb"

    if os.path.exists(args.output_dir):
        root_dir = os.path.abspath(args.output_dir)
    else:
        root_dir = os.getcwd()

    for prefill in args.prefill_bs:
        for decode in args.decode_bs:
            if prefill > decode:
                continue
            output_path = f"BS_{prefill}_{decode}"
            if os.path.exists(root_dir):
                output_path = os.path.abspath(os.path.join(root_dir, output_path))
                if not Path(output_path).exists():
                    os.makedirs(output_path)
            else:
                print("Does not exist")
            os.chdir(output_path)
            export_command = f"python -m sharktank.examples.export_paged_llm_v1 --irpa-file={irpa_path} --output-mlir={output_mlir} --output-config={output_config} --bs-prefill={prefill} --bs-decode={decode} --activation-dtype=bfloat16 --attention-dtype=bfloat16 --use-hf --attention-kernel=torch --fake-quant --kv-cache-dtype=float8_e4m3fnuz --device-block-count 4096"
            os.system(export_command)
            iree_command = f"~/iree-build/tools/iree-compile {output_mlir} --iree-hal-target-device=hip  --iree-hip-target=gfx942  -o {output_vmfb} --iree-opt-level=O3   --iree-hal-indirect-command-buffers=true   --iree-stream-resource-memory-model=discrete   --iree-hal-memoization=true"
            os.system(iree_command)


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Generate artifacts for chai nemo"
    )

    # Add arguments
    parser.add_argument(
        "--path",
        type=Path,
        required=True,
        help="Path to the dir containing artifacts",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default="",
        help="Path to output artifacts",
    )
    parser.add_argument(
        "--prefill-bs",
        type=int,
        default=8,
        nargs="*",
        help="Prefil batch sizes",
    )
    parser.add_argument(
        "--decode-bs",
        type=int,
        default=8,
        nargs="*",
        help="Decode batch sizes",
    )
    # Parse arguments
    args = parser.parse_args()
    generate_artifacts(args)



