import os
import pandas as pd

BASE_DIR = os.getcwd()
FALLBACK_ROOT = r'C:\Arbion Research'
DATA_ROOT = os.environ.get('ARCANA_DATA_ROOT', None)

def resolve_stage_dir(name, sample_file=None):
    if DATA_ROOT:
        candidate = os.path.join(DATA_ROOT, name)
        if os.path.exists(candidate):
            return candidate
    local = os.path.join(BASE_DIR, name)
    if os.path.exists(local):
        return local
    fallback = os.path.join(FALLBACK_ROOT, name)
    if os.path.exists(fallback):
        return fallback
    if sample_file:
        for root, _, files in os.walk(BASE_DIR):
            if sample_file in files:
                return root
    return local

STAGE4A_DIR = resolve_stage_dir('Stage 4A stat arb engine', 'signals_gated_rolling.csv')
OUTPUT_DIR  = os.path.join(BASE_DIR, 'Stage 5 signal blending')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Read rolling signals — already regime-gated, elite pairs only
blended = pd.read_csv(
    os.path.join(STAGE4A_DIR, 'signals_gated_rolling.csv'),
    index_col=0, parse_dates=True)

blended.to_csv(os.path.join(OUTPUT_DIR, 'blended_signal.csv'))

print(f'✓ Stage 5 complete')
print(f'  Shape      : {blended.shape}')
print(f'  Date range : {blended.index[0].date()} to {blended.index[-1].date()}')
print(f'  Pairs      : {blended.shape[1]}')
print(f'  Pair names : {list(blended.columns)}')