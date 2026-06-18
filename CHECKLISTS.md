# 👁️⚖️ MaatEye — Master Checklists

This document contains actionable checklists for ongoing maintenance and project completion. (See `DEVELOPMENT_MAP.md` for the original phase-by-phase breakdown).

---

## 🛠️ Maintenance Checklist (Before Every Release)

- [ ] Run python syntax check: `find scanner tools -name "*.py" | xargs python3 -m py_compile`
- [ ] Run full test suite: `python -m pytest scanner/tests/`
- [ ] Confirm all 20 patterns load without errors: `python -c "from scanner.utils.config import get_all_patterns; print(len(get_all_patterns()))"`
- [ ] Verify `dashboard.json` format is valid
- [ ] Verify `data/token_registry.json` is not corrupted (run `python -m scanner.main tokens stats`)

---

## 🚀 Immediate Next Steps (Pending Features)

- [ ] **Expand Chain Support:** Update `scanner/chains/__init__.py` to include the remaining 36 blockchains supported by Etherscan V2.
- [ ] **UI Polish:** Add a search/filter bar to the Chain Comparison table on the GitHub Pages dashboard.
- [ ] **Documentation:** Update the `README.md` to display all 20 patterns (currently the table truncates at P11).
- [ ] **Security:** Confirm `EVM_CHAINS` correctly maps the new Etherscan V2 unified endpoints.

---

## 🔎 New Pattern Checklist (When Adding a Plague)

When adding a new vulnerability pattern (e.g., `P21_...yaml`):
- [ ] Must have `id`, `name`, `severity` (critical, high, medium, low).
- [ ] Must have clear `description`.
- [ ] Must contain at least one detector (`regex` or `function_signature`).
- [ ] Must include a clear `recommendation` for fixing the vulnerability.
- [ ] Must be tested against a known vulnerable contract.
- [ ] Must be added to the GitHub Pages dashboard UI list (if hardcoded).
