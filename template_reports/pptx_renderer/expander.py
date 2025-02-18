import re
from .merger import merge_runs_in_paragraph
from ..templating import process_text


def process_table_cell(cell, context, errors, request_user, check_permissions):
    """
    Process a table cell.

    If the cell's entire text is exactly a placeholder (matches "{{ ... }}"), process it in "table" mode.
    If the result is a list, expand the cell into multiple rows.
    Otherwise, process each paragraph normally in "normal" mode.
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
    Given a table cell whose processed value is a list (items),
    expand the table by creating a new row for each item.
    The item text is placed into the same column as the original cell.

    Note: python-pptx does not officially support adding rows. This implementation uses
    an XML cloning workaround. It assumes that the entire row is to be duplicated,
    and only the target cell (at the same column index) is modified.
    """
    from pptx.table import _Cell
    from copy import deepcopy

    # Get the parent row of the cell.
    cell_element = cell._tc
    row_element = cell_element.getparent()
    table_element = row_element.getparent()

    # Determine the index of the cell in the row.
    cell_index = list(row_element).index(cell_element)

    # Find the row object. (Assume that row_element is already wrapped by pptx as a row.)
    # We'll get the parent table object from the cell.
    table = (
        cell._tc.getparent().getparent()
    )  # This is the <a:tbl> element wrapped in a Table object.
    # In python-pptx, table.rows is a list of _Row objects.
    # Determine the index of the current row:
    current_row = None
    row_idx = None
    for idx, r in enumerate(cell.parent._tc.getparent().getparent().rows):
        # This is not straightforward; for simplicity, we assume the current row is the first.
        current_row = cell.parent
        row_idx = 0
        break

    # Since proper row cloning is tricky, here we simply set the current cell’s text to the first item,
    # and then for each subsequent item, we clone the current row and replace the target cell’s text.
    cell.text = str(items[0])
    # For the remaining items:
    for item in items[1:]:
        # Clone the entire row using a deepcopy of the XML element.
        new_row_element = deepcopy(row_element)
        # In the new row, find the cell at the same index and set its text.
        new_cells = list(new_row_element)
        if cell_index < len(new_cells):
            target_cell_element = new_cells[cell_index]
            # Clear any existing text in the target cell.
            # (For simplicity, we set its text content by replacing its <a:txBody>.)
            for txBody in target_cell_element.findall(".//a:txBody", cell._tc.nsmap):
                target_cell_element.remove(txBody)
            from pptx.oxml.text import CT_TextBody

            new_txBody = CT_TextBody()
            new_txBody.text = str(item)
            target_cell_element.append(new_txBody)
        # Append the new row element to the table.
        table._tbl.append(new_row_element)
    # (A full implementation would also adjust row heights, etc.)
