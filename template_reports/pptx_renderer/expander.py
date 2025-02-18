from copy import deepcopy
import re
from .merger import merge_runs_in_paragraph
from ..templating import process_text
from pptx.oxml.text import CT_TextBody
from pptx.table import _Cell


def process_table_cell(cell, context, errors, request_user, check_permissions):
    """
    Process the text in a table cell.

    1) If the cell is a pure placeholder (only one tag):
       - We call process_text(..., mode="table"). If this returns a list, we expand the table.
         If it returns a string, we just set the cell text.
    2) Otherwise (mixed text, or partial placeholders), we call merge_runs_in_paragraph in normal mode
       for each paragraph. This handles placeholders split across multiple runs.
    """
    cell_text = cell.text.strip()
    # If cell is a single placeholder
    if re.fullmatch(r"\{\{.*\}\}", cell_text):
        raw_result = process_text(
            cell_text,
            context,
            errors=errors,
            request_user=request_user,
            check_permissions=check_permissions,
            mode="table",
        )
        if isinstance(raw_result, list):
            expand_table_cell_with_list(cell, raw_result)
        else:
            cell.text = raw_result
    else:
        # Not a pure placeholder -> run merging in normal mode
        for paragraph in cell.text_frame.paragraphs:
            merge_runs_in_paragraph(
                paragraph,
                context,
                errors,
                request_user,
                check_permissions,
                mode="normal",
            )


def expand_table_cell_with_list(cell, items):
    """
    Expand the table by creating a new row for each item in `items`.
    The first item replaces the cell's original text; subsequent items create new rows.

    This approach replicates the row that contains the cell (via deepcopy)
    and appends the duplicated row to the table. Then, in that duplicated row,
    we replace the text of the same column index with the item text.

    NOTE: python-pptx doesn't officially support adding rows at runtime,
    so this code is an unsupported workaround. It may break in complex tables.
    """

    # If the list is empty, just clear the cell text.
    if not items:
        cell.text = ""
        return

    # 1) Place the first item in the current cell (no new row yet).
    cell.text = str(items[0])

    # 2) Identify the row and table from the cell’s XML.
    row_element = cell._tc.getparent()  # <a:tr> element for this row
    table_element = row_element.getparent()  # <a:tbl> element for the table

    # 3) Figure out the cell's "column index" in the row.
    row_cells = list(row_element)  # the <a:tc> elements in this row
    cell_index = row_cells.index(cell._tc)

    # 4) For each additional item, clone this row and replace the cell’s text.
    for item in items[1:]:
        new_row_element = deepcopy(row_element)
        new_cells = list(new_row_element)

        # Replace text in the same column index:
        if cell_index < len(new_cells):
            target_cell_element = new_cells[cell_index]
            # Remove any existing text content
            for txBody in target_cell_element.findall(".//a:txBody", cell._tc.nsmap):
                target_cell_element.remove(txBody)
            # Create a new text body for the item text
            new_txBody = CT_TextBody()
            new_txBody.text = str(item)
            target_cell_element.append(new_txBody)

        # Append the new row to the table
        table_element.append(new_row_element)
