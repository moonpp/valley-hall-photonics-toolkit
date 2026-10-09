# Scientific scope of v0.1.0

## Implemented

1. A homogeneous-cladding kinematic test: in the first longitudinal Brillouin zone, the smallest longitudinal diffraction momentum is |kx|. With continuous transverse momentum, a propagating cladding wave is possible iff n*f > |kx|. At equality the normal propagation component vanishes. Numerical threshold classification uses an explicit absolute tolerance.
2. A reference-frequency honeycomb classification, with |K|=2/3. It is a definition evaluated on supplied inputs, not a proof that those inputs describe an admitted exact bulk mode.
3. An independently implemented replay of selection and arithmetic for the archived design-B, delta=0.03a, Nr=16, kx=1/3, eight-phase supercell example.

## Not established

- That an open channel couples to a particular state or bounds its radiation rate.
- That a closed cladding channel guarantees a guided wall state or eliminates other loss channels.
- That the supplied frequency is rigorous, enclosed or experimentally measured.
- That scalar TE/localization selection is sufficient independent evidence of mode identity.
- That a finite supercell equals an isolated wall or that its vertical-radiation estimate supplies isolated-wall channel powers.
- That the underlying FEM baseline, isolated-wall Q or numerical convergence is validated.
- That this classification is novel relative to primary literature, or that publication in any journal is assured.

## Example conventions

Legume's stored positive f_im uses exp(+i omega t), so field amplitude decays at gamma_A = 2*pi*(c/a)*f_im; energy decays at twice that rate. Q = f_r/(2*f_im). This release does not convert complex vector fields between time conventions.

The two geometry walls coexist in a periodic cell. Phase spread is neither a confidence interval nor a complete uncertainty bound. The archived selection uses a computed gap and model-derived mode fractions. Replaying it preserves those dependencies; it does not certify them.

## Provenance

The source is the project's archived 2026-09-30 r9 package, relocated without changing data in the 2026-10-06 submission-preparation subset. The extraction verified the original SHA-256 entries for modes, geometry and sampling, retained all candidate modes' selection inputs, and omitted unrelated fields including unused NaN decay-length entries. Output JSON is standards-compliant. Source and curated hashes identify bytes, not physical truth.

No manuscript, personal correspondence, downloaded publisher content or full internal research history is included. Earlier research archives remain the detailed evidence record. Source calculations are attributed to the Claude-assisted project; this release's recomputation is independent only at the scalar selection and averaging level.
