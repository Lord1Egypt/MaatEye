#!/usr/bin/env python3
"""Clean up duplicate pattern IDs in MaatEye"""
import yaml, os, shutil

patterns_dir = os.path.join(os.path.dirname(__file__), '..', 'scanner', 'patterns')
patterns_dir = os.path.abspath(patterns_dir)
backup_dir = os.path.join(patterns_dir, '_dupes_backup')
os.makedirs(backup_dir, exist_ok=True)

# Which files to DELETE (the duplicates, keep originals)
to_delete = [
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
    'P40_contract_existence_check_missing.yaml',
    'P40_uups_no_upgrade_guard.yaml',
    'P41_gas_stipend_dependency.yaml',
    'P42_gas_stipend_dependency.yaml',
    'P42_delegatecall_untrusted_library.yaml',
    'P43_delegatecall_untrusted.yaml',
    'P43_staticcall_with_side_effects.yaml',
    'P44_create2_address_collision.yaml',
    'P44_staticcall_side_effects.yaml',
]

# Files to KEEP and their new IDs (rename)
# Format: (old_filename, new_id, new_filename)
to_rename = [
    ('P10_cross_function_reentrancy.yaml', 'P81', 'P81_cross_function_reentrancy.yaml'),
    ('P11_read_only_reentrancy.yaml', 'P82', 'P82_read_only_reentrancy.yaml'),
    ('P12_cross_contract_reentrancy.yaml', 'P83', 'P83_cross_contract_reentrancy.yaml'),
    ('P13_erc721_callback_reentrancy.yaml', 'P84', 'P84_erc721_callback_reentrancy.yaml'),
    ('P14_erc1155_batch_reentrancy.yaml', 'P85', 'P85_erc1155_batch_reentrancy.yaml'),
    ('P15_reentrancy_via_fallback.yaml', 'P86', 'P86_reentrancy_via_fallback.yaml'),
    ('P16_flash_loan_reentrancy_bridge.yaml', 'P87', 'P87_flash_loan_bridge_reentrancy.yaml'),
    ('P20_precision_loss_div_before_mul.yaml', 'P88', 'P88_precision_loss_div_before_mul.yaml'),
    ('P21_rounding_wrong_party.yaml', 'P89', 'P89_rounding_wrong_party.yaml'),
    ('P22_fee_calculation_exploit.yaml', 'P90', 'P90_fee_calculation_exploit.yaml'),
    ('P23_share_price_manipulation_eip4626.yaml', 'P91', 'P91_share_price_manipulation_eip4626.yaml'),
    ('P23_ownership_transfer_no_twostep.yaml', 'P92', 'P92_ownership_transfer_no_twostep.yaml'),
    ('P24_pausable_without_unpause_guard.yaml', 'P93', 'P93_pausable_without_unpause_guard.yaml'),
    ('P30_metamorphic_contract.yaml', 'P94', 'P94_metamorphic_contract.yaml'),
    ('P31_implementation_selfdestruct.yaml', 'P95', 'P95_implementation_selfdestruct.yaml'),
    ('P32_constructor_in_implementation.yaml', 'P96', 'P96_constructor_in_implementation.yaml'),
    ('P33_function_clashing.yaml', 'P97', 'P97_function_clashing.yaml'),
    ('P34_uups_without_upgrade_guard.yaml', 'P98', 'P98_uups_without_upgrade_guard.yaml'),
    ('P40_contract_existence_check_missing.yaml', 'P99', 'P99_contract_existence_check_missing.yaml'),
    ('P40_uups_no_upgrade_guard.yaml', 'P100', 'P100_uups_no_upgrade_guard.yaml'),
    ('P41_gas_stipend_dependency.yaml', 'P101', 'P101_gas_stipend_dependency.yaml'),
    ('P42_delegatecall_untrusted_library.yaml', 'P102', 'P102_delegatecall_untrusted_library.yaml'),
    ('P42_gas_stipend_dependency.yaml', 'P103', 'P103_gas_stipend.yaml'),
    ('P43_delegatecall_untrusted.yaml', 'P104', 'P104_delegatecall_untrusted.yaml'),
    ('P43_staticcall_with_side_effects.yaml', 'P105', 'P105_staticcall_side_effects.yaml'),
    ('P44_create2_address_collision.yaml', 'P106', 'P106_create2_collision.yaml'),
    ('P44_staticcall_side_effects.yaml', 'P107', 'P107_staticcall_side_effects.yaml'),
]

