from ..templating import process_text
from .exceptions import UnterminatedTagException


def merge_runs_in_paragraph(
    paragraph, context, errors, request_user, check_permissions, mode="normal"
):
    """
    Merge placeholders in a paragraph if a single placeholder ({{ ... }}) is split across multiple runs.
    We then call process_text in the specified mode.

    Steps:
      1) If a run has "{{" but not "}}", we keep concatenating subsequent runs
         until we see one containing "}}" or we run out of runs.
      2) Once we unify them into one string, we call process_text(..., mode=mode)
         which handles pure vs. mixed text, date formatting, list joining, etc.
      3) We replace the text in the first run with the processed result and delete the subsequent runs.

    If no "}}" is found for a run that starts with "{{", raises UnterminatedTagException.
    """
    runs = paragraph.runs
    i = 0
    while i < len(runs):
        current_text = runs[i].text
        if "{{" in current_text and "}}" not in current_text:
            merged_text = current_text
            j = i + 1
            found_closing = False
            while j < len(runs):
                merged_text += runs[j].text
                if "}}" in runs[j].text:
                    found_closing = True
                    break
                j += 1
            if not found_closing:
                raise UnterminatedTagException(
                    f"Unterminated tag starting in run {i}: {current_text}"
                )
            # Now we have a single string with the entire placeholder. We process it.
            processed = process_text(
                merged_text,
                context,
                errors=errors,
                request_user=request_user,
                check_permissions=check_permissions,
                mode=mode,
            )
            runs[i].text = processed if isinstance(processed, str) else str(processed)
            # Remove the merged runs from i+1 up to j inclusive.
            for k in range(i + 1, j + 1):
                paragraph._p.remove(runs[k]._r)
            runs = paragraph.runs  # refresh
        else:
            # If the run already has both {{ and }} or none at all,
            # we just call process_text.
            processed = process_text(
                current_text,
                context,
                errors=errors,
                request_user=request_user,
                check_permissions=check_permissions,
                mode=mode,
            )
            if isinstance(processed, str):
                runs[i].text = processed
            else:
                # In normal mode, process_text might return a list if it's pure
                # but we are in a single run, so let's join it anyway.
                runs[i].text = ", ".join(str(item) for item in processed)
        i += 1
