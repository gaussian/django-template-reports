import re


def resolve_tag_expression(expr, context):
    """
    Given an expression string (e.g., "user.name", "program.users[is_active=True].email"),
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
    For example: "program.users[is_active=True].email" becomes:
       ['program', 'users[is_active=True]', 'email']
    """
    return re.split(r"\.(?![^\[]*\])", expr)


def resolve_segment(current, segment):
    """
    Resolve one segment of the expression. A segment is of the form:
       attribute_name[optional_filter]
    where attribute_name can contain double-underscores for nested lookup.
    The optional filter (inside [ and ]) is a comma-separated list of conditions.
    """
    m = re.match(r"(\w+(?:__\w+)*)(\[(.*?)\])?$", segment)
    if not m:
        return None
    attr_name = m.group(1)
    filter_expr = m.group(3)

    if isinstance(current, (list, tuple)):
        values = [get_nested_attr(item, attr_name) for item in current]
    else:
        values = get_nested_attr(current, attr_name)

    if filter_expr:
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
    Retrieve an attribute from obj. If attr contains double underscores,
    treat it as a chain of lookups. Works on both objects and dictionaries.
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
    The condition should be in the form: attribute==value (or attribute=value).
    Only equality is supported.
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
    if (val_str.startswith('"') and val_str.endswith('"')) or (
        val_str.startswith("'") and val_str.endswith("'")
    ):
        return val_str[1:-1]
    return val_str


def has_view_permission(obj, request_user):
    """
    Check if request_user has permission to view obj.
    Instead of importing Django’s Model, we check for a _meta attribute.
    If obj does not appear to be a Django model instance, return True.
    """
    if not hasattr(obj, "_meta"):
        return True
    return request_user.has_perm("view", obj)


def process_text(text, context, errors=None, request_user=None, check_permissions=True):
    """
    Process text containing template tags. Each occurrence of {{ ... }} is replaced by
    its evaluated value. Supports a pipe operator for date formatting.
    If a tag cannot be resolved (or fails permission), its expression is added to errors.

    Tag examples:
      - {{ user.name }}
      - {{ date | "MMM dd, YYYY" }}

    :param text: The input text with tags.
    :param context: The context dictionary.
    :param errors: A list to accumulate unresolved tag expressions.
    :param request_user: The user to use for permission checking.
    :param check_permissions: Whether to check permissions (default True).
    """
    pattern = r"\{\{(.*?)\}\}"

    def replacer(match):
        raw_expr = match.group(1).strip()
        # Check for pipe operator for formatting (e.g., date | "MMM dd, YYYY")
        if "|" in raw_expr:
            value_expr, fmt_str = raw_expr.split("|", 1)
            value_expr = value_expr.strip()
            fmt_str = fmt_str.strip()
            # Remove surrounding quotes from the format string if present.
            if (fmt_str.startswith('"') and fmt_str.endswith('"')) or (
                fmt_str.startswith("'") and fmt_str.endswith("'")
            ):
                fmt_str = fmt_str[1:-1]
            value = resolve_tag_expression(value_expr, context)
            # If the value supports strftime, format it.
            if hasattr(value, "strftime"):
                try:
                    value = value.strftime(fmt_str)
                except Exception:
                    if errors is not None:
                        errors.append(raw_expr)
                    return ""
            else:
                # Not a date/datetime? Simply convert to string.
                value = str(value)
        else:
            value = resolve_tag_expression(raw_expr, context)

        if check_permissions and request_user is not None:
            if isinstance(value, list):
                permitted = [
                    item for item in value if has_view_permission(item, request_user)
                ]
                if not permitted:
                    if errors is not None:
                        errors.append(raw_expr)
                    return ""
                value = permitted
            else:
                if not has_view_permission(value, request_user):
                    if errors is not None:
                        errors.append(raw_expr)
                    return ""

        if value == "" or value is None:
            if errors is not None:
                errors.append(raw_expr)
            return ""
        if isinstance(value, list):
            return ", ".join(str(item) for item in value if item is not None)
        return str(value)

    return re.sub(pattern, replacer, text)
