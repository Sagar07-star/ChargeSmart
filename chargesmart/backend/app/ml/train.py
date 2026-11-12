"""Deterministic synthetic demonstration, not a real-world calibrated model."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error,mean_squared_error
from sklearn.model_selection import train_test_split
ROOT=Path(__file__).parent

def train():
    rng=np.random.default_rng(42);n=6000
    hour=rng.integers(0,24,n);day=rng.integers(0,7,n);ports=rng.integers(2,7,n);occupancy=rng.uniform(0,1,n)
    x=pd.DataFrame({'hour':hour,'day':day,'ports':ports,'occupancy':occupancy})
    y=np.maximum(0,occupancy*25+((hour>=17)&(hour<=21))*12+(day>=5)*4-ports*1.5+rng.normal(0,3,n))
    a,b,c,d=train_test_split(x,y,test_size=.2,random_state=42)
    model=RandomForestRegressor(n_estimators=80,max_depth=10,random_state=42,n_jobs=-1).fit(a,c)
    pred=model.predict(b);metrics={'mae_minutes':float(mean_absolute_error(d,pred)),'rmse_minutes':float(mean_squared_error(d,pred)**.5),'training_rows':len(a),'test_rows':len(b),'source':'synthetic held-out random split; not real-world validation','seed':42,'features':list(x.columns)}
    joblib.dump(model,ROOT/'wait_model.joblib');(ROOT/'metrics.json').write_text(json.dumps(metrics,indent=2));x.assign(wait_minutes=y).to_csv(ROOT/'synthetic_sessions.csv',index=False)
    print(json.dumps(metrics,indent=2));return metrics
if __name__=='__main__':train()
