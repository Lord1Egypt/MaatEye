"""MaatEye — Pattern Validator
Validates patterns against test data.
"""

from scanner.utils.logger import get_logger

logger = get_logger(__name__)


def validate_pattern(pattern_id: str, pattern: dict) -> str:
    """Validate a single pattern's configuration."""
    issues = []

    if "id" not in pattern:
        issues.append("❌ Missing 'id' field")
    if "name" not in pattern:
        issues.append("❌ Missing 'name' field")
    if "severity" not in pattern:
        issues.append("❌ Missing 'severity' field")
    if "detectors" not in pattern or not pattern["detectors"]:
        issues.append("❌ No detectors defined")

    severity = pattern.get("severity", "")
    if severity not in ("critical", "high", "medium", "low"):
        issues.append(f"⚠️  Unknown severity: {severity}")

    for i, detector in enumerate(pattern.get("detectors", [])):
        det_type = detector.get("type", "")
        if det_type not in ("regex", "function_signature", "ast_pattern"):
            issues.append(f"⚠️  Detector {i}: unknown type '{det_type}'")
        if not detector.get("description"):
            issues.append(f"⚠️  Detector {i}: missing description")
        if det_type == "regex" and not detector.get("pattern"):
            issues.append(f"❌ Detector {i}: regex pattern missing")

    if not issues:
        return f"✅ {pattern_id} ({pattern.get('name', '')}) — valid"
    else:
        return f"⚠️  {pattern_id} — issues:\n" + "\n".join(f"  {i}" for i in issues)


def validate_patterns(patterns: dict) -> str:
    """Validate all patterns."""
    results = []
    for pid, pattern in sorted(patterns.items()):
        results.append(validate_pattern(pid, pattern))
    return "\n".join(results)
