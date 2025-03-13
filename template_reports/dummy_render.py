import random
import sys
import argparse
import datetime

from template_reports.office_renderer import render_pptx


# Dummy context objects for testing.
class DummyUser:
    def __init__(self, name, email, cohort, impact, is_active=True):
        self.name = name
        self.email = email
        self.cohort = cohort
        self.is_active = is_active
        self.impact = impact
        self.rating = random.randint(1, 5)

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
                attrs = key.split("__")
                current = item
                for attr in attrs:
                    current = getattr(current, attr, None)
                    if current is None:
                        break
                if str(current) != str(val):
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
    def __init__(self, name, users):
        self.name = name
        self.users = users  # This will be a DummyQuerySet

    def __str__(self):
        return self.name


class DummyRequestUser:
    def has_perm(self, perm, obj):
        # For testing, deny permission if the object's name contains "Carol".
        if hasattr(obj, "name") and "Carol" in obj.name:
            return False
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Render a PPTX template with dummy context (including dummy queryset for Django models)."
    )
    parser.add_argument("input_file", help="Path to input PPTX template")
    parser.add_argument(
        "--output",
        "-o",
        help="Path to output PPTX file (defaults to same directory as input, named dummy_test_output.pptx)",
    )
    args = parser.parse_args()

    input_file = args.input_file
    output_file = (
        args.output
        if args.output
        else input_file.rsplit("/", 1)[0] + "/dummy_test_output.pptx"
    )

    # Create dummy objects.
    cohort = DummyCohort(name="Cohort A")
    user = DummyUser(
        name="Alice", email="alice@example.com", cohort=cohort, impact=10, is_active=True
    )
    bob = DummyUser(
        name="Bob", email="bob@test.com", cohort=cohort, impact=20, is_active=True
    )
    carol = DummyUser(
        name="Carol", email="carol@test.com", cohort=cohort, impact=30, is_active=False
    )
    todd = DummyUser(
        name="Todd", email="todd@test.com", cohort=cohort, impact=40, is_active=True
    )
    users_qs = DummyQuerySet([bob, carol, todd])
    program = DummyProgram(name="Test Program", users=users_qs)
    dummy_date = datetime.date(2020, 1, 15)

    # Construct the context.
    context = {
        "user": user,
        "program": program,
        "date": dummy_date,
    }

    print("Context:")
    print("  user:", user.name, user.email)
    print("  cohort:", cohort.name)
    print("  program:", program.name)
    print("  program.users (dummy queryset):", users_qs)
    print("  date:", dummy_date)

    # Create a dummy request user for permission checking.
    request_user = DummyRequestUser()

    rendered, errors = render_pptx(
        input_file,
        context,
        output_file,
        perm_user=None,
    )
    if rendered:
        print("Rendered PPTX saved to:", rendered)


if __name__ == "__main__":
    main()