# KEEP these original files as-is
originals_to_keep = [
    'P01_unprotected_mint.yaml',
    'P02_selfdestruct_anyone.yaml',
    'P03_reentrancy.yaml',
    'P04_integer_overflow.yaml',
    'P05_tx_origin_auth.yaml',
    'P06_unchecked_call.yaml',
    'P07_delegatecall_injection.yaml',
    'P08_storage_collision.yaml',
    'P09_no_input_validation.yaml',
    'P10_oracle_manipulation.yaml',
    'P11_flash_loan_vector.yaml',
    'P12_signature_replay.yaml',
    'P13_governance_attack.yaml',
    'P14_unsafe_ownership_renounce.yaml',
    'P15_incorrect_visibility.yaml',
    'P16_uninitialized_proxy.yaml',
    'P17_arbitrary_external_call.yaml',
    'P18_missing_access_control.yaml',
    'P19_no_safe_erc20.yaml',
    'P20_timestamp_dependence.yaml',
    'P21_unprotected_initializer.yaml',
    'P22_role_admin_hijack.yaml',
    'P23_ownership_no_twostep.yaml',
    'P24_pausable_no_unpause.yaml',
    'P25_cross_function_reentrancy.yaml',
    'P26_read_only_reentrancy.yaml',
    'P27_cross_contract_reentrancy.yaml',
    'P28_erc721_callback_reentrancy.yaml',
    'P29_erc1155_batch_reentrancy.yaml',
    'P30_fallback_reentrancy.yaml',
    'P31_flash_loan_bridge_reentrancy.yaml',
    'P32_precision_loss.yaml',
    'P33_rounding_wrong_party.yaml',
    'P34_fee_calculation_exploit.yaml',
    'P35_share_price_manipulation_4626.yaml',
    'P36_metamorphic_contract.yaml',
    'P37_implementation_selfdestruct.yaml',
    'P38_constructor_in_implementation.yaml',
    'P39_function_clashing.yaml',
    'P40_uups_no_upgrade_guard.yaml',
    'P41_contract_existence_check.yaml',
    'P42_gas_stipend_dependency.yaml',
    'P43_delegatecall_untrusted.yaml',
    'P44_staticcall_side_effects.yaml',
    'P45_create2_collision.yaml',
    'P50_honeypot_detection.yaml',
    'P51_fee_on_transfer_accounting.yaml',
    'P52_deflationary_token_balance.yaml',
    'P60_flash_loan_governance.yaml',
    'P61_low_quorum_governance.yaml',
    'P62_timelock_bypass.yaml',
    'P63_voter_delegation_attack.yaml',
    'P64_proposal_front_running.yaml',
    'P65_cancel_execute_race.yaml',
    'P70_eip2612_permit_frontrun.yaml',
    'P71_eip712_domain_separator.yaml',
    'P72_signature_malleability.yaml',
    'P73_missing_nonce_increment.yaml',
    'P74_cross_chain_replay.yaml',
    'P75_weak_prng.yaml',
    'P76_predictable_randomness.yaml',
]

print("=" * 60)
print("MaatEye Pattern Cleanup")
print("=" * 60)

# Step 1: Back up duplicates
for f in to_delete:
    src = os.path.join(patterns_dir, f)
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(backup_dir, f))
        os.remove(src)
        print(f"  DELETED {f}")
    else:
        print(f"  SKIP (not found) {f}")

# Step 2: Rename duplicates to new IDs
for old_fn, new_id, new_fn in to_rename:
    src = os.path.join(patterns_dir, old_fn)
    if os.path.exists(src):
        # Read and update the ID
        with open(src) as fh:
            content = fh.read()
        p = yaml.safe_load(content)
        old_id = p.get('id', '???')
        p['id'] = new_id
        p['name'] = p.get('name', '') + f' (was {old_id})'
        new_path = os.path.join(patterns_dir, new_fn)
        with open(new_path, 'w') as fh:
            yaml.dump(p, fh, default_flow_style=False, allow_unicode=True, sort_keys=False)
        os.remove(src)
        print(f"  RENAMED {old_fn} -> {new_fn} (ID: {old_id} -> {new_id})")
    else:
        print(f"  SKIP (not found) {old_fn}")

# Step 3: Verify no duplicates remain
print()
print("=" * 60)
print("Verifying...")
files = sorted(os.listdir(patterns_dir))
yaml_files = [f for f in files if f.endswith('.yaml') and f != '__init__.py']
from collections import Counter
ids = []
for f in yaml_files:
    with open(os.path.join(patterns_dir, f)) as fh:
        p = yaml.safe_load(fh)
    if p and 'id' in p:
        ids.append(p['id'])
dupes = {k: v for k, v in Counter(ids).items() if v > 1}
print(f"Files: {len(yaml_files)}, Unique IDs: {len(set(ids))}, Remaining dupes: {len(dupes)}")
for d in dupes:
    flist = [f for f in yaml_files if yaml.safe_load(open(os.path.join(patterns_dir, f))).get('id') == d]
    print(f"  {d}: {flist}")

if not dupes:
    print("✅ ALL CLEAN! No duplicate IDs.")
else:
    print("⚠️  Still have duplicates.")
