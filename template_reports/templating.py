import re


def resolve_tag_expression(expr, context):
    """
    Given an expression string (e.g., "user.email", "program.users[is_active==True].email",
    or even "user__relations__subjects[user__relation__type=='m'].email"),
    resolve it against the provided context dictionary.

    Returns the final value (which might be a list, a string, or any value).
    """
    segments = split_expression(expr)
    if not segments:
        return ""
    # The first segment should be a key in the context:
    current = context.get(segments[0])
    if current is None:
        return ""
    for seg in segments[1:]:
        current = resolve_segment(current, seg)
        if current is None:
            return ""
    return current


def split_expression(expr):
    """
    Split the expression into segments by periods, but ignore periods inside square brackets.
    For example, the expression
       program.users[is_active==True].email
    will be split into:
       ['program', 'users[is_active==True]', 'email']
    """
    return re.split(r"\.(?![^\[]*\])", expr)


def resolve_segment(current, segment):
    """
    Resolve one segment of the expression. A segment is of the form:
      attribute_name[optional_filter]
    where attribute_name can contain double-underscores (for nested attribute lookup).
    The optional filter (inside [ and ]) is a comma‑separated list of conditions.
    """
    # The regular expression matches an attribute (letters, digits, underscore, and optional __ stuff)
    # and an optional filter part in brackets.
    m = re.match(r"(\w+(?:__\w+)*)(\[(.*?)\])?$", segment)
    if not m:
        return None
    attr_name = m.group(1)  # e.g., "users" or "user__relations__subjects"
    filter_expr = m.group(3)  # e.g., "is_active==True" or "user__relation__type=='m'"

    # Retrieve the attribute from current.
    # If current is a list, then apply the lookup to each element.
    if isinstance(current, (list, tuple)):
        values = [get_nested_attr(item, attr_name) for item in current]
    else:
        values = get_nested_attr(current, attr_name)

    # If a filter is specified, then filter the resulting collection.
    if filter_expr:
        # Make sure we’re dealing with a list.
        if not isinstance(values, list):
            values = [values]
        # Conditions are separated by commas.
        conditions = [cond.strip() for cond in filter_expr.split(",")]
        values = [
            item
            for item in values
            if all(evaluate_condition(item, cond) for cond in conditions)
        ]
    return values


def get_nested_attr(obj, attr):
    """
    Retrieve an attribute from obj. If attr contains double underscores,
    treat that as a chain of lookups.
    For example, if attr is "cohort__name", this is equivalent to: getattr(obj, "cohort").name
    Works on both objects and dictionaries.
    """
    parts = attr.split("__")
    for part in parts:
        if obj is None:
            return None
        if isinstance(obj, dict):
            obj = obj.get(part)
        else:
            obj = getattr(obj, part, None)
        if callable(obj):
            try:
                obj = obj()
            except Exception:
                obj = None
    return obj


def evaluate_condition(item, condition):
    """
    Evaluate a condition string on the given item.
    The condition should be in the form:
         attribute==value   or   attribute=value
    Where attribute can be a chain with double underscores.
    For example: "is_active==True" or "user__relation__type=='m'"
    Only equality is supported in this simple example.
    """
    m = re.match(r"([\w__]+)\s*(==|=)\s*(.+)", condition)
    if not m:
        return False
    attr_chain, op, value_str = m.groups()
    expected_value = parse_value(value_str)
    actual_value = get_nested_attr(item, attr_chain)
    return actual_value == expected_value


def parse_value(val_str):
    """
    Parse a string value into a Python object.
    Tries booleans, integers, floats; strips quotes from strings.
    """
    val_str = val_str.strip()
    if val_str.lower() == "true":
        return True
    if val_str.lower() == "false":
        return False
    try:
        return int(val_str)
    except ValueError:
        pass
    try:
        return float(val_str)
    except ValueError:
        pass
    # Remove quotes if present.
    if (val_str.startswith('"') and val_str.endswith('"')) or (
        val_str.startswith("'") and val_str.endswith("'")
    ):
        return val_str[1:-1]
    return val_str


def process_text(text, context):
    """
    Process text containing template tags. Each occurrence of {{ ... }} is replaced by
    its evaluated value. Lists are joined with commas.
    """
    pattern = r"\{\{(.*?)\}\}"

    def replacer(match):
        expr = match.group(1).strip()
        value = resolve_tag_expression(expr, context)
        if isinstance(value, list):
            return ", ".join(str(item) for item in value if item is not None)
        elif value is None:
            return ""
        return str(value)

    return re.sub(pattern, replacer, text)
