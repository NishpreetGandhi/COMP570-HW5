import argparse
import csv
import sys
from collections import Counter
from datetime import datetime

def parse_date(value):
    for fmt in ("%m/%d/%Y %I:%M:%S %p", "%m/%d/%Y %H:%M:%S"):
        try:
            return datetime.strptime((value or "").strip(), fmt)
        except ValueError:
            pass
    return None

def main():
    parser = argparse.ArgumentParser(
        description="Count 311 complaint types by borough within a creation-date range."
    )
    parser.add_argument("-i", required=True, help="Input CSV file")
    parser.add_argument("-s", required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("-e", required=True, help="End date YYYY-MM-DD, inclusive")
    parser.add_argument("-o", help="Output CSV file; defaults to stdout")
    args = parser.parse_args()

    start = datetime.strptime(args.s, "%Y-%m-%d").date()
    end = datetime.strptime(args.e, "%Y-%m-%d").date()
    if end < start:
        parser.error("end date must not precede start date")

    counts = Counter()
    with open(args.i, newline="", encoding="utf-8-sig", errors="replace") as f:
        for row in csv.DictReader(f):
            date = parse_date(row.get("Created Date"))
            if date is None or not (start <= date.date() <= end):
                continue
            borough = (row.get("Borough") or "").strip()
            complaint = (row.get("Complaint Type") or "").strip()
            if borough and complaint:
                counts[(complaint, borough)] += 1

    output = open(args.o, "w", newline="", encoding="utf-8") if args.o else sys.stdout
    try:
        writer = csv.writer(output)
        writer.writerow(["complaint type", "borough", "count"])
        for (complaint, borough), count in sorted(counts.items()):
            writer.writerow([complaint, borough, count])
    finally:
        if args.o:
            output.close()

if __name__ == "__main__":
    main()
