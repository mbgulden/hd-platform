---
name: collect-birth-details
description: >
  Conversational Birth Detail Collection and Chart Generation.
  Collects birth date, birth time, and birth city progressively when missing, resolves
  coordinates, and invokes chart generation. User-facing date format is MM/DD/YYYY
  or natural language; convert to YYYY-MM-DD only for internal tool calls.
triggers:
  - user_asks_about_chart
  - session_start (if birth profile missing)
  - user_asks_to_calculate_design
dependencies:
  - MCP server: daily_journal (tool: generate_human_design_chart)
---

# Conversational Birth Detail Collection Skill

## Purpose
This skill guides the agent to conversationally gather missing birth details from the user, parse their text responses into structured JSON values, validate the coordinates, and call the local `generate_human_design_chart` tool to create their bodygraph and PDF life summary report.

## Conversation Flow & Pacing
1. **Sanctuary Tone**: Keep the interaction low-stimulus, quiet, and deliberate. Do not rush.
2. **Show, Don't Tell**: Do not recite the intake process or present all requirements at once. Embody calm progression.
3. **Step-by-Step Gathering**: Ask for details one at a time to prevent cognitive overwhelm:
   * **Step 1**: Date of Birth. Ask in American-facing format: MM/DD/YYYY, while also accepting normal speech like "June 14, 1990". Convert to YYYY-MM-DD only when calling the tool.
   * **Step 2**: Exact Birth Time. Ask naturally ("What time were you born? Approximate is okay."). Convert to HH:MM 24-hour format internally. If unknown, explain that noon can be used as a temporary placeholder, but exact time is preferred.
   * **Step 3**: Birth Location (City, State/Country. e.g. "Honolulu, Hawaii").
4. **Execution**:
   * Once all details are gathered, tell the user something low-pressure like: *"Good. I have enough to build the chart now — give me a moment."*
   * Call the tool `generate_human_design_chart` passing the collected parameters.
   * Highlight the core chart statistics (Type, Profile, Inner Authority) returned in the tool response. Do not use complex jargon.

## Parsing Examples

* "I was born on Oct 10 1994 at 2:15 PM in London"
  -> Internal Date: `1994-10-10`
  -> Time: `14:15`
  -> Location: `London, UK`
  -> Trigger: `generate_human_design_chart(birth_date="1994-10-10", birth_time="14:15", location="London, UK")`

* "1988-05-12 at 9:00 AM, in Seattle Washington"
  -> Internal Date: `1988-05-12`
  -> Time: `09:00`
  -> Location: `Seattle, WA`
  -> Trigger: `generate_human_design_chart(birth_date="1988-05-12", birth_time="09:00", location="Seattle, WA")`
