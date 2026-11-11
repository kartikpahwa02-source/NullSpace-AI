"""
Code Executor — AI khud code likhta hai, run karta hai, seekhta hai
"""

import subprocess
import os
import sys
import tempfile
import traceback
from datetime import datetime
from brain.knowledge_base import save_code, get_code_history
from brain.llm import ask_llm_direct


def write_and_run_code(purpose, language="python"):
    """AI khud code likhega aur run karega"""

    # Step 1: Past code dekho (similar purpose ka)
    history = get_code_history(limit=5)
    history_text = ""
    if history:
        history_text = "Previous code:\n" + "\n".join([f"- {h['purpose']}: {h['code'][:200]}" for h in history])

    # Step 2: AI se code likhwao
    prompt = f"""Write {language} code for: {purpose}

{history_text}

Rules:
1. Write COMPLETE, WORKING code
2. Include error handling
3. Add comments
4. Make it production-ready

Reply with ONLY the code, no explanation."""

    code = ask_llm_direct(prompt)

    # Clean code (remove markdown)
    if "```" in code:
        parts = code.split("```")
        for part in parts:
            if language in part.lower() or "import" in part or "def " in part or "print" in part:
                code = part.replace("python", "").replace("Python", "").strip()
                break

    # Step 3: Run code
    result = execute_code(code, language)

    # Step 4: Save to database
    success = "Error" not in result and "error" not in result.lower()
    save_code(language, code, purpose, result[:1000], success)

    return {
        "code": code,
        "result": result,
        "success": success
    }


def execute_code(code, language="python"):
    """Code run karo"""
    if language == "python":
        return _run_python(code)
    elif language == "bash" or language == "cmd":
        return _run_command(code)
    else:
        return f"Language '{language}' not supported yet"


def _run_python(code):
    """Python code run karo"""
    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        # Run with timeout
        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=30
        )

        os.unlink(temp_path)

        output = ""
        if result.stdout:
            output += f"Output:\n{result.stdout}"
        if result.stderr:
            output += f"\nErrors:\n{result.stderr}"

        return output if output else "Code ran successfully (no output)"

    except subprocess.TimeoutExpired:
        return "Error: Code took too long (>30 seconds)"
    except Exception as e:
        return f"Error: {str(e)}"


def _run_command(cmd):
    """System command run karo"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=15
        )
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += f"\n{result.stderr}"
        return output if output else "Done"
    except Exception as e:
        return f"Error: {e}"


def debug_code(code, error):
    """Code debug karo"""
    prompt = f"""Fix this code:

Code:
{code}

Error:
{error}

Reply with ONLY the fixed code."""

    fixed = ask_llm_direct(prompt)

    if "```" in fixed:
        parts = fixed.split("```")
        for part in parts:
            if "import" in part or "def " in part or "print" in part:
                fixed = part.replace("python", "").strip()
                break

    return fixed