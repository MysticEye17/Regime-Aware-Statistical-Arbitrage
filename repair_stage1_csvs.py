from pathlib import Path
from io import StringIO
import pandas as pd

OUTPUT_DIR = Path(r'C:\Arbion Research\Stage 1 data layer\Universe_stock data')


def needs_repair(path: Path) -> bool:
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines()
    if len(lines) < 2:
        return False
    return lines[1].startswith(',')


def repair_file(path: Path) -> bool:
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines()
    if len(lines) < 2 or not lines[1].startswith(','):
        return False

    repaired_lines = [lines[0]] + lines[2:]
    repaired_text = '\n'.join(repaired_lines)
    if text.endswith('\n'):
        repaired_text += '\n'

    df = pd.read_csv(StringIO(repaired_text), parse_dates=['Date'])
    if df['Date'].isna().any():
        raise ValueError(f'Bad dates remain in {path}')

    df = df.sort_values('Date').reset_index(drop=True)
    df.to_csv(path, index=False)
    return True


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    repaired = []
    for csv_path in sorted(OUTPUT_DIR.glob('*.csv')):
        try:
            if repair_file(csv_path):
                repaired.append(csv_path.name)
                print(f'Repaired {csv_path.name}')
        except Exception as exc:
            print(f'FAILED {csv_path.name}: {exc}')

    if repaired:
        print(f'Completed repairs for {len(repaired)} files.')
    else:
        print('No files required repair.')


if __name__ == '__main__':
    main()
