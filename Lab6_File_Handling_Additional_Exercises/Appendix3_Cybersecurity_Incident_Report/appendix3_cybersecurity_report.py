import pandas as pd
import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime

# APPENDIX 3: CYBERSECURITY INCIDENT REPORT

SEED_DIGIT = 0
TARGET_YEAR = 2015 + SEED_DIGIT

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "Global_Cybersecurity_Threats_2015-2024.csv"
OUTPUT_DIR = BASE_DIR / "output"

YEAR_FIELD = "Year"
ATTACK_FIELD = "Attack Type"
LOSS_FIELD = "Financial Loss (in Million $)"


def calculate_sha256(file_path):
    digest = hashlib.sha256()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    print("=" * 55)
    print("CYBERSECURITY INCIDENT REPORT")
    print("=" * 55)
    print("Student Number: TUPM-26-1140")
    print("SEED_DIGIT:", SEED_DIGIT)
    print("Target Year:", TARGET_YEAR)

    # 1. Read CSV dataset
    if not DATA_FILE.exists():
        print("\nERROR: CSV dataset not found!")
        print("Expected location:", DATA_FILE)
        return

    try:
        data = pd.read_csv(DATA_FILE)
    except Exception as error:
        print("CSV reading error:", error)
        return

    data.columns = data.columns.astype(str).str.strip()

    required = [YEAR_FIELD, ATTACK_FIELD, LOSS_FIELD]
    missing = [col for col in required if col not in data.columns]

    if missing:
        print("Missing columns:", missing)
        print("Available columns:", list(data.columns))
        return

    total_records = len(data)

    # 2. Select incidents in target year
    data[YEAR_FIELD] = pd.to_numeric(
        data[YEAR_FIELD], errors="coerce"
    )
    data[LOSS_FIELD] = pd.to_numeric(
        data[LOSS_FIELD], errors="coerce"
    )

    selected = data[data[YEAR_FIELD] == TARGET_YEAR].copy()
    selected.insert(0, "Original Dataset Row", selected.index + 2)

    incident_count = len(selected)

    # 3. Count incidents per attack type
    attack_counts = (
        selected[ATTACK_FIELD]
        .fillna("Unknown")
        .astype(str)
        .value_counts()
        .to_dict()
    )

    # 4. Calculate financial loss
    total_loss = selected[LOSS_FIELD].sum()
    average_loss = (
        selected[LOSS_FIELD].mean()
        if incident_count > 0 else None
    )

    # 5. Find five costliest incidents
    ranked = selected.sort_values(
        by=LOSS_FIELD,
        ascending=False,
        kind="mergesort",
        na_position="last"
    )

    top_five = ranked[
        ranked[LOSS_FIELD].notna()
    ].head(5)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 6. Export filtered CSV
    csv_output = OUTPUT_DIR / f"filtered_incidents_{TARGET_YEAR}.csv"
    selected.to_csv(csv_output, index=False)

    # 7. Create JSON summary
    summary = {
        "student_number": "TUPM-26-1140",
        "seed_digit": SEED_DIGIT,
        "target_year": TARGET_YEAR,
        "total_records_in_dataset": total_records,
        "incidents_in_target_year": incident_count,
        "count_per_attack_type": {
            str(key): int(value)
            for key, value in attack_counts.items()
        },
        "total_financial_loss_usd_millions": round(
            float(total_loss), 2
        ),
        "average_financial_loss_usd_millions": (
            round(float(average_loss), 2)
            if pd.notna(average_loss) else None
        ),
        "five_costliest_incidents": json.loads(
            top_five.to_json(orient="records")
        ),
        "missing_financial_loss_values": int(
            selected[LOSS_FIELD].isna().sum()
        ),
        "generated_at": datetime.now().isoformat()
    }

    json_output = OUTPUT_DIR / f"incident_summary_{TARGET_YEAR}.json"

    with open(json_output, "w", encoding="utf-8") as file:
        json.dump(
            summary,
            file,
            indent=4,
            ensure_ascii=False,
            allow_nan=False
        )

    # 8. Create and verify JSON backup
    backup_output = OUTPUT_DIR / (
        f"incident_summary_{TARGET_YEAR}_backup.json"
    )

    shutil.copy2(json_output, backup_output)

    backup_verified = (
        calculate_sha256(json_output)
        == calculate_sha256(backup_output)
    )

    # 9. Verify CSV row count
    exported_data = pd.read_csv(csv_output)
    count_verified = len(exported_data) == incident_count

    # 10. Generate text report
    report_output = OUTPUT_DIR / f"incident_report_{TARGET_YEAR}.txt"

    lines = [
        "CYBERSECURITY INCIDENT REPORT",
        "=" * 55,
        f"Student Number: TUPM-26-1140",
        f"Target Year: {TARGET_YEAR}",
        "",
        "DATASET SUMMARY",
        "-" * 55,
        f"Total records in dataset: {total_records}",
        f"Incidents in target year: {incident_count}",
        "",
        "COUNT PER ATTACK TYPE",
        "-" * 55
    ]

    if attack_counts:
        for attack, count in attack_counts.items():
            lines.append(f"{attack}: {count}")
    else:
        lines.append("No incidents found.")

    lines.extend([
        "",
        "FINANCIAL LOSS (USD MILLIONS)",
        "-" * 55,
        f"Total financial loss: {total_loss:.2f}",
        (
            f"Average financial loss: {average_loss:.2f}"
            if pd.notna(average_loss)
            else "Average financial loss: N/A"
        ),
        "",
        "FIVE COSTLIEST INCIDENTS",
        "-" * 55
    ])

    if top_five.empty:
        lines.append("No incidents with valid financial loss.")
    else:
        for rank, (_, row) in enumerate(
            top_five.iterrows(), start=1
        ):
            lines.append(
                f"{rank}. Row {int(row['Original Dataset Row'])} | "
                f"{row[ATTACK_FIELD]} | "
                f"{row[LOSS_FIELD]:.2f} million USD"
            )

    lines.extend([
        "",
        "OUTPUT FILES AND VERIFICATION",
        "-" * 55,
        f"Filtered CSV: {csv_output.name}",
        f"JSON Summary: {json_output.name}",
        f"JSON Backup: {backup_output.name}",
        f"Text Report: {report_output.name}",
        f"CSV exported rows: {len(exported_data)}",
        f"Selected records: {incident_count}",
        f"CSV row-count verification: "
        f"{'PASSED' if count_verified else 'FAILED'}",
        f"JSON backup verification: "
        f"{'PASSED' if backup_verified else 'FAILED'}",
        f"Backup file size: {backup_output.stat().st_size} bytes",
        f"Backup SHA-256: {calculate_sha256(backup_output)}",
        "",
        "END OF REPORT"
    ])

    report_output.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    print("\n" + "\n".join(lines))
    print("\nProcessing completed!")


if __name__ == "__main__":
    main()