import unittest
import pendulum

from textual_datepicker import DateSelect


class AttributeCases(unittest.TestCase):
    def test_empty_attributes(self):
        with self.assertRaises(TypeError) as context:
            DateSelect()

        self.assertTrue(
            "missing 1 required positional argument" in str(context.exception)
        )

    def test_required_attributes(self):
        date_select = DateSelect(picker_mount="#some_mount_point")
        assert isinstance(date_select, DateSelect)

    def test_default_format(self):
        date_select = DateSelect(picker_mount="#some_mount_point")
        assert date_select.format == "YYYY-MM-DD"

    def test_given_format(self):
        date_select = DateSelect(picker_mount="#some_mount_point", format="MM/DD/YYYY")
        assert date_select.format == "MM/DD/YYYY"

    def test_given_placeholder(self):
        date_select = DateSelect(picker_mount="#some_mount_point",
                                 placeholder="please select")
        assert date_select.placeholder == "please select"

    def test_given_date(self):
        date_select = DateSelect(picker_mount="#some_mount_point",
                                 date=pendulum.tomorrow())
        assert date_select.date == pendulum.tomorrow()
        assert date_select.value == pendulum.tomorrow()
