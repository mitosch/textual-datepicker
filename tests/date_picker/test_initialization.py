import unittest
import pendulum

from textual_datepicker import DatePicker


class AttributeCases(unittest.TestCase):
    def test_empty_attributes(self):
        date_picker = DatePicker()
        assert isinstance(date_picker, DatePicker)

    def test_date_is_this_month_by_default(self):
        date_picker = DatePicker()
        assert date_picker.date == pendulum.today().start_of("month")
