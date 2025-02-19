import unittest
import datetime
import re

# Import functions from our templating module.
from template_reports.templating.core import process_text
from template_reports.templating.formatting import convert_format
from template_reports.templating.parser import (
    resolve_tag_expression,
    split_expression,
    resolve_segment,
)
from template_reports.templating.resolver import (
    get_nested_attr,
    evaluate_condition,
    parse_value,
)
from template_reports.templating.permissions import (
    enforce_permissions,
    has_view_permission,
)

# ----- Dummy Classes for Testing -----


class DummyUser:
    def __init__(self, name, email, is_active=True):
        self.name = name
        self.email = email
        self.is_active = is_active
        # Simulate a Django object by adding _meta
        self._meta = True

    def __str__(self):
        return self.name


class DummyCohort:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class DummyRequestUser:
    """A dummy request user that approves everything except objects with 'deny' in their name."""

    def has_perm(self, perm, obj):
        if hasattr(obj, "name") and "deny" in obj.name.lower():
            return False
        return True


# For testing, we'll use a normal Python list to simulate program.users.
# (Our parser code should work on lists as well.)

# ----- Unit Test Class -----


class TestTemplatingCore(unittest.TestCase):
    def setUp(self):
        # Create a dummy cohort, users, and program context.
        self.cohort = DummyCohort("Cohort A")
        self.user1 = DummyUser("Alice", "alice@example.com", is_active=True)
        self.user2 = DummyUser("Bob", "bob@example.com", is_active=True)
        self.user3 = DummyUser("DenyUser", "deny@example.com", is_active=True)
        # program.users as a list (simulate queryset already converted to a list)
        self.program = {
            "users": [self.user1, self.user2, self.user3],
            "name": "Test Program",
        }
        self.now = datetime.datetime(2025, 2, 18, 12, 0, 0)
        self.context = {
            "user": self.user1,
            "program": self.program,
            "now": self.now,
            "date": datetime.date(2020, 1, 15),
        }
        # Use a dummy request user that denies permission on any object whose name contains "deny".
        self.request_user = DummyRequestUser()
        # We'll collect errors here.
        self.errors = []

    # --- Tests for Formatting & Pure Placeholders ---

    def test_pure_now_formatting_normal(self):
        # Pure placeholder for now in normal mode should format correctly.
        tpl = "{{ now | MMMM dd, YYYY }}"
        result = process_text(
            tpl,
            self.context,
            errors=self.errors,
            request_user=self.request_user,
            check_permissions=False,
            mode="normal",
        )
        # Expect the full month name since MMMM -> %B.
        expected = self.now.strftime("%B %d, %Y")
        self.assertEqual(result, expected)

    def test_pure_now_formatting_table(self):
        # Pure placeholder in table mode returns a string (if not list).
        tpl = "{{ now | MMMM dd, YYYY }}"
        result = process_text(
            tpl,
            self.context,
            errors=self.errors,
            request_user=self.request_user,
            check_permissions=False,
            mode="table",
        )
        expected = self.now.strftime("%B %d, %Y")
        self.assertEqual(result, expected)

    def test_pure_list_normal(self):
        # Pure placeholder that resolves to a list in normal mode
        tpl = "{{ program.users.email }}"
        # Since self.program["users"] is a list of DummyUser, and email is an attribute
        # Expect joined emails, but note that self.user3 should be filtered out by permission check.
        # However, here check_permissions is False.
        result = process_text(
            tpl,
            self.context,
            errors=self.errors,
            request_user=self.request_user,
            check_permissions=False,
            mode="normal",
        )
        expected = ", ".join(u.email for u in self.program["users"])
        self.assertEqual(result, expected)

    def test_pure_list_table(self):
        # Pure placeholder in table mode returns a list of strings.
        tpl = "{{ program.users.email }}"
        result = process_text(
            tpl,
            self.context,
            errors=self.errors,
            request_user=self.request_user,
            check_permissions=False,
            mode="table",
        )
        expected = [str(u.email) for u in self.program["users"]]
        self.assertEqual(result, expected)

    # --- Tests for Mixed Text ---

    def test_mixed_text_normal(self):
        # Mixed text with a placeholder that resolves to a list should join the list.
        tpl = "All emails: {{ program.users.email }} are active."
        result = process_text(
            tpl,
            self.context,
            errors=self.errors,
            request_user=self.request_user,
            check_permissions=False,
            mode="normal",
        )
        # Expected: "All emails: alice@example.com, bob@example.com, deny@example.com are active."
        expected = (
            f"All emails: {', '.join(u.email for u in self.program['users'])} are active."
        )
        self.assertEqual(result, expected)

    def test_mixed_text_table(self):
        # Mixed text in table mode: only one placeholder allowed. If it resolves to a list, should return a list.
        tpl = "User email: {{ program.users.email }}"
        result = process_text(
            tpl,
            self.context,
            errors=self.errors,
            request_user=self.request_user,
            check_permissions=False,
            mode="table",
        )
        # Expect a list with one entry per user.
        expected = [f"User email: {u.email}" for u in self.program["users"]]
        self.assertEqual(result, expected)

    # --- Test Permission Enforcement ---

    def test_permission_denied_in_pure(self):
        # In pure mode with check_permissions True, the dummy request user denies objects with "deny".
        tpl = "{{ program.users.email }}"
        # Now, with permission checking enabled, self.user3 ("DenyUser") should be filtered out.
        result = process_text(
            tpl,
            self.context,
            errors=self.errors,
            request_user=self.request_user,
            check_permissions=True,
            mode="normal",
        )
        # Expected: joined emails of user1 and user2 only.
        expected = ", ".join(u.email for u in [self.user1, self.user2])
        self.assertEqual(result, expected)
        # Also, errors should contain a permission error message.
        self.assertTrue(any("Permission denied" in e for e in self.errors))

    def test_permission_denied_in_mixed(self):
        tpl = "Emails: {{ program.users.email }}"
        result = process_text(
            tpl,
            self.context,
            errors=self.errors,
            request_user=self.request_user,
            check_permissions=True,
            mode="normal",
        )
        # Expected: "Emails: alice@example.com, bob@example.com" joined inline.
        expected = f"Emails: {', '.join(u.email for u in [self.user1, self.user2])}"
        self.assertEqual(result, expected)
        self.assertTrue(any("Permission denied" in e for e in self.errors))

    # --- Test Edge Cases ---

    def test_mixed_text_multiple_placeholders_table(self):
        tpl = "User: {{ user.name }} and Email: {{ user.email }}"
        with self.assertRaises(ValueError):
            process_text(
                tpl,
                self.context,
                errors=self.errors,
                request_user=self.request_user,
                check_permissions=False,
                mode="table",
            )

    def test_empty_placeholder(self):
        tpl = "Empty tag: {{   }}."
        result = process_text(
            tpl,
            self.context,
            errors=self.errors,
            request_user=self.request_user,
            check_permissions=False,
            mode="normal",
        )
        self.assertEqual(result, "Empty tag: .")
        self.assertTrue(len(self.errors) > 0, self.errors)

    def test_missing_key_in_context(self):
        tpl = "Missing: {{ non_existent }}."
        result = process_text(
            tpl,
            self.context,
            errors=self.errors,
            request_user=self.request_user,
            check_permissions=False,
            mode="normal",
        )
        self.assertEqual(result, "Missing: .")
        self.assertTrue(len(self.errors) == 0)

    def test_nested_lookup_with_function(self):
        # Dynamically add a callable attribute to user1.
        self.user1.get_display = lambda: self.user1.name.upper()
        self.context["user"] = self.user1
        tpl = "Display: {{ user.get_display }}"
        result = process_text(
            tpl,
            self.context,
            errors=self.errors,
            request_user=self.request_user,
            check_permissions=False,
            mode="normal",
        )
        self.assertEqual(result, "Display: ALICE")

    def test_filter_multiple_conditions(self):
        tpl = "{{ program.users[is_active=True, email=bob@example.com].email }}"
        result = process_text(
            tpl,
            self.context,
            errors=self.errors,
            request_user=self.request_user,
            check_permissions=False,
            mode="normal",
        )
        # The filtered list will join a single email into a string.
        self.assertEqual(result, self.user2.email)

    def test_all_permissions_denied(self):
        # Create a request user that denies permission for all objects.
        class DenyAllUser:
            def has_perm(self, perm, obj):
                return False

        denier = DenyAllUser()
        tpl = "{{ program.users.email }}"
        result = process_text(
            tpl,
            self.context,
            errors=self.errors,
            request_user=denier,
            check_permissions=True,
            mode="normal",
        )
        self.assertEqual(result, "")
        self.assertTrue(len(self.errors) > 0)

    def test_table_mode_with_single_value(self):
        self.context["value"] = 100
        tpl = "{{ value }}"
        result = process_text(
            tpl,
            self.context,
            errors=self.errors,
            request_user=self.request_user,
            check_permissions=False,
            mode="table",
        )
        self.assertEqual(result, "100")

    def test_table_mode_with_list_value(self):
        self.context["value"] = [100]
        tpl = "{{ value }}"
        result = process_text(
            tpl,
            self.context,
            errors=self.errors,
            request_user=self.request_user,
            check_permissions=False,
            mode="table",
        )
        self.assertEqual(result, ["100"])

    def test_non_date_formatting(self):
        # Test if formatting fails gracefully.
        tpl = "{{ now | RANDOM WORDS }}"
        result = process_text(
            tpl,
            self.context,
            errors=self.errors,
            request_user=self.request_user,
            check_permissions=False,
            mode="normal",
        )
        self.assertEqual(
            result, "RANDOM WORDS"
        )  # Should return empty string and record an error.

    def test_no_placeholder_mixed_text(self):
        tpl = "This text has no placeholders."
        result = process_text(
            tpl,
            self.context,
            errors=self.errors,
            request_user=self.request_user,
            check_permissions=False,
            mode="normal",
        )
        self.assertEqual(result, tpl)

    def test_now_in_mixed_text(self):
        tpl = "Date is {{ now | MMMM dd, YYYY }} and time is set."
        result = process_text(
            tpl,
            self.context,
            errors=self.errors,
            request_user=self.request_user,
            check_permissions=False,
            mode="normal",
        )
        expected_date = self.now.strftime("%B %d, %Y")
        expected = re.sub(r"\{\{.*?\}\}", expected_date, tpl)
        self.assertEqual(result, expected)

    def test_integer_resolution(self):
        self.context["count"] = 42
        tpl = "The count is {{ count }}"
        result = process_text(
            tpl,
            self.context,
            errors=self.errors,
            request_user=self.request_user,
            check_permissions=False,
            mode="normal",
        )
        self.assertEqual(result, "The count is 42")

    def test_float_resolution(self):
        self.context["price"] = 19.95
        tpl = "Price: {{ price }}"
        result = process_text(
            tpl,
            self.context,
            errors=self.errors,
            request_user=self.request_user,
            check_permissions=False,
            mode="normal",
        )
        self.assertEqual(result, "Price: 19.95")

    def test_table_mode_single_item(self):
        self.context["single_item"] = ["OnlyOne"]
        tpl = "{{ single_item }}"
        result = process_text(
            tpl,
            self.context,
            errors=self.errors,
            request_user=self.request_user,
            check_permissions=False,
            mode="table",
        )
        self.assertEqual(result, ["OnlyOne"])


if __name__ == "__main__":
    unittest.main()
