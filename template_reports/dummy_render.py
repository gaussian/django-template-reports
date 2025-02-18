import sys
import argparse
import datetime
from template_reports.pptx_renderer.renderer import render_pptx


# Dummy context objects for testing.
class DummyUser:
    def __init__(self, name, email, cohort, is_active=True):
        self.name = name
        self.email = email
        self.cohort = cohort
        self.is_active = is_active

    def __str__(self):
        return self.name


class DummyCohort:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class DummyQuerySet:
    """A simple dummy QuerySet to simulate Django's queryset behavior."""

    def __init__(self, items):
        self.items = items

    def all(self):
        return self

    def filter(self, **kwargs):
        result = []
        for item in self.items:
            match = True
            for key, val in kwargs.items():
                # Support nested lookups via __.
                attrs = key.split("__")
                current = item
                for attr in attrs:
                    current = getattr(current, attr, None)
                    if current is None:
                        break
                if current != val:
                    match = False
                    break
            if match:
                result.append(item)
        return DummyQuerySet(result)

    def __iter__(self):
        return iter(self.items)

    def __repr__(self):
        return repr(self.items)


class DummyProgram:
    def __init__(self, users):
        self.users = users  # This will be a DummyQuerySet

    def __str__(self):
        return ", ".join(str(u) for u in self.users)


def main():
    parser = argparse.ArgumentParser(
        description="Render a PPTX template with dummy context (including dummy queryset for Django models)."
    )
    parser.add_argument("input_file", help="Path to input PPTX template")
    parser.add_argument(
        "--output",
        "-o",
        help="Path to output PPTX file (defaults to same directory as input, named output_test.pptx)",
    )
    args = parser.parse_args()

    input_file = args.input_file
    output_file = (
        args.output if args.output else input_file.rsplit("/", 1)[0] + "/output_test.pptx"
    )

    # Create dummy objects.
    cohort = DummyCohort(name="Cohort A")
    user = DummyUser(
        name="Alice", email="alice@example.com", cohort=cohort, is_active=True
    )
    bob = DummyUser(name="Bob", email="bob@test.com", cohort=cohort, is_active=True)
    carol = DummyUser(
        name="Carol", email="carol@test.com", cohort=cohort, is_active=False
    )
    # Simulate a Django QuerySet for program.users.
    users_qs = DummyQuerySet([bob, carol])
    program = DummyProgram(users=users_qs)
    dummy_date = datetime.date(2020, 1, 15)

    # Construct the context dictionary.
    context = {
        "user": user,
        "program": program,
        "date": dummy_date,
    }

    print("Context:")
    print("  user:", user.name, user.email)
    print("  cohort:", cohort.name)
    print("  program.users (dummy queryset):", users_qs)
    print("  date:", dummy_date)

    try:
        rendered = render_pptx(
            input_file, context, output_file, request_user=user, check_permissions=False
        )
        print("Rendered PPTX saved to:", rendered)
    except Exception as e:
        print("Error during rendering:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
