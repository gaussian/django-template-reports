# Template Authoring Guide

This guide helps you build PowerPoint (PPTX) or Excel (XLSX) files with dynamic placeholders. No coding required—just design your slides or worksheets, then insert simple tags to pull in data, apply formatting, perform calculations, and more.

---

## 1. Basic Placeholder Syntax

Wrap any placeholder in double curly braces:
```  
{{ variable_name }}  
```
At generation time, `variable_name` is looked up in the context you supply (e.g. a Django dict).

---

## 2. Accessing Attributes and Nested Data

If your context contains objects or dicts with attributes, use dots or double-underscores to dive in:
```  
{{ user.name }}             → “Alice”  
{{ user.profile__email }}    → “alice@example.com”  
{{ company.address.street }} → “123 Main St.”  
```

Add a Python snippet showing how the context dict provides data:
```python
context = {
  "user": {"name": "Alice", "profile": {"email": "alice@example.com"}},
  "company": {"address": {"street": "123 Main St."}},
  "orders": [{"id": 1, "total": 9.99}, {"id": 2, "total": 19.99}],
  "users": [
    {"email": "a@example.com"},
    {"email": "b@example.com"}
  ],
}
```

---

## 3. Lists and Table Expansion

When a placeholder by itself resolves to a list, the engine will repeat the row (in Excel) or slide (in PPTX) for each item. Inside that row/slide you can refer to each item’s properties:
```  
{{ orders }}                • if `orders` is a list, rows/slides repeat  
{{ orders.id }}             • shows order ID for each item  
{{ orders.total | .2f }}    • shows total with two decimals  
```

Add explanation of list property notation:
A dot after a list returns a new list of that property for every item. For example, if `users` is a list of user objects, then `{{ users.email }}` produces a list of all email addresses (e.g. [`a@example.com`, `b@example.com`]).

After the code example for section 3, add details on expansions:

**Table Row Expansion (PPTX Tables)**  
If a table cell contains exactly one placeholder and it resolves to a list:
1. The first item fills the original row.  
2. Any existing empty rows below are filled in order.  
3. If more items remain, new rows are cloned from the template row and appended.

**Excel Worksheet Expansion (XLSX)**  
Works the same way in Excel sheets: a cell that resolves to a list fills empty cells below in the same column, and adds rows if needed.

**Chart Data Expansion (PPTX Charts)**  
Placeholders in the embedded spreadsheet behind a PPTX chart also expand:
- Series names, categories, and data ranges can use placeholders.  
- If a series or category resolves to a list, the chart’s rows or columns grow to fit arbitrary-length data.  
- Headings in the first row or column expand similarly to show each item.

---

## 4. Filtering Lists

You can filter a list by conditions in square brackets:
```  
{{ users[is_active=True].email }}  
```
This outputs a list of email addresses only for active users. If you want to loop through the filtered list, use the filter-only tag as a standalone placeholder.

---

## 5. Mathematical Operations

You can do basic math right in your placeholder:
```  
{{ price * 1.15 }}           → adds 15% tax  
{{ quantity + 2 }}           → increases quantity by 2  
{{ total / count }}          → average  
```

---

## 6. Formatting with `|` (Pipe Operator)

Use `|` to apply formatting to dates, numbers, or strings.

### 6.1 Date & Time Formats  
Supported tokens (custom or strftime):
- MMMM → full month name (June)  
- MMM  → short month (Jun)  
- MM   → zero-padded month (06)  
- dd   → zero-padded day (01)  
- YYYY → year (2024)  
- %Y, %m, %d, %H, %M, %S, %p, etc.

Examples:
```  
{{ now | MMMM, dd, YYYY }}   → “June, 01, 2024”  
{{ now | %Y-%m-%d }}         → “2024-06-01”  
{{ now | %I:%M %p }}         → “01:30 PM”  
```

### 6.2 Numeric Formats  
Standard Python numeric formats:
- `.2f` → two decimal places (3.14)  
- `.0f` → no decimals (3)  
- `d` → integer  

Examples:
```  
{{ amount | .2f }}           → “123.45”  
{{ count | d }}              → “42”  
```

### 6.3 String Case  
- `upper`      → ALL CAPS  
- `lower`      → all lower  
- `capitalize` → First letter caps  
- `title`      → Title Case  

Examples:
```  
{{ name | upper }}           → “ALICE”  
{{ title | title }}          → “My Report Title”  
```

---

## 7. Nested Placeholders

You can embed one placeholder inside another using `$…$`. The inner tag is resolved first:
```  
{{ user.greet($time_of_day$) }}  
```
If `time_of_day` is “Morning”, this becomes `user.greet("Morning")`.

---

## 8. Images in Templates

To insert an image from a URL, start a text box (or cell) with `%image% ` followed by the URL:
```  
%image% https://example.com/logo.png  
```
The engine downloads and embeds the image in place.

Remember you can use the nested placeholders, so you could always do:
```  
%image% https://example.com/$cohort.id$.png  
```

---

## 9. Looping in PowerPoint

In PowerPoint templates, you can use special loop directives to repeat slides for items in a collection:

```
%loop user in users%           • First slide of loop section
... Content with {{ user.name }} etc.
%endloop%                      • Last slide of loop section
```

Slides between these markers (inclusive) are duplicated for each item in the collection.
Each duplicate gets the variable (`user` in this example) set to a different item.

See the separate [Looping in PowerPoint Templates.md](./Looping%20in%20PowerPoint%20Templates.md) guide for complete details.

---

## 10. Best Practices

1. **Design first**: Lay out your slide or sheet exactly as you want the final report to look.  
2. **Use plain text**: Avoid formulas or extra punctuation inside `{{ }}`.  
3. **Test early**: Start with a minimal context, generate a draft, and confirm placeholders resolve.  
4. **Check list rows**: Make sure repeating rows or slides align correctly when lists expand.  
5. **Escape braces**: If you need literal `{{` or `}}`, double them (e.g. `{{ '{{' }}`).

---

## Quick Reference

| Feature        | Syntax Example                      | Output                         |
|----------------|-------------------------------------|--------------------------------|
| Variable       | `{{ user.name }}`                   | Alice                          |
| Date Format    | `{{ now | MMMM dd, YYYY }}`         | June 01, 2024                  |
| Number Format  | `{{ total | .2f }}`                 | 123.45                         |
| Uppercase      | `{{ title | upper }}`               | REPORT TITLE                   |
| Length         | `{{ title | length }}`              | 12                             |
| Math           | `{{ price * 1.2 }}`                 | 240.00                         |
| Filter         | `{{ items[type="A"].count }}`       | [count1, count2, …]            |
| Loop (PPTX)    | `%loop user in users%`              | Repeats slides with user data  |
| Image          | `%image% https://…/logo.png`        | (embedded logo)                |

With this guide, you’ll be able to build dynamic, data-driven slides and spreadsheets—no code required!