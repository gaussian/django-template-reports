import re
from copy import deepcopy
from pptx.oxml.text import CT_TextBody
from pptx.table import _Cell
from .merger import merge_runs_in_paragraph
from ..templating import process_text


def process_table_cell(cell, context, errors, request_user, check_permissions):
    """
    Process the text in a table cell.

    If the cell's entire text is exactly one placeholder, process in "table" mode.
    If the result is a list, expand the table by adding new rows.
    Otherwise, for mixed text, process each paragraph in "normal" mode.
    """
    cell_text = cell.text.strip()
    if re.fullmatch(r"\{\{.*\}\}", cell_text):
        result = process_text(
            cell_text,
            context,
            errors=errors,
            request_user=request_user,
            check_permissions=check_permissions,
            mode="table",
        )
        if isinstance(result, list):
            expand_table_cell_with_list(cell, result)
        else:
            cell.text = result
    else:
        for paragraph in cell.text_frame.paragraphs:
            merge_runs_in_paragraph(
                paragraph, context, errors, request_user, check_permissions, mode="normal"
            )


def expand_table_cell_with_list(cell, items):
    """
    Expand the table by adding a new row for each additional item in `items`.
    The original cell is updated with the first item; for each subsequent item, a new row is cloned
    and the corresponding cell (at the same column index) is updated with the item's text.

    Uses _Cell to update the text properly.
    """
    if not items:
        cell.text = ""
        return

    # Set first item in original cell.
    cell.text = str(items[0])

    # Get the row element (<a:tr>) and table element (<a:tbl>) from the cell's XML.
    row_element = cell._tc.getparent()
    table_element = row_element.getparent()

    # Determine the cell's index in the row.
    row_cells = list(row_element)
    cell_index = row_cells.index(cell._tc)

    # For each additional item, clone the row.
    for item in items[1:]:
        new_row_element = deepcopy(row_element)
        # Get the target cell element in the cloned row.
        new_row_cells = list(new_row_element)
        if cell_index < len(new_row_cells):
            target_cell_element = new_row_cells[cell_index]
            # Create a new _Cell object for the target cell.
            new_cell = _Cell(target_cell_element, new_row_element)
            # Set its text.
            new_cell.text = str(item)
        # Append the new row to the table.
        table_element.append(new_row_element)
