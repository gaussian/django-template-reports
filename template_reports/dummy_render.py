import os
import sys
import argparse
import datetime
from template_reports.pptx_renderer import render_pptx


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


class DummyProgram:
    def __init__(self, users):
        self.users = users

    def __str__(self):
        return ", ".join(str(u) for u in self.users)


def main():
    parser = argparse.ArgumentParser(
        description="Render a PPTX template with dummy context."
    )
    parser.add_argument(
        "input_file",
        help="Path to the input PPTX template file (e.g., raw_templates/template.pptx)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Path to the output PPTX file (default: same directory as input, named output_test.pptx)",
    )
    args = parser.parse_args()

    # Resolve the input file's absolute path.
    input_file = os.path.abspath(args.input_file)
    if not os.path.exists(input_file):
        print(f"Input file '{input_file}' does not exist.")
        sys.exit(1)

    # Default output file: same directory as input, file name "output_test.pptx"
    if args.output:
        output_file = os.path.abspath(args.output)
    else:
        output_file = os.path.join(os.path.dirname(input_file), "output_test.pptx")

    # Create dummy objects.
    cohort = DummyCohort(name="Cohort A")
    dummy_date = datetime.date(2020, 1, 15)
    user = DummyUser(
        name="Alice", email="alice@example.com", cohort=cohort, is_active=True
    )
    bob = DummyUser(name="Bob", email="bob@example.com", cohort=cohort, is_active=True)
    carol = DummyUser(
        name="Carol", email="carol@example.com", cohort=cohort, is_active=False
    )
    program = DummyProgram(users=[bob, carol])

    # Construct a context dictionary.
    context = {
        "user": user,
        "program": program,
        "date": dummy_date,
    }

    print("Using input file:", input_file)
    print("Using output file:", output_file)

    try:
        rendered_file = render_pptx(
            template_path=input_file,
            context=context,
            output_path=output_file,
            request_user=user,
            check_permissions=False,  # Set to True if you want to enforce permission checks.
        )
        print(f"Rendered PPTX saved to: {rendered_file}")
    except Exception as e:
        print("Error during rendering:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
