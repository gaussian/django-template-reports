import re
from pptx import Presentation
from .templating import process_text


def render_pptx(template_path, context, output_path):
    """
    Open the PPTX template at `template_path`, process all text placeholders that contain
    template tags (e.g., "{{ user.email }}"), and save the rendered presentation to `output_path`.
    """
    prs = Presentation(template_path)
    for slide in prs.slides:
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    run.text = process_text(run.text, context)
    prs.save(output_path)
    return output_path
