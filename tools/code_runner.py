from brain.code_executor import write_and_run_code, execute_code, debug_code, get_code_history


def run_purpose_code(purpose):
    """Purpose ke hisaab se code likho aur run karo"""
    result = write_and_run_code(purpose)
    output = f"💻 Code Written for: {purpose}\n\n"
    output += f"Code:\n```python\n{result['code']}\n```\n\n"
    output += f"Result: {'✅ Success' if result['success'] else '❌ Failed'}\n"
    output += f"Output:\n{result['result']}"
    return output


def run_custom_code(code):
    """Custom code run karo"""
    return execute_code(code)


def fix_code(code, error):
    """Code fix karo"""
    fixed = debug_code(code, error)
    result = execute_code(fixed)
    return f"Fixed Code:\n{fixed}\n\nResult:\n{result}"


def show_code_history():
    """Past code dekho"""
    history = get_code_history(10)
    if not history:
        return "No code history yet."

    output = "💻 Code History:\n\n"
    for h in history:
        status = "✅" if h["success"] else "❌"
        output += f"{status} [{h['language']}] {h['purpose']}\n"
        output += f"   Code: {h['code'][:100]}...\n"
        output += f"   Date: {h['created_at']}\n\n"
    return output