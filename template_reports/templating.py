import re


def resolve_tag_expression(expr, context):
    """
    Resolve a template tag expression (e.g. "user.email" or "program.users[is_active==True].email")
    against a context dictionary.
    """
    segments = split_expression(expr)
    if not segments:
        return ""
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
    Split the expression into segments by periods but ignore dots inside square brackets.
    For example: "program.users[is_active==True].email" becomes:
      ["program", "users[is_active==True]", "email"]
    """
    return re.split(r"\.(?![^\[]*\])", expr)


def resolve_segment(current, segment):
    """
    Resolve a segment that might include an optional filter.
    For example: "users[is_active==True]" will perform a lookup on "users" then filter.
    """
    m = re.match(r"(\w+(?:__\w+)*)(\[(.*?)\])?$", segment)
    if not m:
        return None
    attr_name = m.group(1)
    filter_expr = m.group(3)

    # Apply the attribute lookup. If current is a list, map the lookup.
    if isinstance(current, (list, tuple)):
        values = [get_nested_attr(item, attr_name) for item in current]
    else:
        values = get_nested_attr(current, attr_name)

    if filter_expr:
        # Ensure we have a list for filtering.
        if not isinstance(values, list):
            values = [values]
        conditions = [cond.strip() for cond in filter_expr.split(",")]
        values = [
            item
            for item in values
            if all(evaluate_condition(item, cond) for cond in conditions)
        ]
    return values


def get_nested_attr(obj, attr):
    """
    Retrieve an attribute via a dot (or double-underscore) chain.
    For example, "profile__phone" is equivalent to: getattr(obj, 'profile').phone
    Works for both objects and dictionaries.
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
    Evaluate a condition of the form attribute==value (or attribute=value) on the item.
    Supports double-underscore chains in the attribute.
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
    Convert a string representation into a Python value.
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
