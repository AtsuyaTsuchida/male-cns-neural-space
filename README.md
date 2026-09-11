# Male CNS — Learning & Neural Space

A minimal associative learning model and interactive 3D visualizations built from real connectivity and reconstructed neuronal skeletons in the male Drosophila `male-cns:v1.0` dataset.

## Explore the visualizations

```sh
python3 -m http.server 8000
```

Open http://localhost:8000/outputs/neural-space.html to rotate and zoom through 33 neuronal skeletons. Press **PLAY** to visualize changes synchronized with the learning results from all 664 modeled Kenyon cells. Three.js loads from a CDN, so the 3D viewer requires internet access.

- [3D Neural Space](outputs/neural-space.html)
- [Cell-level learning visualization](outputs/learning-interactive.html)
- [Model details, results, and limitations](outputs/README.md)

## Reproduce the experiment

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r outputs/requirements.txt
python outputs/run_learning.py
```

The extracted connectivity is included, so rerunning the experiment does not require downloading the approximately 1.1 GB source connectivity table. The visualizations contain embedded snapshots of the original results; they do not update automatically after rerunning the model.

## Recorded data and artistic interpretation

- **Learning model:** 664 KCg-m neurons connecting to the right MBON01 (body ID `10013`), representing 15,147 synapses.
- **3D view:** 32 selected KCs and MBON01, using 33 official SWC skeletons. Selection takes the 12 strongest connections among A-active cells, the 12 strongest among remaining B-active cells, and the eight strongest among inactive cells.
- Skeletons are simplified while retaining branch points and endpoints. Source coordinates use 8 nm voxels; the viewer centers and uniformly scales the geometry.
- Stimuli, plasticity, and value readout are modeling assumptions. Moving light particles are an artistic effect, not a simulation of spikes or signal propagation.
- This project does not establish that it reproduces learning or behavior in a real fly, or that this task requires the specific male-cns wiring.

## Data attribution

[Official MaleCNS data](https://male-cns.janelia.org/download/) — FlyEM/Janelia, Cambridge/MRC LMB, and Google Research. The data is distributed under CC-BY. This project extracts and reformats connectivity and simplifies neuronal skeletons for visualization. Source table hashes are recorded in `outputs/provenance.json`.

Skeleton source: `https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/{bodyId}.swc`

`visualizations/` contains editable inline fragments. `outputs/` contains the experiment code, extracted data, results, and standalone browser views. Temporary environments and large source downloads are excluded from Git.
