#!/usr/bin/env python3
"""Read-only evidence inspection for the recorded demonstration; no fitting/orders."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/'reports/releases/project2_team16_v2_2026-11-01/release_registry.json'


def inspect():
    r=json.loads(REGISTRY.read_text());ids=r['ids'];rows=[]
    for stage,key,base in [('2025','FINAL_RUN_ID','cross_market_ai_capability'),('2026 Jan–Sep','FORWARD_RUN_ID','cross_market_ai_capability_2026')]:
        folder=ROOT/'artifacts'/base/'runs'/ids[key];m=json.loads((folder/'manifest.json').read_text())
        assert m['status']=='complete'
        ledger=pd.read_parquet(folder/'strategy_ledgers.parquet')
        if 'config_id' in ledger:ledger=ledger.loc[ledger.config_id.eq(ids['SELECTED_CONFIG_ID'])]
        assert len(ledger)>0 and not ledger.decision_date.duplicated().any()
        assert np.isfinite(ledger[['gross_return','trading_cost','net_return']]).all().all()
        assert np.allclose(ledger.gross_return-ledger.trading_cost,ledger.net_return,atol=1e-12)
        assert np.allclose(ledger.turnover,2*ledger.gross_exposure,atol=1e-12)
        assert np.allclose(ledger.trading_cost,ledger.turnover*.00075,atol=1e-10)
        assert ledger.gross_exposure.between(0,1+1e-10).all()
        diagnostics=pd.read_csv(folder/'refit_diagnostics.csv')
        if 'config_id' in diagnostics:diagnostics=diagnostics.loc[diagnostics.config_id.eq(ids['SELECTED_CONFIG_ID'])]
        assert (pd.to_datetime(diagnostics.training_end)<pd.to_datetime(diagnostics.block_start)).all()
        for name in ['strategy_ledgers.parquet','refit_diagnostics.csv']:
            expected=m.get('files',{}).get(name)
            if expected:assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==expected
        active=ledger.loc[ledger.gross_exposure.gt(0)]
        sample=active[['decision_date','expected_gross_return','expected_net_return','holdings','gross_return','trading_cost','net_return']].head(2)
        print('\n'+stage+' — RECORDED HISTORICAL RUN, NOT A NEW FIT')
        print('run:',ids[key]);print('sessions:',len(ledger));print('net period return:',f'{((1+ledger.net_return).prod()-1)*100:.2f}%')
        print('Past-only refit dates and ledger arithmetic: PASS')
        print(sample.to_string(index=False))
        rows.append({'stage':stage,'sessions':len(ledger),'status':'pass'})
    return rows


if __name__=='__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    print(json.dumps({'checks':inspect(),'status':'pass','training_performed':False},indent=2))
