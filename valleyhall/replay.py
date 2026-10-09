"""Recompute the archived eight-phase selection and rate-average estimate."""
import hashlib
import json
import math
from pathlib import Path
from .channels import finite

TARGETS = {"SS": 689.6353541677968, "LL": 419.08209346998086}


def load_checked(directory):
    directory = Path(directory)
    manifest = json.loads((directory / "SHA256SUMS.json").read_text(encoding="utf-8"))
    for name in ("modes.json", "geometry.json", "provenance.json"):
        digest = hashlib.sha256((directory / name).read_bytes()).hexdigest()
        if digest != manifest[name]:
            raise ValueError(f"Checksum mismatch: {name}")
    return json.loads((directory / "modes.json").read_text(encoding="utf-8"))


def replay(data):
    """Require exactly eight distinct prescribed phases and an admitted mode each.

    This is the archived selection rule, not independent mode-identity validation.
    Ties are rejected rather than silently selecting by input order.
    """
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported data schema")
    low, high = (finite(x, "gap edge", True) for x in data["gap"])
    if low >= high:
        raise ValueError("Gap edges must be increasing")
    samples = data["samples"]
    phases = [finite(s["s"], "phase") for s in samples]
    if sorted(phases) != [i / 8 for i in range(8)]:
        raise ValueError("Exactly the eight distinct archived phases are required")
    selected = {"SS": [], "LL": []}
    for sample in sorted(samples, key=lambda s: s["s"]):
        candidates = {"SS": [], "LL": []}
        identifiers = set()
        for mode in sample["modes"]:
            idx = mode["eigen_index"]
            if isinstance(idx, bool) or not isinstance(idx, int) or idx < 0 or idx in identifiers:
                raise ValueError("Mode indices must be unique nonnegative integers per phase")
            identifiers.add(idx)
            f = finite(mode["f"], "f", True)
            fim = finite(mode["f_im"], "f_im", True)
            te = finite(mode["te"], "TE fraction")
            weight = finite(mode["W_max"], "wall weight")
            if not 0 <= te <= 1 or not 0 <= weight <= 1 or mode["wall"] not in candidates:
                raise ValueError("Invalid mode fractions or wall label")
            if low < f < high and te >= 0.6 and weight >= 0.6:
                candidates[mode["wall"]].append(mode)
        for wall, modes in candidates.items():
            if not modes:
                raise ValueError(f"No admitted {wall} mode at phase {sample['s']}")
            modes.sort(key=lambda m: m["W_max"], reverse=True)
            if len(modes) > 1 and modes[0]["W_max"] == modes[1]["W_max"]:
                raise ValueError("Ambiguous tied wall weights")
            chosen = modes[0]
            selected[wall].append({"s": sample["s"], "eigen_index": chosen["eigen_index"],
                                   "f": chosen["f"], "f_im": chosen["f_im"],
                                   "Q_phase": chosen["f"] / (2 * chosen["f_im"])})
    result = {}
    for wall, modes in selected.items():
        fmean = math.fsum(m["f"] for m in modes) / 8
        imean = math.fsum(m["f_im"] for m in modes) / 8
        q = fmean / (2 * imean)
        result[wall] = {"Q_rate_average": q,
                        "relative_difference_from_archive": (q / TARGETS[wall]) - 1,
                        "retained_phases": len(modes), "selected_modes": modes}
    return result
