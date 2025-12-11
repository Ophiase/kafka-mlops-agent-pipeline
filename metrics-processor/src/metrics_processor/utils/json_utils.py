import json
import re
from typing import List, Optional


def parse_llm_response(response: str, expected_count: int) -> List[Optional[str]]:
    """
    Parses the LLM response to extract sentiment analysis results.
    Args:
        response: The raw response string from the LLM.
        expected_count: The expected number of results based on input posts.
    Returns:
        A list of JSON strings representing sentiment analysis results, or None for failures.
    """

    if not response:
        return [None] * expected_count

    try:
        json_block = re.search(r"```json\s*(\[.*?\])\s*```", response, re.DOTALL)
        if json_block:
            response = json_block.group(1)
        else:
            bracketed = re.search(r"(\[.*\])", response, re.DOTALL)
            if bracketed:
                response = bracketed.group(1)

        data = json.loads(response)

        if not isinstance(data, list):
            print(f"[Processor] Error: expected list, got {type(data)}")
            return [None] * expected_count

        if len(data) != expected_count:
            print(f"[Processor] Warning: expected {expected_count}, got {len(data)}")
            return [None] * expected_count

        return [json.dumps(item) for item in data]

    except json.JSONDecodeError:
        print("[Processor] Failed to decode JSON response.")
        fallback = best_effort_parse(response, expected_count)
        if fallback is not None:
            return fallback
        return [None] * expected_count
    except Exception as exc:
        print(f"[Processor] Unexpected error parsing response: {exc}")
        return [None] * expected_count


def best_effort_parse(
    response: str, expected_count: int
) -> Optional[List[Optional[str]]]:
    """Attempts a tolerant parse when the LLM returns slightly invalid JSON.

    This primarily escapes stray quotes inside the explanation field (e.g.,
    "The \"Samstag Show\" ...") that otherwise break strict JSON parsing.
    Returns None if parsing still fails.
    """

    objects = re.findall(r"\{[^}]*\}", response, re.DOTALL)
    if not objects:
        return None

    parsed: List[str] = []
    for raw_obj in objects:
        normalized = escape_explanation_quotes(raw_obj)
        try:
            data_obj = json.loads(normalized)
            parsed.append(json.dumps(data_obj))
        except json.JSONDecodeError:
            continue

    if len(parsed) != expected_count:
        return None

    return parsed


def escape_explanation_quotes(raw_obj: str) -> str:
    """Escapes unescaped quotes in the explanation field within a JSON object string."""

    parts = raw_obj.split('"explanation":', 1)
    if len(parts) != 2:
        return raw_obj

    head, tail = parts
    tail_stripped = tail.lstrip()

    if not tail_stripped.startswith('"'):
        return raw_obj

    # Drop the leading quote for analysis
    body = tail_stripped[1:]
    closing_idx = body.rfind('"')
    if closing_idx == -1:
        return raw_obj

    value = body[:closing_idx]
    rest = body[closing_idx + 1 :]

    escaped_value = value.replace('"', '\\"')
    rebuilt_tail = f' "{escaped_value}"{rest}'

    return head + '"explanation":' + rebuilt_tail
