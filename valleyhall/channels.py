"""Dimensionless kinematics for a straight, period-a wall."""
import math


def finite(value, name, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    if not math.isfinite(value) or (positive and value <= 0):
        raise ValueError(f"{name} must be finite" + (" and positive" if positive else ""))
    return float(value)


def channel_status(frequency, kx, index, *, tolerance=1e-12):
    """Test availability of at least one propagating cladding order.

    f=a/lambda_0; kx in 2*pi/a units; homogeneous isotropic cladding.
    Transverse momentum is continuous (isolated straight wall).
    An open channel does not establish coupling, radiation rate or mode existence.
    """
    f = finite(frequency, "frequency", True)
    k = finite(kx, "kx")
    n = finite(index, "index", True)
    tol = finite(tolerance, "tolerance")
    if tol < 0:
        raise ValueError("tolerance must be nonnegative")
    if abs(k) > 0.5:
        raise ValueError("kx must be in the first wall Brillouin zone [-0.5, 0.5]")
    radius = finite(n * f, "light-cone radius", True)
    margin = radius - abs(k)
    status = "threshold" if abs(margin) <= tol else ("open" if margin > 0 else "closed")
    return {"status": status, "margin": margin, "light_cone_radius": radius,
            "minimum_longitudinal_momentum": abs(k), "absolute_tolerance": tol}


def reference_regime(frequency, cladding_index, *, tolerance=1e-12):
    """Honeycomb reference-frequency classification with |K|=2/3.

    No finite-gap extension, frequency enclosure or theorem admission is inferred.
    """
    f = finite(frequency, "frequency", True)
    n = finite(cladding_index, "cladding_index", True)
    tol = finite(tolerance, "tolerance")
    if tol < 0:
        raise ValueError("tolerance must be nonnegative")
    rho = finite((2 / 3) / finite(n * f, "n*f", True), "rho", True)
    for edge in (1.0, 4 / 3, 2.0):
        if abs(rho - edge) <= tol:
            return {"rho": rho, "regime": "boundary", "boundary": edge}
    regime = "I" if rho > 2 else "II" if rho > 4 / 3 else "III" if rho > 1 else "IV"
    return {"rho": rho, "regime": regime}
