"""Cleanup duplicate pattern IDs."""
import sys, os, yaml, shutil
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scanner.utils.config import PATTERNS_DIR

patterns_dir = str(PATTERNS_DIR)
backup_dir = os.path.join(patterns_dir, '_dupes_backup')
os.makedirs(backup_dir, exist_ok=True)

# Files to DELETE (duplicates, keep originals)
to_delete = set([
    'P10_cross_function_reentrancy.yaml',
    'P11_read_only_reentrancy.yaml',
    'P12_cross_contract_reentrancy.yaml',
    'P13_erc721_callback_reentrancy.yaml',
    'P14_erc1155_batch_reentrancy.yaml',
    'P15_reentrancy_via_fallback.yaml',
    'P16_flash_loan_reentrancy_bridge.yaml',
    'P20_precision_loss_div_before_mul.yaml',
    'P21_rounding_wrong_party.yaml',
    'P22_fee_calculation_exploit.yaml',
    'P23_ownership_transfer_no_twostep.yaml',
    'P23_share_price_manipulation_eip4626.yaml',
    'P24_pausable_without_unpause_guard.yaml',
    'P30_metamorphic_contract.yaml',
    'P31_implementation_selfdestruct.yaml',
    'P32_constructor_in_implementation.yaml',
    'P33_function_clashing.yaml',
    'P34_uups_without_upgrade_guard.yaml',
])

# Delete them
for f in sorted(to_delete):
    fp = os.path.join(patterns_dir, f)
    if os.path.exists(fp):
        shutil.copy2(fp, os.path.join(backup_dir, f))
        os.remove(fp)
        print(f'  DEL {f}')

# Now verify
files = sorted(os.listdir(patterns_dir))
yaml_files = [f for f in files if f.endswith('.yaml') and not f.startswith('_')]
ids = []
fm = {}
for f in yaml_files:
    fp = os.path.join(patterns_dir, f)
    try:
        with open(fp) as fh:
            p = yaml.safe_load(fh)
        if p and 'id' in p:
            pid = p['id']
            ids.append(pid)
            fm.setdefault(pid, []).append(f)
    except: pass

dupes = {k:v for k,v in fm.items() if len(v)>1}
print(f'Remaining: {len(yaml_files)} files, {len(set(ids))} unique IDs, {len(dupes)} dupes')
for d in sorted(dupes):
    print(f'  {d}: {dupes[d]}')

if not dupes:
    print('ALL CLEAN!')
