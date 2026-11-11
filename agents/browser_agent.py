from brain.llm import ask_llm_direct
from tools.browser_auto import (
    browse_open, browse_content, browse_click_text,
    browse_type_and_enter, browse_search_google,
    browse_scroll, browse_screenshot, browse_type_text,
    browse_click_css, close_driver
)

def run_browser_task(task: str) -> str:
    """
    AI ko task do — wo khud decide karega browser me kya karna hai
    Step by step execute karega
    """

    # Step 1: AI se plan lo
    plan_prompt = f"""You are a browser automation agent.
Task: "{task}"

Break this into numbered steps using ONLY these actions:
- open <url>
- search <query>
- click_text <text>
- type_enter <css_selector> <text>
- type <css_selector> <text>
- read
- scroll_down
- screenshot
- close

Examples:
Task: "Wikipedia me Artificial Intelligence search karo"
1. open https://wikipedia.org
2. type_enter #searchInput Artificial Intelligence
3. read
4. screenshot

Task: "YouTube me lofi music search karo"
1. open https://youtube.com
2. type_enter input[name="search_query"] lofi music
3. read

Give ONLY numbered steps, nothing else."""

    plan_text = ask_llm_direct(plan_prompt)

    # Step 2: Parse steps
    steps = []
    for line in plan_text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        # Remove numbering
        for prefix in ["1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10."]:
            if line.startswith(prefix):
                line = line[len(prefix):].strip()
                break
        if line:
            steps.append(line)

    if not steps:
        return f"Plan banane me error aaya:\n{plan_text}"

    # Step 3: Execute steps
    results = []
    for i, step in enumerate(steps):
        parts = step.split()
        action = parts[0].lower() if parts else ""

        try:
            if action == "open":
                url = " ".join(parts[1:])
                r = browse_open(url)

            elif action == "search":
                query = " ".join(parts[1:])
                r = browse_search_google(query)

            elif action == "click_text":
                text = " ".join(parts[1:])
                r = browse_click_text(text)

            elif action == "type_enter":
                selector = parts[1]
                text = " ".join(parts[2:])
                r = browse_type_and_enter(selector, text)

            elif action == "type":
                selector = parts[1]
                text = " ".join(parts[2:])
                r = browse_type_text(selector, text)

            elif action == "read":
                r = browse_content()

            elif action == "scroll_down":
                r = browse_scroll("down")

            elif action == "scroll_up":
                r = browse_scroll("up")

            elif action == "screenshot":
                r = browse_screenshot()

            elif action == "close":
                close_driver()
                r = "Browser band ho gaya"

            else:
                r = f"Unknown action: {action}"

        except Exception as e:
            r = f"Step error: {e}"

        results.append(f"Step {i+1}: {step}\nResult: {r}")

    # Step 4: Summary
    summary_prompt = f"""Task: {task}

Steps executed:
{chr(10).join(results)}

Give a short summary of what happened in Hindi/Hinglish."""
    summary = ask_llm_direct(summary_prompt)

    return f"Browser Task Complete\n\n{summary}"