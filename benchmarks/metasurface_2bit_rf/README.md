# metasurface_2bit_rf

Minimal benchmark for DL-assisted inverse design of a 2-bit metasurface tile.

Run from repo root:

1. `python -m benchmarks.metasurface_2bit_rf.dataset_make`
2. `python -m benchmarks.metasurface_2bit_rf.train_forward`
3. `python -m benchmarks.metasurface_2bit_rf.inverse_optimize`
4. `python -m benchmarks.metasurface_2bit_rf.validate`
5. `python -m benchmarks.metasurface_2bit_rf.export_geometry`
