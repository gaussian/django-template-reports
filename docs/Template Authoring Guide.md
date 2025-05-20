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

---

## 3. Lists and Table Expansion

When a placeholder by itself resolves to a list, the engine will repeat the row (in Excel) or slide (in PPTX) for each item. Inside that row/slide you can refer to each item’s properties:
```  
{{ orders }}                • if `orders` is a list, rows/slides repeat  
{{ orders.id }}             • shows order ID for each item  
{{ orders.total | .2f }}    • shows total with two decimals  
```

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
If `time_of_day` is “Morning”, this becomes `{{ user.greet(Morning) }}` which is processed as if that were the placeholder you wrote.

---

## 8. Images in Templates

To insert an image from a URL, start a text box (or cell) with `%image% ` followed by the URL:
```  
%image% https://example.com/logo.png  
```
The engine downloads and embeds the image in place.

---

## 9. Best Practices

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
| Math           | `{{ price * 1.2 }}`                 | 240.00                         |
| Filter         | `{{ items[type="A"].count }}`       | [count1, count2, …]            |
| Image          | `%image% https://…/logo.png`        | (embedded logo)                |

With this guide, you’ll be able to build dynamic, data-driven slides and spreadsheets—no code required!# Template Authoring Guide

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

---

## 3. Lists and Table Expansion

When a placeholder by itself resolves to a list, the engine will repeat the row (in Excel) or slide (in PPTX) for each item. Inside that row/slide you can refer to each item’s properties:
```  
{{ orders }}                • if `orders` is a list, rows/slides repeat  
{{ orders.id }}             • shows order ID for each item  
{{ orders.total | .2f }}    • shows total with two decimals  
```

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

---

## 9. Best Practices

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
| Math           | `{{ price * 1.2 }}`                 | 240.00                         |
| Filter         | `{{ items[type="A"].count }}`       | [count1, count2, …]            |
| Image          | `%image% https://…/logo.png`        | (embedded logo)                |

With this guide, you’ll be able to build dynamic, data-driven slides and spreadsheets—no code required!