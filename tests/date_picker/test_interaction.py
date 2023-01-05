import pytest
import pendulum
import asyncio

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widget import events
from rich.text import Text

from textual_datepicker import DatePicker


@pytest.mark.asyncio
async def test_month_control():
    class DatePickerApp(App):
        def compose(self) -> ComposeResult:
            yield Container(
                DatePicker(),
            )
    app = DatePickerApp()

    async with app.run_test() as pilot:
        assert len(app.query(DatePicker)) == 1
        date_picker = app.query_one(DatePicker)
        month_header = app.query_one("DatePicker DatePickerHeader")
        current_month = pendulum.today().start_of("month")
        current_month_str = current_month.format(month_header.format)
        assert month_header.renderable == Text(current_month_str)
        assert date_picker.date == current_month

        assert app.focused is None
        await pilot.press("tab")
        assert app.focused == app.query("DatePicker DatePickerControl").first()
        await pilot.press("enter")

        last_month = pendulum.today().add(months=-1)
        last_month_str = last_month.format(month_header.format)
        assert month_header.renderable == Text(last_month_str)

        await pilot.press("tab")
        assert app.focused == app.query("DatePicker DatePickerHeader").first()
        await pilot.press("tab")
        assert app.focused == app.query("DatePicker DatePickerControl").last()
        await pilot.press("enter")
        assert month_header.renderable == Text(current_month_str)
        await pilot.press("enter")

        next_month = pendulum.today().add(months=1)
        next_month_str = next_month.format(month_header.format)
        assert month_header.renderable == Text(next_month_str)


@pytest.mark.asyncio
async def test_month_control_one_year_back():
    class DatePickerApp(App):
        def compose(self) -> ComposeResult:
            yield Container(
                DatePicker(),
            )
    app = DatePickerApp()

    async with app.run_test() as pilot:
        month_header = app.query_one("DatePicker DatePickerHeader")
        date_picker = app.query_one(DatePicker)

        await pilot.press("tab")
        assert app.focused == app.query("DatePicker DatePickerControl").first()
        for month in range(1, 13):
            await pilot.press("enter")

        last_year = pendulum.today(tz="UTC").add(years=-1).start_of("month")
        last_year_str = last_year.format(month_header.format)
        assert month_header.renderable == Text(last_year_str)
        assert date_picker.date == last_year


@pytest.mark.asyncio
async def test_keys_pageup_pagedown_home():
    class DatePickerApp(App):
        def compose(self) -> ComposeResult:
            yield Container(
                DatePicker(),
            )
    app = DatePickerApp()

    async with app.run_test() as pilot:
        date_picker = app.query_one(DatePicker)
        current_month = pendulum.today().start_of("month")

        await pilot.press("tab")
        assert app.focused == app.query("DatePicker DatePickerControl").first()

        assert date_picker.date == current_month
        await pilot.press("pageup")
        assert date_picker.date == pendulum.today(
            tz="UTC").start_of("month").add(months=-1)

        await pilot.press("tab")
        await pilot.press("tab")
        await pilot.press("tab")
        assert app.focused == app.query("DatePicker DayLabel.--day").first()
        await pilot.press("pageup")
        assert date_picker.date == pendulum.today(
            tz="UTC").start_of("month").add(months=-2)

        await pilot.press("pagedown")
        await pilot.press("pagedown")
        assert date_picker.date == pendulum.today(tz="UTC").start_of("month")

        await pilot.press("pagedown")
        await pilot.press("pagedown")
        assert date_picker.date == pendulum.today(
            tz="UTC").start_of("month").add(months=2)

        await pilot.press("home")
        assert date_picker.date == pendulum.today()
        assert app.focused == app.query("DatePicker DayLabel.--today").first()


