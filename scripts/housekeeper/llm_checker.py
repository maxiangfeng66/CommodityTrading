"""
LLM Checker - Uses AI for semantic similarity confirmation

Simplified version that uses direct API calls for semantic comparison.
"""

import sys
from pathlib import Path
from typing import Tuple

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
_SCRIPT_DIR = Path(__file__).parent

if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from scripts.housekeeper.config import LLM_COMPARISON_PROMPT, LLM_SYSTEM_PROMPT
except ImportError:
    from config import LLM_COMPARISON_PROMPT, LLM_SYSTEM_PROMPT


def check_semantic_similarity(
    new_code: str,
    existing_code: str,
    new_name: str = "",
    existing_name: str = "",
) -> Tuple[str, str]:
    """
    Check if two code pieces are semantically equivalent.

    This is a simplified version that returns SIMILAR for high embedding matches,
    without requiring an external LLM API.

    For full LLM-based checking, you can extend this to use OpenAI/Anthropic APIs.

    Args:
        new_code: The new function/class code
        existing_code: The existing function/class code
        new_name: Name of the new code
        existing_name: Name of the existing code

    Returns:
        Tuple of (verdict: "SAME"|"SIMILAR"|"DIFFERENT"|"UNKNOWN", explanation: str)
    """
    # Simple heuristic-based check without LLM
    # Compare normalized code structure

    # Remove comments and whitespace for comparison
    def normalize_code(code: str) -> str:
        lines = []
        for line in code.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                lines.append(line)
        return '\n'.join(lines)

    norm_new = normalize_code(new_code)
    norm_existing = normalize_code(existing_code)

    # Check for very similar structure
    if norm_new == norm_existing:
        return "SAME", "Identical code structure"

    # Count common significant tokens
    new_tokens = set(norm_new.split())
    existing_tokens = set(norm_existing.split())

    if not new_tokens or not existing_tokens:
        return "DIFFERENT", "Unable to compare"

    common = len(new_tokens & existing_tokens)
    total = len(new_tokens | existing_tokens)
    token_similarity = common / total if total > 0 else 0

    if token_similarity > 0.8:
        return "SAME", f"High token similarity ({token_similarity:.0%})"
    elif token_similarity > 0.5:
        return "SIMILAR", f"Moderate token similarity ({token_similarity:.0%})"
    else:
        return "DIFFERENT", f"Low token similarity ({token_similarity:.0%})"


def get_existing_code(file_path: str, line_number: int, num_lines: int = 30) -> str:
    """
    Read existing code from a file.

    Args:
        file_path: Path to the file (relative to project root)
        line_number: Starting line number
        num_lines: Number of lines to read

    Returns:
        The code snippet
    """
    full_path = PROJECT_ROOT / file_path

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        start = max(0, line_number - 1)
        end = min(len(lines), start + num_lines)

        return ''.join(lines[start:end])
    except Exception as e:
        print(f"[Housekeeper] Could not read {file_path}: {e}")
        return ""


if __name__ == "__main__":
    # Test the checker
    code1 = """
def validate_dcf(cashflows, discount_rate):
    '''Validate DCF calculation inputs'''
    if not cashflows:
        return False
    if discount_rate <= 0:
        return False
    return True
"""

    code2 = """
def check_cashflow_validity(flows, rate):
    '''Check if cashflow data is valid for DCF'''
    if len(flows) == 0:
        return False
    if rate < 0:
        return False
    return True
"""

    verdict, explanation = check_semantic_similarity(code1, code2)
    print(f"Verdict: {verdict}")
    print(f"Explanation: {explanation}")
