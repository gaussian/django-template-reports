# Django Template Reports

A Django library for generating parameterized PowerPoint (PPTX) reports from template files.

## Overview

Django Template Reports provides a powerful templating system that allows you to create reusable report templates with dynamic content placeholders. These templates can be populated with data from your Django models, enabling seamless report generation without hard-coding the report structure.

The library separates presentation design from data logic. This separation of concerns makes it easy to maintain and update reports over time.

## Key Features

- **Dynamic Template System**: Use expression syntax (`{{ variable }}`) to insert model data into PowerPoint slides
- **Data Manipulation**: Apply filters, access nested properties, and format values like dates
- **Permission Controls**: Security-aware templating that respects user access permissions
- **Complex Elements Support**: Handles text boxes, dynamically expanding tables, and data-driven charts
- **Admin Integration**: Built-in Django admin views to manage report definitions and generation history
- **Reusable Architecture**: Designed as a modular Django app that integrates with your existing projects