@pytest.mark.asyncio
async def test_keys_up_down_left_right():
    class DatePickerApp(App):
        def compose(self) -> ComposeResult:
            yield Container(
                DatePicker(),
            )
    app = DatePickerApp()

    async with app.run_test() as pilot:
        date_picker = app.query_one(DatePicker)
        month_header = app.query_one("DatePicker DatePickerHeader")

        aug22 = pendulum.datetime(2022, 8, 1, 0, 0, 0)
        date_picker.date = aug22
        aug22_str = aug22.format(month_header.format)
        assert month_header.renderable == Text(aug22_str)
        assert date_picker.date == aug22

        await pilot.press("tab")
        assert app.focused == app.query("DatePicker DatePickerControl").first()

        assert date_picker.date == aug22
        await pilot.press("up")
        await pilot.press("down")
        await pilot.press("left")
        await pilot.press("right")
        assert date_picker.date == aug22

        await pilot.press("tab")
        await pilot.press("tab")
        await pilot.press("tab")
        assert app.focused == app.query("DatePicker DayLabel.--day").first()
        assert app.focused.day == 1

        # navigate within month
        await pilot.press("right")
        await pilot.press("right")
        await pilot.press("right")
        assert app.focused.day == 4

        await pilot.press("down")
        assert app.focused.day == 11

        await pilot.press("left")
        await pilot.press("left")
        assert app.focused.day == 9

        await pilot.press("up")
        assert app.focused.day == 2

        # nudging
        await pilot.press("up")
        assert app.focused.day == 2
        await pilot.press("down")
        await pilot.press("down")
        await pilot.press("down")
        await pilot.press("down")
        assert app.focused.day == 30
        await pilot.press("down")
        assert app.focused.day == 30

        await pilot.press("left")
        assert app.focused.day == 29
        await pilot.press("left")
        assert app.focused.day == 25
        jul22 = aug22.add(months=-1)
        jul22_str = jul22.format(month_header.format)
        assert date_picker.date == jul22
        assert month_header.renderable == Text(jul22_str)

        await pilot.press("right")
        await pilot.press("right")
        await pilot.press("right")
        await pilot.press("right")
        await pilot.press("right")
        await pilot.press("right")
        await pilot.press("right")
        await asyncio.sleep(0.05)
        assert app.focused.day == 28
        assert date_picker.date == aug22
        assert month_header.renderable == Text(aug22_str)

        # nudging on last line with empty labels
        await pilot.press("left")
        await pilot.press("left")
        await pilot.press("left")
        await pilot.press("left")
        await pilot.press("down")
        await pilot.press("right")
        await asyncio.sleep(0.05)
        assert app.focused.day == 28
        sep22 = aug22.add(months=1)
        sep22_str = sep22.format(month_header.format)
        assert date_picker.date == sep22
        assert month_header.renderable == Text(sep22_str)

        # nudging on first line with empty labels
        await pilot.press("right")
        await pilot.press("up")
        await pilot.press("up")
        await pilot.press("up")
        await pilot.press("up")
        await pilot.press("left")
        await asyncio.sleep(0.05)
        assert app.focused.day == 4
        assert date_picker.date == aug22
        assert month_header.renderable == Text(aug22_str)


@pytest.mark.asyncio
async def test_down_nudging_by_index_error():
    class DatePickerApp(App):
        def compose(self) -> ComposeResult:
            yield Container(
                DatePicker(),
            )
    app = DatePickerApp()

    async with app.run_test() as pilot:
        date_picker = app.query_one(DatePicker)
        month_header = app.query_one("DatePicker DatePickerHeader")

        # a month with a day on the last line
        oct22 = pendulum.datetime(2022, 10, 1, 0, 0, 0)
        date_picker.date = oct22
        oct22_str = oct22.format(month_header.format)
        assert month_header.renderable == Text(oct22_str)
        assert date_picker.date == oct22

        # move to 31
        await pilot.press("tab")
        await pilot.press("tab")
        await pilot.press("tab")
        await pilot.press("tab")
        await pilot.press("down")
        await pilot.press("down")
        await pilot.press("down")
        await pilot.press("down")
        await pilot.press("left")
        await pilot.press("left")
        await pilot.press("left")
        await pilot.press("left")
        await pilot.press("left")
        await pilot.press("down")
        assert app.focused.day == 31
        # handle down with IndexError catched here:
        await pilot.press("down")
        assert app.focused.day == 31


@pytest.mark.asyncio
async def test_month_with_only_five_rows():
    class DatePickerApp(App):
        def compose(self) -> ComposeResult:
            feb23 = pendulum.datetime(2023, 2, 1, 0, 0, 0)
            date_picker = DatePicker()
            date_picker.date = feb23
            yield Container(
                date_picker,
            )
    app = DatePickerApp()

    async with app.run_test() as pilot:
        date_picker = app.query_one(DatePicker)
        month_header = app.query_one("DatePicker DatePickerHeader")

        # a month with five rows
        feb23 = pendulum.datetime(2023, 2, 1, 0, 0, 0)
        date_picker.date = feb23
        feb23_str = feb23.format(month_header.format)
        assert month_header.renderable == Text(feb23_str)
        assert date_picker.date == feb23
        await pilot.press("tab")


@pytest.mark.asyncio
async def test_day_click():
    """A simple click simulation, which does not really work, but should not break."""
    class DatePickerApp(App):
        def compose(self) -> ComposeResult:
            yield Container(
                DatePicker(),
            )
    app = DatePickerApp()

    async with app.run_test() as pilot:
        first_day_label = app.query("DatePicker DayLabel").first()
        first_day = app.query("DatePicker DayLabel.--day").first()
        click = events.Click(sender=first_day, x=0, y=0, screen_x=0, screen_y=0,
                             delta_x=0, delta_y=0, button=1,
                             shift=False, meta=False, ctrl=False)
        await first_day_label.post_message(click)
        await first_day.post_message(click)
        await pilot.press("tab")
