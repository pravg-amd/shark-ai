import os
import argparse
from pathlib import Path
import subprocess
import csv


def get_csv_field(reader, key_val):
    for row in reader:
        print("Row is ", row)
        return row[key_val]

def run_perf(itl, otl, req_len, out_dir, prefill_bs, decode_bs):
    out_dir = os.path.join(out_dir, f"{itl}_{otl}_{req_len}_{prefill_bs}")
    export_command = f"python -m shortfin_apps.llm.benchmark_client --endpoint http://localhost:8020 --min-concurrent-requests={req_len} --max-concurrent-requests={req_len} --results-dir={out_dir} --output-token-length={otl} --input-token-lengths={itl}"
    os.system(export_command)


    with open("fp8_tom_chai_benchmark_bo8.csv", "a", newline="") as csvfile:
        fieldnames = ["Prefill", "Decode", "Input Token length", "Output Token length", "Concurrent Requests", "Total Time", "RPS", "E2E latency", "TTFT Median", "TPOT Median", "Throughput"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # writer.writeheader()

        d = os.path.join(out_dir, "benchmark_results_greedy.csv")
        with open(d, "r", newline="") as benchmark_csv:
            benchmark_reader = csv.DictReader(benchmark_csv)
            row = {}
            for r in benchmark_reader:
                row = r

            new_rows = {}
            new_rows["Prefill"] = prefill_bs
            new_rows["Decode"] = decode_bs
            new_rows["Input Token length"] = itl
            new_rows["Output Token length"] = otl
            new_rows["Concurrent Requests"] = req_len
            new_rows["Total Time"] = row["total_time"]
            new_rows["RPS"] = row["requests_per_second"]
            new_rows["E2E latency"] = row["E2E_latency"]
            new_rows["TTFT Median"] = row["TTFT_median"]
            new_rows["TPOT Median"] = row["TPOT_median"]


        d = os.path.join(out_dir, "throughput_results_greedy.csv")
        with open(d, "r", newline="") as benchmark_csv:
            benchmark_reader = csv.DictReader(benchmark_csv)
            for r in benchmark_reader:
                row = r
            new_rows["Throughput"] = row["throughput"]

        writer.writerow(new_rows)


def run_benchmark(args):
    # Check if the artifacts exists in the path
    input_token_lengths = [128, 256, 512, 1024, 2048]
    output_token_lengths = [64, 128]
    concurrent_requests = [2, 3, 4, 5]

    # input_token_lengths = [128, 256]
    # output_token_lengths = [64, 128]
    # concurrent_requests = [32]
    for itl in input_token_lengths:
        for otl in output_token_lengths:
            for req in concurrent_requests:
                run_perf(itl, otl, req, args.output_dir, args.prefill_bs, args.decode_bs)

    # output_mlir = "quark_mistral_nemo.mlir"
    # output_config = "quark_config.json"
    # output_vmfb = "quark_mistral_nemo.vmfb"

    # if os.path.exists(args.output_dir):
    #     root_dir = os.path.abspath(args.output_dir)
    # else:
    #     root_dir = os.getcwd()

    # for prefill in args.prefill_bs:
    #     for decode in args.decode_bs:
    #         if prefill > decode:
    #             continue
    #         output_path = f"BS_{prefill}_{decode}"
    #         if os.path.exists(root_dir):
    #             output_path = os.path.abspath(os.path.join(root_dir, output_path))
    #             if not Path(output_path).exists():
    #                 os.makedirs(output_path)
    #         else:
    #             print("Does not exist")
    #         os.chdir(output_path)
    #         export_command = f"python -m sharktank.examples.export_paged_llm_v1 --irpa-file={irpa_path} --output-mlir={output_mlir} --output-config={output_config} --bs-prefill={prefill} --bs-decode={decode} --activation-dtype=bfloat16 --attention-dtype=bfloat16 --use-hf --attention-kernel=torch --fake-quant --kv-cache-dtype=float8_e4m3fnuz --device-block-count 4096"
    #         os.system(export_command)
    #         iree_command = f"~/iree-build/tools/iree-compile {output_mlir} --iree-hal-target-device=hip  --iree-hip-target=gfx942  -o {output_vmfb} --iree-opt-level=O3   --iree-hal-indirect-command-buffers=true   --iree-stream-resource-memory-model=discrete   --iree-hal-memoization=true"
    #         os.system(iree_command)


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Generate artifacts for chai nemo"
    )

    # Add arguments
    parser.add_argument(
        "--output-dir",
        type=Path,
        default="results",
        help="Path to output artifacts",
    )
    
    # parser.add_argument(
    #     "--input-token-lengths",
    #     type=int,
    #     nargs="+",
    #     default=[1024],
    #     help="List of input token lengths to test",
    # )
    # parser.add_argument(
    #     "--output-token-lengths",
    #     type=int,
    #     nargs="+",
    #     default=[64],
    #     help="List of output token lengths to test",
    # )
    parser.add_argument(
        "--prefill_bs",
        type=int,
        required=True,
        help="Prefill batch size used",
    )
    parser.add_argument(
        "--decode_bs",
        type=int,
        required=True,
        help="Decode batch size used",
    )

    # Parse arguments
    args = parser.parse_args()
    # generate_artifacts(args)
    run_benchmark(args)