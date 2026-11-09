"""Audit saved ridge feature ladders on matched dates; no tuning or refitting."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from quantfin.io import atomic_json_dump, sha256_file

ROOT = Path(__file__).resolve().parents[1]


def audit(registry):
    rows=[]; sources={}
    for stage,key in [('Screening','SCREENING_RUN_ID'),('Confirmation','CONFIRMATION_RUN_ID'),('Replication','FINAL_RUN_ID')]:
        folder=ROOT/'artifacts/cross_market_ai_capability/runs'/registry['ids'][key]
        for name in ['configurations.json','predictions.parquet']:
            path=folder/name;sources[str(path.relative_to(ROOT))]=sha256_file(path)
        configurations=json.loads((folder/'configurations.json').read_text())
        configs=[c for c in configurations if c['family']=='ridge' and c['experiment']=='feature_progression']
        data=pd.read_parquet(folder/'predictions.parquet')
        baseline=data.loc[data.family.eq('asset_mean'),['decision_date','asset','prediction']].rename(columns={'prediction':'baseline'})
        expected=set(map(tuple,baseline[['decision_date','asset']].to_numpy()))
        for c in configs:
            q=data.loc[data.config_id.eq(c['config_id'])].merge(baseline,on=['decision_date','asset'],validate='one_to_one')
            if set(map(tuple,q[['decision_date','asset']].to_numpy())) != expected: raise ValueError('Unmatched ladder dates')
            q['quarter']=pd.to_datetime(q.decision_date).dt.to_period('Q').astype(str)
            for quarter,g in q.groupby('quarter'):
                mse=np.mean((g.target_oc_return-g.prediction)**2)
                bmse=np.mean((g.target_oc_return-g.baseline)**2)
                rows.append(dict(stage=stage,quarter=quarter,feature_set=c['feature_set'],config_id=c['config_id'],
                    alpha=c['parameters']['alpha'],sessions=g.decision_date.nunique(),observations=len(g),
                    mse=mse,baseline_mse=bmse,r2=1-mse/bmse,target_std=g.target_oc_return.std()))
    return pd.DataFrame(rows),sources


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--registry',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    frame,sources=audit(json.loads(Path(a.registry).read_text()));out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    frame.to_csv(out/'quarterly_feature_progression.csv',index=False)
    atomic_json_dump({'status':'complete','sources':sources,'script_sha256':sha256_file(Path(__file__)),
        'interpretation':'Same-date fixed-penalty ridge comparisons. Quarter variation is descriptive; volatility is shared across feature sets, and cannot alone explain within-quarter differences.',
        'files':{'quarterly_feature_progression.csv':sha256_file(out/'quarterly_feature_progression.csv')}},out/'manifest.json')
    print(frame.groupby('feature_set').agg(quarters=('quarter','count'),mean_r2=('r2','mean')).to_string())
