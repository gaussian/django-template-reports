# Django Template Reports

Django Template Reports is a Django application that turns PowerPoint (PPTX) and Excel (XLSX) files into reusable templates.  Placeholders inside those templates are resolved using your Django models so that you can generate polished reports without hard‑coding the layout.

## Key Features

* **PowerPoint and Excel rendering** – supply a PPTX or XLSX file and a context dictionary to produce a finished document.
* **Placeholder expressions** using ``{{ }}`` to access attributes, call methods, filter lists and perform math.
* **Formatting helpers** for dates, numbers and string casing (``upper``, ``lower``, ``title``).
* **Arithmetic operators** in expressions (``+``, ``-``, ``*``, ``/``).
* **Dynamic table and worksheet expansion** when a placeholder resolves to a list.
* **Chart support** where spreadsheet values inside charts contain placeholders.
* **Permission enforcement** – data is filtered based on ``perm_user``.
* **Admin integration** with a flow to choose a template, configure context and generate ``ReportRun`` records.  Generated files can be downloaded individually or as a ZIP archive.
* **Configurable filenames** using ``config.filename_template`` in ``ReportDefinition``.
* **Global context** injection for values that should always be available.
* **Context extraction** to inspect templates and determine which context keys are required.
* **Image placeholders** – shapes or cells starting with ``%imagesqueeze%`` or ``%image%`` are replaced by an image downloaded from the provided URL.

## Codebase Overview

``template_reports/`` contains the library:

* ``models/`` – base classes ``ReportDefinition`` and ``ReportRun`` plus utilities for file storage.
* ``admin/`` – Django admin classes and views used to generate reports and download them in bulk.
* ``office_renderer/`` – logic for rendering PPTX and XLSX files.  This handles text boxes, tables, charts, worksheets and the `%image%`/`%imagesqueeze%` directives.
* ``templating/`` – the template engine responsible for parsing and evaluating expressions.
* ``templates/`` and ``raw_templates/`` – the admin templates and example Office templates.
* ``tests/`` – the test suite.

Start by looking at ``ReportDefinition`` in ``models/base.py`` and the functions in ``office_renderer`` to see how a file is rendered.  The templating package is standalone and can be read independently if you want to learn how placeholders are parsed.

## Writing Templates

Template files are just normal PowerPoint or Excel documents.  No coding or macros are required—just type plain text placeholders where you want dynamic information to appear.

1. **Design your layout.** Build the slides or workbook exactly as you would for a static report.
2. **Insert placeholders.** Anywhere you would type text you can instead type a placeholder wrapped in `{{` and `}}`:
   * `{{ user.name }}` – insert a simple value from the context.
   * `{{ user.profile__email }}` – read nested attributes using `.` or `__`.
   * `{{ users[is_active=True].email }}` – pick a specific item from a list.
   * `{{ amount * 1.15 }}` – perform calculations.
   * `{{ price | .2f }}` or `{{ name | upper }}` – apply formatting filters.
3. **Repeat rows or slides for lists.** If a placeholder by itself resolves to a list, extra rows (or slides) will be created so that each item appears separately.  This is how you build tables from querysets.
4. **Add images.** To include an image from a URL, create a text box or cell that starts with `%image%` or `%imagesqueeze%` followed by the address:
   `%image% https://example.com/logo.png`
   `%imagesqueeze% https://example.com/logo.png`
   The former keeps the image's aspect ratio while fitting it inside the shape. The latter squeezes the image to exactly fill the shape.
5. **Save the file** and register it in the Django admin as a report template.

You can experiment with the example files in `template_reports/raw_templates` to see common patterns.  Remember that all placeholders are plain text—avoid formulas or punctuation that might confuse the parser.

Chart data sheets can also contain placeholders so your graphs update automatically.

## Learning More

After trying the example templates in ``raw_templates/`` explore the ``tests/`` directory to see many usage patterns.  The test files demonstrate complex placeholders, permission checks and the new image replacement behaviour.

