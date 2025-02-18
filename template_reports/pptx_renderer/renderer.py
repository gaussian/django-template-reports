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
    Render the PPTX template at template_path using the provided context and save to output_path.

    - Non-table text boxes are processed in "normal" mode (which joins list values using a delimiter).
    - Table cells are processed in "table" mode; if a placeholder returns a list, the cell is expanded into multiple rows.

    After processing, if any errors were recorded:
      - If any error indicates a permission problem, a PermissionDeniedException is raised.
      - Otherwise, an UnresolvedTagError is raised.

    Args:
      template_path (str): Path to the input PPTX template.
      context (dict): The template context.
      output_path (str): Path to save the rendered PPTX.
      request_user: The user object for permission checking.
      check_permissions (bool): Whether to enforce permission checks.

    Returns:
      The output_path if rendering succeeds.

    Raises:
      PermissionDeniedException, UnresolvedTagError, UnterminatedTagException.
    """
    prs = Presentation(template_path)
    errors = []
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
