
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from scipy.io import loadmat


# ============================================================
# PROJECT PATHS
# ============================================================

# backend/app/ai/dataset_reader.py
# parents[0] = ai
# parents[1] = app
# parents[2] = backend

BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_ROOT = (
    BASE_DIR
    / "data"
    / "raw"
    / "5. Battery Data Set"
)

MAX_FILES = 10


# ============================================================
# FIND MAT FILES
# ============================================================

def iter_mat_files(dataset_path: Path):
    """
    Find .mat files inside:
    - normal folders
    - ZIP files
    """

    for path in sorted(dataset_path.rglob("*")):

        if not path.is_file():
            continue

        # ----------------------------------------------------
        # Normal .mat file
        # ----------------------------------------------------

        if path.suffix.lower() == ".mat":

            yield (
                path.name,
                path.read_bytes()
            )

        # ----------------------------------------------------
        # .mat files inside ZIP
        # ----------------------------------------------------

        elif path.suffix.lower() == ".zip":

            with ZipFile(path) as archive:

                for member in sorted(
                    archive.namelist()
                ):

                    if member.lower().endswith(".mat"):

                        yield (
                            f"{path.name}!/{member}",
                            archive.read(member)
                        )


# ============================================================
# PRINT ARRAY SUMMARY
# ============================================================

def print_array_summary(
    name: str,
    value: object
) -> None:

    """
    Print information about a measurement array.
    """

    array = np.asarray(value)

    summary = (
        f"    {name}: "
        f"shape={array.shape}, "
        f"dtype={array.dtype}"
    )

    # --------------------------------------------------------
    # Numeric arrays
    # --------------------------------------------------------

    if (
        np.issubdtype(array.dtype, np.number)
        and array.size
    ):

        if np.iscomplexobj(array):

            values = np.abs(array)

        else:

            values = array

        finite_values = values[
            np.isfinite(values)
        ]

        if finite_values.size:

            if np.iscomplexobj(array):

                summary += (
                    f", magnitude_min="
                    f"{finite_values.min():.4g}, "
                    f"magnitude_max="
                    f"{finite_values.max():.4g}"
                )

            else:

                summary += (
                    f", min="
                    f"{finite_values.min():.4g}, "
                    f"max="
                    f"{finite_values.max():.4g}"
                )

    print(summary)


# ============================================================
# INSPECT DISCHARGE CYCLE
# ============================================================

def inspect_discharge_cycle(cycle) -> None:

    """
    Inspect measurement fields of one discharge cycle.
    """

    measurements = getattr(
        cycle,
        "data",
        None
    )

    # --------------------------------------------------------
    # No data field
    # --------------------------------------------------------

    if measurements is None:

        print(
            "\n  Discharge cycle "
            "has no data field."
        )

        return

    print(
        "\n  Discharge cycle fields:"
    )

    fields = getattr(
        measurements,
        "_fieldnames",
        None
    )

    # --------------------------------------------------------
    # Print measurement fields
    # --------------------------------------------------------

    if fields:

        for field in fields:

            value = getattr(
                measurements,
                field
            )

            print_array_summary(
                field,
                value
            )

    else:

        print(
            "    No measurement fields found."
        )


# ============================================================
# INSPECT ONE MAT FILE
# ============================================================

