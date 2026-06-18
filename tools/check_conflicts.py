"""Check pattern conflicts"""
import yaml, os, sys
from collections import Counter

patterns_dir = 'scanner/patterns'
files = sorted(os.listdir(patterns_dir))
yaml_files = [f for f in files if f.endswith('.yaml')]

ids = []
file_map = {}
for f in yaml_files:
    try:
        p = yaml.safe_load(open(os.path.join(patterns_dir, f)))
        if p and 'id' in p:
            pid = p['id']
            ids.append(pid)
            if pid not in file_map:
                file_map[pid] = []
            file_map[pid].append(f)
    except Exception as e:
        print(f'Error loading {f}: {e}')

dupes = {k: v for k, v in Counter(ids).items() if v > 1}
print(f'Total YAML files: {len(yaml_files)}')
print(f'Unique IDs: {len(set(ids))}')
print(f'Duplicate IDs: {len(dupes)}')
for d in sorted(dupes.keys()):
    print(f'  {d}: {file_map[d]}')
