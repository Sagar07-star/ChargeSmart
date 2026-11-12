from pathlib import Path
from functools import lru_cache
import json
import joblib
import pandas as pd
ROOT=Path(__file__).parent
@lru_cache
def model():
    return joblib.load(ROOT/'wait_model.joblib') if (ROOT/'wait_model.joblib').exists() else None

def predict(hour,day,ports,occupancy):
    m=model()
    value=float(m.predict(pd.DataFrame([{'hour':hour,'day':day,'ports':ports,'occupancy':occupancy}]))[0]) if m else max(0,occupancy*25+(12 if 17<=hour<=21 else 0)-ports*1.5)
    return {'minutes':round(value,1),'source':'Simulated prediction · synthetic-trained Random Forest' if m else 'Demo estimate · rules','metrics':json.loads((ROOT/'metrics.json').read_text()) if m else None}
