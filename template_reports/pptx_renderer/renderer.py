from pptx import Presentation
from .merger import merge_runs_in_paragraph
from .expander import process_table_cell
from .exceptions import (
    UnterminatedTagException,
    PermissionDeniedException,
    UnresolvedTagError,
)
from ..templating import process_text


def render_pptx(
    template_path, context, output_path, request_user=None, check_permissions=True
):
    """
    Open the PPTX template at template_path, process all text placeholders using our templating logic,
    and save the rendered presentation to output_path.

    In non-table text boxes, process in "normal" mode.
    In table cells, process in "table" mode.

    After processing, if any errors were recorded, raise a PermissionDeniedException if any
    error indicates a permission problem, or otherwise raise an UnresolvedTagError.
    """
    prs = Presentation(template_path)
    errors = []
    # Process text frames (normal mode).
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text_frame"):
                for paragraph in shape.text_frame.paragraphs:
                    merge_runs_in_paragraph(
                        paragraph,
                        context,
                        errors,
                        request_user,
                        check_permissions,
                        mode="normal",
                    )
            # Process tables.
            if hasattr(shape, "has_table") and shape.has_table:
                for row in shape.table.rows:
                    for cell in row.cells:
                        process_table_cell(
                            cell, context, errors, request_user, check_permissions
                        )
    if errors:
        perm_errors = [e for e in errors if "Permission denied" in e]
        if perm_errors:
            raise PermissionDeniedException(perm_errors)
        else:
            print(
                "The following template tags could not be resolved or failed permission checks:"
            )
            for tag in set(errors):
                print(" -", tag)
            raise UnresolvedTagError(
                "One or more template tags could not be resolved; output file not created."
            )
    prs.save(output_path)
    return output_path
