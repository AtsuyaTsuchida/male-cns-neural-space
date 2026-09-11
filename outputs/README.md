# A Minimal Learning Experiment with male-cns

## Results

This simplified model learns an association between synthetic stimuli and reward, using real `male-cns:v1.0` connectivity to initialize its weights. It includes 664 KCg-m neurons connecting to the right MBON01 (body ID `10013`), representing 15,147 synapses. It is neither a whole-brain simulation nor a validation of learning in real flies.

Model probability of choosing A after 40 training blocks, averaged over 30 random seeds:

| Condition | Probability of choosing A |
|---|---:|
| Reward paired with A | 98.70% |
| Reward paired with B | 1.30% |
| No reward | 50.00% |
| Plasticity disabled | 50.00% |
| Equal reward for A and B | 50.02% |

These values depend on the imposed learning rate and readout gain. They are not measured fly accuracy. The small bias under equal reward results from double updates to shared active cells and differences in their relative connection weights across stimuli.

## Real data and assumptions

- **Real data:** official v1.0 annotations and KC-to-MBON partners and synapse counts, with a minimum confidence threshold of 0.5. The complete extracted KC-to-MBON table of 61,210 rows is included.
- The modeled connection was fixed to KCg-m → right MBON01 before evaluating learning. Cells were not selected by searching for good learning performance.
- Initial weights are synapse counts divided by their sum. This does not establish that synapse counts equal physiological connection strengths.
- A and B are random patterns, each directly activating approximately 10% of KCs, with overlap allowed. They do not represent measured odors, olfactory receptor responses, or projection neuron responses.
- Reward is an externally supplied scalar. Dopamine neuron dynamics, reward sensing, spikes, the body, and recurrent circuit feedback are not modeled.
- Reward reduces the weights of active KC connections. This does not reproduce compartment-specific dopamine effects throughout MBON01.
- An artificial readout converts output suppression into value relative to each stimulus's naive response. There is no claim that real flies perform this normalization.

## Computation

`w_i(0) = synapse_count_i / sum(synapse_count)`

`w_i(t+1) = w_i(t) * (1 - 0.08 * reward * x_i)`

`value(s) = 1 - sum_i[x_si*w_i(t)] / sum_i[x_si*w_i(0)]`

`P(A) = sigmoid(5 * (value(A)-value(B)))`

Each block presents A and B once. The experiment runs for 40 blocks across 30 seeds. Evaluation only reads the state and does not change weights. The equal-reward control supplies 0.5 reward for each stimulus, matching the total reward per block. The B-reward condition is an independent experiment trained with B from the start, not a reversal midway through learning.

This simple task can also be learned with other positive connection weights. The controls check the learning rule and reward dependence; they do not show that male-cns-specific wiring is necessary. Checks verify that no-reward and frozen-weight conditions remain at 50%, changing the rewarded stimulus reverses preference, weights remain nonnegative and no greater than their initial values, and connection pairs are unique. No comparison with measured behavior has been performed.

## Reproduction

Tested with Python 3.12. Dependencies are NumPy, pandas, and Matplotlib; PyArrow is needed only when extracting from the original data. With dependencies installed, the bundled extracted data supports offline reruns.

From this directory:

```sh
python -m pip install -r requirements.txt
python run_learning.py
```

Alternatively, from the repository root, run `python outputs/run_learning.py` using your configured Python environment.

- `learning.png`: learning curves; shading is ±1 standard deviation across seeds.
- `learning_results.csv`: results for every condition and seed.
- `learning_unit_edges.csv`: real connections used by the model.
- `kc_mbon_edges.csv.gz` / `neurons.csv`: all extracted KC-to-MBON connections and annotations.
- `provenance.json`: SHA-256 hashes and sizes of source files.
- `summary.json`: results and settings.

To repeat extraction, download `body-annotations-male-cns-v1.0-minconf-0.5.feather` and `connectome-weights-male-cns-v1.0-minconf-0.5.feather` from the official download page. Save them as `annotations.feather` and `weights.feather` in a working directory. Copy `run_learning.py` into a fresh output directory without the extracted files and run it with `--raw /path/to/working-directory`. The original connectivity table is approximately 1.1 GB.

## Sources

- [Official MaleCNS data](https://male-cns.janelia.org/download/): FlyEM/Janelia, Cambridge/MRC LMB, and Google Research. CC-BY. The bundled tables are extracted and reformatted KC-to-MBON data.
- [Hige et al., 2015, Coordinated and Compartmentalized Neuromodulation Shapes Sensory Processing in Drosophila](https://doi.org/10.1016/j.cell.2015.11.019): experimental background for compartmentalized plasticity. This implementation does not quantitatively reproduce the paper.
- [Learning with reinforcement prediction errors in a model of the Drosophila mushroom body](https://www.nature.com/articles/s41467-021-22592-4): background on models using KC-to-MBON plasticity. This implementation is not a reproduction of that model.
