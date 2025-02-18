from ..templating import process_text
from .exceptions import UnterminatedTagException


def merge_runs_in_paragraph(
    paragraph, context, errors, request_user, check_permissions, mode="normal"
):
    """
    Iterate through runs in a paragraph. If a run contains a starting '{{' without a closing '}}',
    merge subsequent runs into that run until the closing '}}' is found.

    Raise UnterminatedTagException if no closing '}}' is found in the paragraph.
    After merging, process the merged text using process_text with the given mode.
    Subsequent runs that have been merged are removed.
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
            processed_text = process_text(
                merged_text,
                context=context,
                errors=errors,
                request_user=request_user,
                check_permissions=check_permissions,
                mode=mode,
            )
            runs[i].text = processed_text
            # Remove the merged runs.
            for k in range(i + 1, j + 1):
                paragraph._p.remove(runs[k]._r)
            runs = paragraph.runs
        else:
            processed_text = process_text(
                current_text,
                context=context,
                errors=errors,
                request_user=request_user,
                check_permissions=check_permissions,
                mode=mode,
            )
            runs[i].text = processed_text
        i += 1
