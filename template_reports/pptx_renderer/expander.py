import re
from .merger import merge_runs_in_paragraph
from ..templating import process_text


def process_table_cell(cell, context, errors, request_user, check_permissions):
    """
    Process a table cell. If the entire cell text is exactly a placeholder,
    call process_text in "table" mode.

    If the result is a list, expand the cell into multiple rows.
    Otherwise, set the cell text to the processed result.
    For non-pure cells, process each paragraph normally (using normal mode).
    """
    placeholder = cell.text.strip()
    if re.fullmatch(r"\{\{.*\}\}", placeholder):
        result = process_text(
            placeholder, context, errors, request_user, check_permissions, mode="table"
        )
        if isinstance(result, list):
            _expand_table_cell_with_list(cell, result)
        else:
            cell.text = result
    else:
        for paragraph in cell.text_frame.paragraphs:
            merge_runs_in_paragraph(
                paragraph, context, errors, request_user, check_permissions, mode="normal"
            )


def _expand_table_cell_with_list(cell, items):
    """
    Expand the table cell when the processed placeholder returns a list.
    For each item in the list, create a new row by cloning the current row,
    and replace the text in the target cell with the item.

    This is a simplified XML cloning workaround.
    """
    # Replace current cell text with first item.
    cell.text = str(items[0])
    # For each subsequent item, clone the row and update the corresponding cell.
    # (Detailed row cloning is implementation-specific; this is a placeholder.)
    for item in items[1:]:
        # [IMPLEMENT ROW CLONING AND INSERTION HERE]
        pass
