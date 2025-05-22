# Looping in PowerPoint Templates

In PowerPoint templates, you can use loop directives to repeat slides for each item in a collection. This is useful for creating reports with repetitive sections, such as user profiles, product information, or any other data that follows the same structure for multiple items.

## Basic Loop Syntax

To create a loop in your PowerPoint template:

1. Add a shape with text `%loop variable in collection%` to mark the start of the loop
2. Add a shape with text `%endloop%` to mark the end of the loop
3. In the slides between these markers, use `{{ variable }}` to reference the current item

For example, to create slides for each user in a list of users:

```
%loop user in users%           • On the first slide of the loop
... slides with {{ user.name }}, {{ user.email }}, etc.
%endloop%                      • On the last slide of the loop
```

## How Looping Works

- The slides between the loop start and end (inclusive) will be duplicated for each item in the collection
- For each duplicate set, the loop variable will be set to the current item in the collection
- You can reference the loop variable in any placeholders within the duplicated slides

## Example

If your context has:

```python
context = {
  "users": [
    {"name": "Alice", "email": "alice@example.com"},
    {"name": "Bob", "email": "bob@example.com"}
  ]
}
```

And your template has three slides:
1. First slide with `%loop user in users%`
2. Middle slide with `Name: {{ user.name }}, Email: {{ user.email }}`
3. Last slide with `%endloop%`

The result will be:
1. First slide with `%loop user in users%`
2. Middle slide with `Name: Alice, Email: alice@example.com`
3. Middle slide with `Name: Bob, Email: bob@example.com`
4. Last slide with `%endloop%`

## Rules and Limitations

- Loops cannot be nested (no loop inside another loop)
- A slide cannot have both loop start and loop end directives
- Each loop must have a matching endloop
- The collection must be iterable (list, tuple, etc.)