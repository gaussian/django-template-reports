import re
from copy import deepcopy
from pptx.oxml.text import CT_TextBody
from .merger import merge_runs_in_paragraph
from ..templating import process_text


def process_table_cell(cell, context, errors, request_user, check_permissions):
    """
    If the cell is pure placeholder => "table" mode. If that yields a list, expand the table.
    Otherwise => normal run merging for partial placeholders.
    """
    cell_text = cell.text.strip()
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
        # Mixed or partial placeholders => normal mode merging
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
    Add a new row for each item beyond the first. The original row gets the first item.
    The second row, etc., get the subsequent items. This code is an unsupported hack in python-pptx.
    """
    if not items:
        cell.text = ""
        return

    # Original cell: first item
    cell.text = str(items[0])

    # Identify row/ table from the cell
    row_element = cell._tc.getparent()  # <a:tr>
    table_element = row_element.getparent()  # <a:tbl>
    row_cells = list(row_element)
    cell_index = row_cells.index(cell._tc)

    for item in items[1:]:
        new_row_element = deepcopy(row_element)
        new_cells = list(new_row_element)
        # Fix the text in the same column
        if cell_index < len(new_cells):
            target_cell_element = new_cells[cell_index]
            # Remove existing <a:txBody> elements
            for txBody in target_cell_element.findall(".//a:txBody", cell._tc.nsmap):
                target_cell_element.remove(txBody)

            new_txBody = CT_TextBody()
            new_txBody.text = str(item)
            target_cell_element.append(new_txBody)
        table_element.append(new_row_element)
