"""Stock report: reads the catalogue export and prints the items that need to be reordered."""
import argparse
import csv
import json
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class Item:
    sku: str
    name: str
    category: str
    price: float
    stock: int

    @property
    def value(self):
        return self.price * self.stock


def load(path):
    """Read the JSON export and return the active items."""
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    return [Item(p["sku"], p["name"], p["category"], p["price"], p["stock"]) for p in data["products"] if p["active"]]


def by_category(items):
    totals = defaultdict(float)
    for item in items:
        totals[item.category] += item.value
    return dict(sorted(totals.items(), key=lambda pair: -pair[1]))


def to_reorder(items, threshold=50):
    return [item for item in items if item.stock < threshold]


def write_csv(items, path):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["SKU", "Name", "Stock"])
        for item in items:
            writer.writerow([item.sku, item.name, item.stock])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export")
    parser.add_argument("--threshold", type=int, default=50)
    parser.add_argument("--out", default="reorder.csv")
    args = parser.parse_args()
    items = load(args.export)
    print("Stock value by category:")
    for category, total in by_category(items).items():
        print("  %-10s %10.2f EUR" % (category, total))
    low = to_reorder(items, args.threshold)
    write_csv(low, args.out)
    print("%d of %d items below %d units, written to %s" % (len(low), len(items), args.threshold, args.out))


if __name__ == "__main__":
    main()
