import os
import sys
import traceback
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

path = 'arcana_stage7_risk.ipynb'
output_path = 'arcana_stage7_risk_executed.ipynb'

try:
    print('Working dir:', os.getcwd())
    print('Using ARCANA_DATA_ROOT:', os.environ.get('ARCANA_DATA_ROOT'))
    nb = nbformat.read(path, as_version=4)
    proc = ExecutePreprocessor(timeout=600, kernel_name='python3')
    proc.preprocess(nb, {'metadata': {'path': os.getcwd()}})
    nbformat.write(nb, output_path)
    print('SUCCESS', output_path)
except Exception:
    traceback.print_exc()
    sys.exit(1)
