# Valley-Hall Photonics Toolkit

Small, dependency-free Python tools for checking radiation-channel accessibility and replaying an archived valley-Hall photonics calculation.

**Research preview v0.1.0.** This is not a Maxwell solver or a validated device-design tool. It does not establish a new scientific priority claim. A physically validated radiative quality factor is not available from this project yet.

## What you can do

- Check whether a homogeneous cladding permits a propagating radiation order for a straight periodic wall.
- Classify a supplied reference frequency using the honeycomb convention below.
- Reproduce the selection and averaging behind one archived design-B table row, with all eight phases and candidate modes retained.

## Quick start

Install Python 3.10 or newer, download or clone this repository, then open a terminal in its folder. No Python packages need installing to run from the checkout.

```sh
python -m valleyhall screen --frequency 0.4535443863565483 --kx 0.3333333333333333 --upper-index 1.0 --lower-index 1.428
python -m valleyhall replay examples/design_b
python -m unittest discover -s tests -v
```

The first command reports **open** channels in both claddings. This means radiation is kinematically permitted, not that a state exists, must radiate, or has a particular loss. A bound state in the continuum can remain non-radiating despite open channels.

The second command reconstructs these archived estimates (floating-point last digits may differ):

| Wall | Eight-phase rate-average estimate |
| --- | ---: |
| SS | 689.6353541677968 |
| LL | 419.08209346998086 |

Here SS and LL denote the small-hole and large-hole wall terminations in the accompanying geometry. These are supercell estimates of vertical-radiation Q, **not validated isolated-wall total Q**. Reproducing the numbers does not validate their physical accuracy.

## Units and scope

Frequency is `f = a/lambda_0`. Longitudinal wavevector is in units of `2*pi/a`, within the first wall Brillouin zone `[-0.5, 0.5]`. The wall period is `a`. Indices are positive real scalar indices for lossless, isotropic homogeneous claddings.

For an isolated straight wall, transverse momentum is continuous. At least one propagating cladding order is available when `n*f > abs(kx)`. A positive margin is open; a negative margin is closed. The default absolute numerical tolerance is `1e-12` in these dimensionless momentum units. Values within that tolerance are labelled **threshold**, meaning grazing or numerically too close to distinguish; they are not certified equalities. There is no physical uncertainty model behind this tolerance.

For a periodic transverse supercell the transverse momentum is discrete. The isolated-wall test must not be read as a count of that supercell's open channels.

The optional reference-frequency classification uses `rho = (2/3)/(n_c*f)`, `n_c = max(n_upper,n_lower)`, and honeycomb `|K|=2/3` in `2*pi/a` units:

| Reference regime | Interval |
| --- | --- |
| I | rho > 2 |
| II | 4/3 < rho < 2 |
| III | 1 < rho < 4/3 |
| IV | rho < 1 |

Thresholds are returned separately. These labels concern the **input reference frequency only**. They do not classify an entire finite gap, prove an exact eigenfrequency, certify a theorem's hypotheses, or establish mode existence. The illustrative frequency above is an archived wall-mode frequency, not an independently established bulk Dirac frequency.

## Reproducibility and limitations

The replay selects modes strictly between the stored gap edges, with TE fraction and wall weight each at least 0.6, choosing the largest wall weight at each phase. It then computes `mean(f)/(2*mean(f_im))`. It does not average per-phase Q. Missing phases, empty selections, ties, non-finite values and corrupted example files fail explicitly.

`examples/design_b/provenance.json` records the source hashes, extraction and original settings. This release includes scalar candidate data and the 128-hole geometry. It does **not** include the original field/eigenvector or coupling arrays and does not independently recompute mode identity, radiation couplings or eigenfrequencies. It is a replay of one archived row, not reproduction of the complete manuscript or a fresh simulation.

Truncation, supercell size, mode mixing, averaging and group velocity can affect reported estimates. This release establishes no convergence certificate, error bar, physical Q validation or comparison with experiment. The paper remains under review and development. See [scientific scope](docs/SCIENTIFIC_SCOPE.md).

## Development

Tests cover analytic channel cases and boundaries, invalid input, synthetic averaging cases, failure controls, checksum corruption, and the archived numerical targets. GitHub Actions runs the same tests. Test success concerns software behavior and archived arithmetic, not the physical adequacy of the model.

Project lead: Nouh Al Busaidi. Claude assisted with source calculations; Codex assisted with this implementation and verification. This release does not imply university endorsement or completed expert review.

No reuse license has been selected yet. Public availability should not be described as an open-source license grant. Licensing and formal citation metadata can be added after the author selects them.
