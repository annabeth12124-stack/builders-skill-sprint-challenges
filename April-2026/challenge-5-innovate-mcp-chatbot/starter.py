"""
Challenge 5 (Innovate): Build Your Own MCP-Powered Agent

YOUR TASK:
  Build an innovative agent from scratch that connects to any MCP server.
  The most creative and useful agent gets a special shoutout! 🏆

RULES:
  - Must use Strands Agents SDK
  - Must use at least one MCP server
  - Must use Amazon Nova Pro (or any Bedrock model)
  - Must have an interactive chat loop
  - Must be YOUR OWN idea — be creative!

EXAMPLE MCP SERVERS:
  pip install awslabs.aws-documentation-mcp-server   # AWS Docs
  uvx awslabs.cdk-mcp-server@latest                  # AWS CDK
  uvx awslabs.cost-analysis-mcp-server@latest        # AWS Pricing

BROWSE MORE: https://github.com/modelcontextprotocol/servers

RESOURCES:
  - Strands MCP docs: https://strandsagents.com/latest/user-guide/concepts/tools/mcp-tools/
  - AWS MCP servers: https://github.com/awslabs/mcp

Build something that makes us go "whoa!" 🚀
"""

# Your code here — build the entire agent from scratch!
"""
╔══════════════════════════════════════════════════════════╗
║        AWS ARCHITECTURE ROASTER 🔥                       ║
║  Describe your setup. Get roasted. Cry. Learn. Grow.     ║
╚══════════════════════════════════════════════════════════╝

Usage:
    pip install strands-agents awslabs.aws-documentation-mcp-server
    python roaster.py
"""

import re
import sys
from strands import Agent
from strands.tools.mcp import MCPClient
from mcp import StdioServerParameters, stdio_client

# ── Colours ───────────────────────────────────────────────────────
R  = "\033[91m"   # red
Y  = "\033[93m"   # yellow
G  = "\033[92m"   # green
C  = "\033[96m"   # cyan
M  = "\033[95m"   # magenta
B  = "\033[1m"    # bold
D  = "\033[2m"    # dim
RS = "\033[0m"    # reset

BANNER = f"""
{R}{B}
  ██████╗  ██████╗  █████╗ ███████╗████████╗███████╗██████╗
  ██╔══██╗██╔═══██╗██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗
  ██████╔╝██║   ██║███████║███████╗   ██║   █████╗  ██████╔╝
  ██╔══██╗██║   ██║██╔══██║╚════██║   ██║   ██╔══╝  ██╔══██╗
  ██║  ██║╚██████╔╝██║  ██║███████║   ██║   ███████╗██║  ██║
  ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
{RS}{Y}{B}
        🔥  AWS Architecture Roaster  🔥
{RS}{D}     Describe your cloud setup. Get destroyed. Learn something.{RS}
"""

SYSTEM_PROMPT = """\
You are a hilariously blunt AWS solutions architect — a seasoned cloud veteran who \
reviews architectures with sharp wit and sarcastic humour. Think: a code reviewer \
who has seen every possible anti-pattern and responds with exasperated comedy. \
Every critique is backed by a real AWS best practice or documentation reference.

When the user describes their AWS setup:

1. Use the AWS Documentation MCP tool to look up best practices for the services \
they mentioned. Ground every critique in real AWS guidance.

2. Humorously critique each anti-pattern or poor decision with sarcasm and wit. \
Reference actual AWS service names, quotas, failure modes, and well-known \
cloud reliability principles. Keep it funny but technically accurate.

3. At the very end of your response, output EXACTLY this block and nothing after it:

SCORECARD
Architecture Score: X/10
Roast Severity: <level>

Where X is 1–10 based on how sound the architecture is, \
and <level> is exactly one of: Mild | Medium | Spicy | Nuclear | Disappointed

Severity guide:
- Mild        → score 7-8  (minor issues, mostly solid)
- Medium      → score 5-6  (real problems but fixable)
- Spicy       → score 3-4  (significant concerns)
- Nuclear     → score 1-2  (a textbook example of what not to do)
- Disappointed → score 9-10 (excellent architecture; nothing to critique)

If score is 9-10: set severity to "Disappointed" and express deep comic \
disappointment that you had nothing to work with. \
Say something like "I came here to critique someone. You've robbed me of that joy."

Keep your critique to 150–250 words before the SCORECARD. Make it memorable.
"""

SEVERITY_COLOURS = {
    "mild":          G,
    "medium":        Y,
    "spicy":         R,
    "nuclear":       M,
    "disappointed":  C,
}

SEVERITY_EMOJI = {
    "mild":          "🌶️ ",
    "medium":        "🔥",
    "spicy":         "💀",
    "nuclear":       "☢️ ",
    "disappointed":  "😤",
}