def inspect_mat_file(
    name: str,
    contents: bytes
) -> None:

    """
    Read and display the structure
    of one MATLAB .mat file.
    """

    print()
    print("=" * 70)
    print(f"FILE: {name}")
    print("=" * 70)

    # --------------------------------------------------------
    # Load MATLAB file
    # --------------------------------------------------------

    data = loadmat(
        BytesIO(contents),
        squeeze_me=True,
        struct_as_record=False
    )

    # --------------------------------------------------------
    # Remove MATLAB metadata variables
    # --------------------------------------------------------

    variables = [
        key
        for key in data
        if not key.startswith("__")
    ]

    print(
        "Variables:",
        ", ".join(variables)
        if variables
        else "(none)"
    )

    # ========================================================
    # PROCESS EACH VARIABLE
    # ========================================================

    for variable_name in variables:

        battery = data[variable_name]

        # ----------------------------------------------------
        # Get cycle field
        # ----------------------------------------------------

        cycle = getattr(
            battery,
            "cycle",
            None
        )

        if cycle is None:

            print(
                f"\n{variable_name}: "
                "no cycle field"
            )

            continue

        # ----------------------------------------------------
        # Convert cycle structure to array
        # ----------------------------------------------------

        cycles = np.atleast_1d(cycle)

        print(
            f"\n{variable_name}: "
            f"{len(cycles)} cycles"
        )

        # ----------------------------------------------------
        # Empty cycles
        # ----------------------------------------------------

        if len(cycles) == 0:
            continue

        # ====================================================
        # CYCLE TYPES
        # ====================================================

        cycle_types = []

        for current_cycle in cycles:

            cycle_type = getattr(
                current_cycle,
                "type",
                "unknown"
            )

            cycle_types.append(
                str(cycle_type)
            )

        print("\n  Cycle types:")

        for cycle_type in sorted(
            set(cycle_types)
        ):

            count = cycle_types.count(
                cycle_type
            )

            print(
                f"    {cycle_type}: {count}"
            )

        # ====================================================
        # FIRST DISCHARGE CYCLE
        # ====================================================

        discharge_cycles = [
            current_cycle
            for current_cycle in cycles
            if str(
                getattr(
                    current_cycle,
                    "type",
                    ""
                )
            ).lower() == "discharge"
        ]

        if discharge_cycles:

            first_discharge_cycle = (
                discharge_cycles[0]
            )

            print(
                "\n  First discharge cycle:"
            )

            inspect_discharge_cycle(
                first_discharge_cycle
            )

        else:

            print(
                "\n  No discharge cycle found."
            )

        # ====================================================
        # FIRST CYCLE
        # ====================================================

        first_cycle = cycles[0]

        measurements = getattr(
            first_cycle,
            "data",
            None
        )

        if measurements is None:

            print(
                "\n  First cycle has "
                "no data field."
            )

            continue

        fields = getattr(
            measurements,
            "_fieldnames",
            None
        )

        print(
            "\n  First-cycle measurements:"
        )

        # ----------------------------------------------------
        # Print fields
        # ----------------------------------------------------

        if fields:

            for field in fields:

                value = getattr(
                    measurements,
                    field
                )

                print_array_summary(
                    field,
                    value
                )

        else:

            print(
                "    No measurement "
                "fields found."
            )

        # ====================================================
        # AVAILABLE MEASUREMENT FIELDS
        # ====================================================

        print(
            "\n  Available measurement fields:"
        )

        if fields:

            for field in fields:

                print(
                    f"    - {field}"
                )

        else:

            print("    None")


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    dataset_path = DATASET_ROOT

    print("=" * 70)
    print("Battery Dataset Reader")
    print("=" * 70)

    print("\nDataset path:")
    print(dataset_path)

    # --------------------------------------------------------
    # Check dataset folder
    # --------------------------------------------------------

    if not dataset_path.is_dir():

        raise FileNotFoundError(
            f"\nDataset folder not found:\n"
            f"{dataset_path}\n\n"
            f"Expected structure:\n"
            f"backend/\n"
            f"  data/\n"
            f"    raw/\n"
            f"      5. Battery Data Set/\n"
        )

    print(
        "\nDataset folder found."
    )

    # --------------------------------------------------------
    # Find MAT files
    # --------------------------------------------------------

    mat_files = iter_mat_files(
        dataset_path
    )

    inspected = 0
    seen_files = set()

    # ========================================================
    # READ FILES
    # ========================================================

    for name, contents in mat_files:

        # ----------------------------------------------------
        # Stop after MAX_FILES
        # ----------------------------------------------------

        if inspected >= MAX_FILES:
            break

        # ----------------------------------------------------
        # Get actual .mat filename
        # ----------------------------------------------------

        battery_file = (
            name
            .rsplit("!/", 1)[-1]
            .casefold()
        )

        # ----------------------------------------------------
        # Skip duplicate files
        # ----------------------------------------------------

        if battery_file in seen_files:
            continue

        seen_files.add(
            battery_file
        )

        # ----------------------------------------------------
        # Inspect file
        # ----------------------------------------------------

        try:

            inspect_mat_file(
                name,
                contents
            )

            inspected += 1

        except Exception as error:

            print(
                f"\nERROR while reading "
                f"{name}:"
            )

            print(
                f"  {type(error).__name__}: "
                f"{error}"
            )

    # ========================================================
    # NO FILES FOUND
    # ========================================================

    if not inspected:

        raise FileNotFoundError(
            f"\nNo .mat files found in:\n"
            f"{dataset_path}\n\n"
            f"Check whether your .mat files "
            f"are directly inside the folder "
            f"or inside ZIP files."
        )

    # ========================================================
    # FINISHED
    # ========================================================

    print()
    print("=" * 70)
    print(
        f"Finished. Inspected "
        f"{inspected} file(s)."
    )
    print("=" * 70)


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
