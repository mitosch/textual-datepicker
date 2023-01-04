import unittest
import pendulum

from textual_datepicker import DatePicker, DateSelect


class DatePickerAttributeCases(unittest.TestCase):
    def test_empty_attributes(self):
        date_picker = DatePicker()
        assert isinstance(date_picker, DatePicker)

    def test_date_is_this_month_by_default(self):
        date_picker = DatePicker()
        assert date_picker.date == pendulum.today().start_of("month")


class DateSelectAttributeCases(unittest.TestCase):
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