def parse_scorecard(text: str):
    """Extract score and severity from the SCORECARD block."""
    score_match    = re.search(r"Architecture Score:\s*(\d+)/10", text, re.IGNORECASE)
    severity_match = re.search(r"Roast Severity:\s*(\w+)", text, re.IGNORECASE)
    score    = int(score_match.group(1))    if score_match    else None
    severity = severity_match.group(1).lower() if severity_match else None
    return score, severity


def render_score_bar(score: int) -> str:
    """Render a colourful 10-block progress bar."""
    filled = score
    empty  = 10 - score
    colour = G if score >= 7 else Y if score >= 4 else R
    bar = colour + B + "█" * filled + RS + D + "░" * empty + RS
    return bar


def print_scorecard(score, severity):
    """Pretty-print the scorecard box after the roast."""
    if score is None or severity is None:
        return

    sev_colour = SEVERITY_COLOURS.get(severity, Y)
    emoji      = SEVERITY_EMOJI.get(severity, "🔥")
    bar        = render_score_bar(score)

    print(f"\n{D}{'─' * 52}{RS}")
    print(f"  🏆  {B}Architecture Score:{RS}  {bar}  {B}{score}/10{RS}")
    print(f"  {emoji}  {B}Roast Severity:   {RS}  {sev_colour}{B}{severity.capitalize()}{RS}")
    print(f"{D}{'─' * 52}{RS}\n")


def strip_thinking(text: str) -> str:
    """Remove <thinking> blocks — closed or unclosed — that Nova Pro leaks."""
    # Remove properly closed blocks first
    text = re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.DOTALL)
    # Remove anything from an unclosed <thinking> tag onwards
    text = re.sub(r"<thinking>.*", "", text, flags=re.DOTALL)
    return text.strip()


def strip_scorecard(text: str) -> str:
    """Remove the SCORECARD block so we can render it ourselves."""
    idx = text.find("SCORECARD")
    return text[:idx].strip() if idx != -1 else text


def strip_tool_lines(text: str) -> str:
    """Remove 'Tool #N: ...' lines Strands injects into the response string."""
    return re.sub(r"^Tool #[0-9]+:.*", "", text, flags=re.MULTILINE).strip()


def clean(text: str) -> str:
    """Full cleanup: thinking tags → tool lines → scorecard."""
    return strip_scorecard(strip_tool_lines(strip_thinking(text)))


def print_sep():
    print(f"\n{D}{'─' * 52}{RS}\n")


def main():
    print(BANNER)

    print(f"{C}[*] Connecting to AWS Docs MCP…{RS}")
    aws_docs_mcp = MCPClient(
        lambda: stdio_client(
            StdioServerParameters(command="awslabs.aws-documentation-mcp-server")
        )
    )

    try:
        aws_docs_mcp.__enter__()
        tools = aws_docs_mcp.list_tools_sync()
        print(f"  {G}✓{RS} AWS Docs MCP ready ({len(tools)} tools)\n")
    except Exception as e:
        print(f"  {R}✗ Could not connect to AWS Docs MCP: {e}{RS}")
        print(f"  {D}Run: pip install awslabs.aws-documentation-mcp-server{RS}")
        sys.exit(1)

    # Silent callback suppresses Strands' built-in stdout printing
    def _silent(**kwargs):
        pass

    agent = Agent(
        model="us.amazon.nova-pro-v1:0",
        system_prompt=SYSTEM_PROMPT,
        tools=tools,
        callback_handler=_silent,
    )

    print(f"{Y}{B}AWS ARCHITECTURE ROASTER{RS} is warmed up and ready to judge you.")
    print(f"{D}Describe your AWS setup. The worse it is, the better this gets.")
    print(f"Commands: 'quit' to exit | 'clear' to reset{RS}")
    print_sep()

    while True:
        try:
            user_input = input(f"{R}{B}you > {RS}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{D}Leaving so soon? Your architecture thanks you.{RS}")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print(f"{D}Goodbye. Go fix your subnets.{RS}")
            break
        if user_input.lower() == "clear":
            agent = Agent(
                model="us.amazon.nova-pro-v1:0",
                system_prompt=SYSTEM_PROMPT,
                tools=tools,
                callback_handler=lambda **kw: None,
            )
            print(f"{D}Fresh slate. New victim.{RS}")
            continue

        print(f"\n{R}{B}roaster > {RS}")

        try:
            response = agent(user_input)
            full_text = str(response)
        except Exception as e:
            print(f"\n{R}[!] Agent error: {e}{RS}")
            continue

        # Strip thinking tags + scorecard block, then print the roast body
        full_text_clean = strip_thinking(full_text)
        print(clean(full_text))

        score, severity = parse_scorecard(full_text_clean)
        print_scorecard(score, severity)
        print_sep()

    try:
        aws_docs_mcp.__exit__(None, None, None)
    except Exception:
        pass


if __name__ == "__main__":
    main()
