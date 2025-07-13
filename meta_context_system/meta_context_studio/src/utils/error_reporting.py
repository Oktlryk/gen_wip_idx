import os
import datetime
import traceback
import platform
import sys
from typing import List, Dict, Any

REQUEST_FOR_RESOLUTION_DIR = "request_for_resolution"

def generate_error_report(
    summary: str,
    error: Exception,
    code_context: Dict[str, Any],
    reproduction_steps: Dict[str, Any],
    key_dependencies: List[str]
) -> str:
    """Generates a structured markdown report for an unhandled exception."""
    timestamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    report_filename = f"resolution_request_{code_context.get('agent_name', 'unknown_agent')}_{timestamp}.md"
    report_path = os.path.join(REQUEST_FOR_RESOLUTION_DIR, report_filename)

    os.makedirs(REQUEST_FOR_RESOLUTION_DIR, exist_ok=True)

    stack_trace = traceback.format_exc()

    report_content = f"""
# Request for Resolution

## Summary
{summary}

## Error & Stack Trace
```python
{stack_trace}
```

## Code Context
- File: {code_context.get('file', 'N/A')}
- Function/Method: {code_context.get('function', 'N/A')}
```python
{code_context.get('snippet', 'N/A')}
```

## Reproduction Steps
- Command: {reproduction_steps.get('command', 'N/A')}
- Input File: {reproduction_steps.get('input_file', 'N/A')}

## System Environment
- Python Version: {sys.version}
- Operating System: {platform.system()} {platform.release()}
- Key Dependencies:
{chr(10).join([f'  - {dep}' for dep in key_dependencies])}

## Intended vs. Actual Behavior
{reproduction_steps.get('intended_vs_actual', 'N/A')}
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return report_path
