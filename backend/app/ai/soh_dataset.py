
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile

import numpy as np
from scipy.io import loadmat
import pandas as pd

# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_ROOT = (
    BASE_DIR
    / "data"
    / "raw"
    / "5. Battery Data Set"
)


# ---------------------------------------------------------
# BATTERIES TO USE FOR SOH DATASET
# ---------------------------------------------------------

TARGET_BATTERIES = {
    "B0005",
    "B0006",
    "B0007",
    "B0018",
}


# ---------------------------------------------------------
# FIND BATTERY FILE
# ---------------------------------------------------------

def find_battery_file(battery_id: str):

    for zip_path in DATASET_ROOT.rglob("*.zip"):

        with ZipFile(zip_path) as archive:

            for member in archive.namelist():

                if member.endswith(
                    f"{battery_id}.mat"
                ):

                    return archive.read(member)

    raise FileNotFoundError(
        f"{battery_id}.mat not found"
    )


# ---------------------------------------------------------
# EXTRACT DISCHARGE CAPACITY
# ---------------------------------------------------------

def extract_battery_data(
    battery_id: str,
    contents: bytes
):

    data = loadmat(
        BytesIO(contents),
        squeeze_me=True,
        struct_as_record=False
    )

    battery = data[battery_id]

    cycles = np.atleast_1d(
        battery.cycle
    )

    rows = []

    discharge_number = 0

    # -----------------------------------------------------
    # READ ALL DISCHARGE CYCLES
    # -----------------------------------------------------

    for cycle in cycles:

        cycle_type = str(
            getattr(
                cycle,
                "type",
                ""
            )
        ).lower()

        if cycle_type != "discharge":
            continue

        measurements = getattr(
            cycle,
            "data",
            None
        )

        if measurements is None:
            continue

        capacity = getattr(
            measurements,
            "Capacity",
            None
        )

        if capacity is None:
            continue

        capacity = float(
            np.asarray(
                capacity
            ).squeeze()
        )

        discharge_number += 1

        rows.append({
            "battery_id": battery_id,
            "cycle": discharge_number,
            "capacity_ah": capacity
        })

    return rows


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    all_rows = []

    # =====================================================
    # READ EACH BATTERY
    # =====================================================

    for battery_id in sorted(
        TARGET_BATTERIES
    ):

        print(
            f"\nReading {battery_id}..."
        )

        # -------------------------------------------------
        # Find battery file
        # -------------------------------------------------

        contents = find_battery_file(
            battery_id
        )

        # -------------------------------------------------
        # Extract discharge data
        # -------------------------------------------------

        rows = extract_battery_data(
            battery_id,
            contents
        )

        # -------------------------------------------------
        # Add rows to complete dataset
        # -------------------------------------------------

        all_rows.extend(rows)

        # -------------------------------------------------
        # Print battery information
        # -------------------------------------------------

        print(
            f"  Discharge cycles: "
            f"{len(rows)}"
        )

        if rows:

            print(
                f"  First capacity: "
                f"{rows[0]['capacity_ah']:.4f} Ah"
            )

            print(
                f"  Last capacity: "
                f"{rows[-1]['capacity_ah']:.4f} Ah"
            )

        # =================================================
        # CALCULATE SOH
        # =================================================

        if rows:

            # First discharge capacity is considered
            # the initial/reference capacity.
            initial_capacity = (
                rows[0]["capacity_ah"]
            )

            for row in rows:

                row["soh"] = round(
                    (
                        row["capacity_ah"]
                        / initial_capacity
                    ) * 100,
                    2
                )

    # =====================================================
    # DATASET SUMMARY
    # =====================================================

    print(
        "\n" + "=" * 60
    )

    print(
        f"Total discharge records: "
        f"{len(all_rows)}"
    )

    print(
        "=" * 60
    )

    # =====================================================
    # FIRST 10 SOH RECORDS
    # =====================================================

    print(
        "\nFirst 10 SOH records:"
    )

    for row in all_rows[:10]:

        print(row)

    # -----------------------------------------------------
    # SAVE SOH DATASET
    # -----------------------------------------------------

    output_dir = BASE_DIR / "data" / "processed"

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        output_dir
        / "soh_dataset.csv"
    )

    df = pd.DataFrame(all_rows)

    df.to_csv(
        output_file,
        index=False
    )

    print(
        f"\nSOH dataset saved to:"
    )

    print(output_file)

    print(
        f"Dataset shape: {df.shape}"
    )
    # =====================================================
    # FIRST 10 ORIGINAL RECORDS
    # =====================================================

    print(
        "\nFirst 10 records:"
    )

    for row in all_rows[:10]:

        print(row)


# ---------------------------------------------------------
# PROGRAM ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":
    main()

