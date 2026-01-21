import csv
import os
from datetime import datetime

from prettytable import PrettyTable


def compare_plate_results(results_dir="results", correct_results_file="result_correct.csv"):
    def short_name(p: str) -> str:
        # Nice column names: filename without extension, uppercase
        base = os.path.basename(p)
        name, _ = os.path.splitext(base)
        return name.upper()

    # --- Load correct answers ---
    correct_path = os.path.join(results_dir, correct_results_file)
    if not os.path.exists(correct_path):
        raise FileNotFoundError(f"Correct results file not found: {correct_path}")

    correct_plates: dict[str, str] = {}
    with open(correct_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "PATH" not in reader.fieldnames or "RESULT" not in reader.fieldnames:
            raise ValueError(f"{correct_results_file} must have header PATH,RESULT")

        for row in reader:
            p = row.get("PATH", "")
            r = (row.get("RESULT") or "").strip()
            if p:
                correct_plates[p] = r

    # Determine which images to display (stable order)
    image_paths = list(correct_plates.keys())
    image_cols = [short_name(p) for p in image_paths]

    # --- Scan prediction CSVs ---
    prediction_files = []
    for filename in os.listdir(results_dir):
        if not filename.endswith(".csv"):
            continue
        if filename == correct_results_file or filename.startswith("result_correct"):
            continue
        # Expect: result_<MODEL>_<YYYYMMDD-HHMMSS>.csv
        if filename.startswith("result_"):
            prediction_files.append(filename)

    # Sort by timestamp if present; otherwise by filename
    def parse_file_info(fname: str):
        name_no_ext = os.path.splitext(fname)[0]  # result_model_yyyymmdd-hhmmss
        parts = name_no_ext.split("_")
        model = "UNKNOWN"
        ts = None
        if len(parts) >= 3 and parts[0] == "result":
            model = "_".join(parts[1:-1])  # supports model names that contain underscores
            ts_raw = parts[-1]
            try:
                ts = datetime.strptime(ts_raw, "%Y%m%d-%H%M%S")
            except ValueError:
                ts = None
        return model, ts

    prediction_files.sort(key=lambda fn: (parse_file_info(fn)[1] or datetime.min, fn))

    # --- Build table ---
    table = PrettyTable()
    table.field_names = ["Model", "Timestamp", "Accuracy"] + image_cols

    for filename in prediction_files:
        model, ts = parse_file_info(filename)
        ts_str = ts.strftime("%Y-%m-%d %H:%M:%S") if ts else "N/A"

        file_path = os.path.join(results_dir, filename)
        preds: dict[str, str] = {}

        with open(file_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # Be tolerant if someone wrote without headers (but your code writes headers)
            if reader.fieldnames and "PATH" in reader.fieldnames and "RESULT" in reader.fieldnames:
                for row in reader:
                    p = row.get("PATH", "")
                    r = (row.get("RESULT") or "").strip()
                    if p:
                        preds[p] = r
            else:
                # fallback: naive 2-column csv
                f.seek(0)
                raw = csv.reader(f)
                for row in raw:
                    if len(row) == 2 and row[0] != "PATH":
                        preds[row[0]] = (row[1] or "").strip()

        # Compare
        checks = []
        correct_count = 0
        total_count = 0

        for p in image_paths:
            correct = correct_plates.get(p)
            pred = preds.get(p)

            if pred is None or pred == "":
                checks.append("N/A")
                continue

            total_count += 1
            if pred == correct:
                correct_count += 1
                checks.append("✅")
            else:
                checks.append("❌")

        acc = f"{correct_count}/{total_count}" if total_count else "0/0"
        table.add_row([model, ts_str, acc] + checks)

    print(table)
