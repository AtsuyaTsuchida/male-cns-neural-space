"""Real male-cns v1.0 edges + explicitly synthetic stimuli and plasticity.
Run: python run_learning.py --raw ../work
After extraction, raw files are not needed for reruns.
"""
from pathlib import Path
import argparse, json, hashlib
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent

def extract(raw):
    import pyarrow as pa
    import pyarrow.ipc as ipc
    import pyarrow.compute as pc
    ann = pd.read_feather(raw / 'annotations.feather')
    kcs = ann[ann['class'].eq('Kenyon_Cell')]
    mbons = ann[ann['class'].eq('MBON')]
    reader = ipc.open_file(pa.memory_map(str(raw / 'weights.feather')))
    rows = []
    for i in range(reader.num_record_batches):
        batch = reader.get_batch(i)
        mask = pc.and_(pc.is_in(batch['body_pre'], value_set=pa.array(kcs.bodyId)),
                       pc.is_in(batch['body_post'], value_set=pa.array(mbons.bodyId)))
        selected = batch.filter(mask)
        if selected.num_rows:
            rows.append(selected.to_pandas())
    edges = pd.concat(rows, ignore_index=True)
    edges.to_csv(OUT / 'kc_mbon_edges.csv.gz', index=False)
    ann[ann.bodyId.isin(set(edges.body_pre) | set(edges.body_post))][
        ['bodyId', 'type', 'instance', 'class', 'somaSide']
    ].to_csv(OUT / 'neurons.csv', index=False)
    manifest = {'dataset': 'male-cns:v1.0', 'confidence_threshold': 0.5,
                'source': 'https://male-cns.janelia.org/download/',
                'license': 'CC-BY; FlyEM/Janelia, Cambridge/MRC LMB and Google Research',
                'files': {}}
    for filename in ['annotations.feather', 'weights.feather']:
        h = hashlib.sha256()
        with open(raw / filename, 'rb') as f:
            for block in iter(lambda: f.read(8*1024*1024), b''):
                h.update(block)
        manifest['files'][filename] = {'sha256': h.hexdigest(), 'bytes': (raw/filename).stat().st_size}
    (OUT/'provenance.json').write_text(json.dumps(manifest, indent=2))

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw', type=Path, default=OUT.parent/'work')
    args = parser.parse_args()
    if not (OUT/'kc_mbon_edges.csv.gz').exists():
        extract(args.raw)
    edges = pd.read_csv(OUT/'kc_mbon_edges.csv.gz')
    ann = pd.read_csv(OUT/'neurons.csv')
    # Predeclared cell type and side, not selected by learning performance.
    target = ann[ann.type.eq('MBON01') & ann.somaSide.eq('R')].sort_values('bodyId').iloc[0]
    kcs = ann[ann.type.eq('KCg-m')]
    unit = edges[edges.body_post.eq(target.bodyId) & edges.body_pre.isin(kcs.bodyId)].sort_values('body_pre')
    assert len(unit) >= 20 and (unit.weight > 0).all()
    assert not unit.duplicated(['body_pre','body_post']).any()
    unit.to_csv(OUT/'learning_unit_edges.csv', index=False)
    base = unit.weight.to_numpy(float)
    base /= base.sum()
    records = []
    # No odor receptor, PN or dopamine-neuron dynamics are simulated.
    # Each synthetic stimulus directly recruits 10% of recorded KCs.
    for seed in range(30):
        rng = np.random.default_rng(seed)
        x = np.zeros((2,len(base)))
        for row in x:
            row[rng.choice(len(base), max(2,round(.1*len(base))),replace=False)] = 1
        naive = x @ base
        for condition in ['reward_A','reward_B','no_reward','frozen','nonselective_reward']:
            w = base.copy()
            for trial in range(41):
                # Abstract value readout: normalized reduction from naive MBON response.
                value = 1 - (x @ w)/naive
                pA = 1/(1+np.exp(-5*(value[0]-value[1])))
                records.append([seed,condition,trial,float(pA),*value])
                if trial == 40:
                    break
                eta = 0 if condition == 'frozen' else .08
                for odor in range(2):
                    reward = (condition in ['reward_A','frozen'] and odor==0) or (condition=='reward_B' and odor==1)
                    if condition == 'nonselective_reward':
                        reward = .5  # Same total reward per block, independent of identity.
                    w *= 1 - eta*float(reward)*x[odor]
                assert np.all(w >= 0) and np.all(w <= base+1e-12)
    data = pd.DataFrame(records,columns=['seed','condition','training_blocks','p_choose_A','value_A','value_B'])
    data.to_csv(OUT/'learning_results.csv',index=False)
    end = data[data.training_blocks.eq(40)].groupby('condition').p_choose_A.agg(['mean','std','min','max'])
    assert np.allclose(data[data.condition.isin(['no_reward','frozen'])].p_choose_A,.5)
    assert end.loc['reward_A','min'] > .5 and end.loc['reward_B','max'] < .5
    # Equal reward need not yield exact equality: overlapping KCs receive two
    # updates, and their anatomical weight fractions differ between stimuli.
    summary = {'target': {'bodyId': int(target.bodyId), 'type':target.type,'instance':target.instance},
               'unit_KCs':len(unit),'unit_synapses':int(unit.weight.sum()),
               'all_KC_MBON_edges':len(edges),'seeds':30,'blocks':40,
               'eta':.08,'softmax_gain':5,'KC_active_fraction':.1,
               'final_p_choose_A':json.loads(end.to_json(orient='index')),
               'checks':'frozen/no-reward stay at 0.5; reward-label swap reverses preference; weights bounded; nonselective bias reported, not assumed zero',
               'interpretation':'Model probabilities, not measured fly behavior. Synthetic KC inputs and imposed LTD/readout.'}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9,5.2),layout='constrained')
    labels={'reward_A':'A paired with reward','reward_B':'B paired with reward',
            'no_reward':'No reward','frozen':'Plasticity disabled','nonselective_reward':'Reward independent of stimulus'}
    for cond,color,style in zip(labels,['#007f75','#b54b32','#777777','#777777','#a79554'],['-','-','--',':','-.']):
        q=data[data.condition.eq(cond)].groupby('training_blocks').p_choose_A
        mean=q.mean(); sd=q.std()
        ax.plot(mean.index,mean,label=labels[cond],color=color,ls=style,lw=2)
        if cond in ['reward_A','reward_B']:
            ax.fill_between(mean.index,mean-sd,mean+sd,color=color,alpha=.16)
    ax.set(xlabel='Training blocks (A and B presented once each)',ylabel='Model probability of choosing A',ylim=(0,1),
           title='Learning on real male-cns KC → MBON01 connections')
    ax.legend(loc='center right',fontsize=8);ax.spines[['top','right']].set_visible(False)
    fig.supxlabel('Synthetic stimuli + imposed plasticity/readout • 30 seeds • band: ±1 SD',fontsize=9)
    fig.savefig(OUT/'learning.png',dpi=180)
    print(json.dumps(summary,indent=2))

if __name__ == '__main__':
    run()
