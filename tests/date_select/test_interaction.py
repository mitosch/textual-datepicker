import pytest
import pendulum

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widget import events

from textual_datepicker import DateSelect, DatePicker


@pytest.mark.asyncio
async def test_open_close():
    """Focus select, open it, press enter to select and close."""
    class OpenDateSelectApp(App):
        def compose(self) -> ComposeResult:
            yield Container(
                DateSelect(picker_mount="#main_container"),
                id="main_container"
            )

    app = OpenDateSelectApp()
    async with app.run_test() as pilot:
        assert len(app.query(DateSelect)) == 1
        assert len(app.query(DatePicker)) == 1
        date_select = app.query_one("DateSelect")
        assert date_select.date is None

        await pilot.press("tab")
        assert date_select.dialog.display is False

        await pilot.press("enter")
        assert date_select.dialog.display is True
        assert date_select.date is None

        await pilot.press("enter")
        assert date_select.dialog.display is False
        assert date_select.date == pendulum.today(tz="UTC")

@pytest.mark.asyncio
async def test_given_placeholder():
    class OpenDateSelectApp(App):
        def compose(self) -> ComposeResult:
            yield Container(
                DateSelect(picker_mount="#main_container", placeholder="please select"),
                id="main_container"
            )

    app = OpenDateSelectApp()
    async with app.run_test() as pilot:
        date_select = app.query_one(DateSelect)
        assert date_select.date is None
        assert "please select" in date_select.render()

@pytest.mark.asyncio
async def test_given_date():
    default_format = "YYYY-MM-DD"
    date = pendulum.datetime(2022, 4, 1, 0, 0, 0)

    class OpenDateSelectApp(App):
        def compose(self) -> ComposeResult:
            yield Container(
                DateSelect(picker_mount="#main_container", date=date),
                id="main_container"
            )

    app = OpenDateSelectApp()
    async with app.run_test() as pilot:
        date_select = app.query_one(DateSelect)
        assert date_select.date is not None
        assert date_select.date == date
        assert date.format(default_format) in date_select.render()

@pytest.mark.asyncio
async def test_given_format():
    format = "MM/DD/YYYY"
    date = pendulum.datetime(2022, 4, 1, 0, 0, 0)

    class OpenDateSelectApp(App):
        def compose(self) -> ComposeResult:
            yield Container(
                DateSelect(picker_mount="#main_container", date=date, format=format),
                id="main_container"
            )

    app = OpenDateSelectApp()
    async with app.run_test() as pilot:
        date_select = app.query_one(DateSelect)
        assert date_select.date is not None
        assert date_select.date == date
        assert date.format(format) in date_select.render()

@pytest.mark.asyncio
async def test_date_selection():
    default_format = "YYYY-MM-DD"
    tomorrow = pendulum.tomorrow(tz="UTC")
    tomorrow_str = tomorrow.format(default_format)

    class OpenDateSelectApp(App):
        def compose(self) -> ComposeResult:
            yield Container(
                DateSelect(picker_mount="#main_container"),
                id="main_container"
            )

    app = OpenDateSelectApp()
    async with app.run_test() as pilot:
        date_select = app.query_one(DateSelect)
        assert date_select.date is None
        assert tomorrow_str not in date_select.render()
        assert date_select.dialog.display is False

        await pilot.press("tab")
        await pilot.press("enter")
        assert date_select.dialog.display is True
        assert app.focused.day == pendulum.today().day

        await pilot.press("right")
        await pilot.press("enter")
        assert date_select.date == tomorrow
        assert tomorrow_str in date_select.render()

@pytest.mark.asyncio
async def test_given_this_month_focuses_today():
    default_format = "YYYY-MM-DD"
    today = pendulum.today(tz="UTC")

    class OpenDateSelectApp(App):
        def compose(self) -> ComposeResult:
            yield Container(
                DateSelect(picker_mount="#main_container", date=today),
                id="main_container"
            )

    app = OpenDateSelectApp()
    async with app.run_test() as pilot:
        await pilot.press("tab")
        await pilot.press("enter")

        assert app.focused == app.query("DatePicker DayLabel.--today").first()

@pytest.mark.asyncio
async def test_given_last_month_focuses_first():
    default_format = "YYYY-MM-DD"
    old_month = pendulum.today().add(months=-2)

    class OpenDateSelectApp(App):
        def compose(self) -> ComposeResult:
            yield Container(
                DateSelect(picker_mount="#main_container", date=old_month),
                id="main_container"
            )

    app = OpenDateSelectApp()
    async with app.run_test() as pilot:
        await pilot.press("tab")
        await pilot.press("enter")

        assert app.focused.day == old_month.day

@pytest.mark.asyncio
async def test_text_cut_for_small_inputs():
    date = pendulum.datetime(2022, 4, 1, 0, 0, 0)

    class OpenDateSelectApp(App):
        DEFAULT_CSS = """
        DateSelect {
            width: 12;
        }
        """
        def compose(self) -> ComposeResult:
            yield Container(
                DateSelect(picker_mount="#main_container", date=date),
                id="main_container"
            )

    app = OpenDateSelectApp()
    async with app.run_test() as pilot:
        date_select = app.query_one(DateSelect)
        await pilot.press("tab")
        await pilot.press("enter")

        assert date.format("YYYY") in date_select.render()

@pytest.mark.asyncio
async def test_text_sign_bug():
    date = pendulum.datetime(2022, 4, 1, 0, 0, 0)

    class OpenDateSelectApp(App):
        DEFAULT_CSS = """
        DateSelect {
            width: 5;
        }
        """
        def compose(self) -> ComposeResult:
            yield Container(
                DateSelect(picker_mount="#main_container"),
                id="main_container"
            )

    app = OpenDateSelectApp()
    async with app.run_test() as pilot:
        date_select = app.query_one(DateSelect)
        await pilot.press("tab")
        await pilot.press("enter")

        assert date_select.render()

@pytest.mark.asyncio
async def test_open_click():
    class OpenDateSelectApp(App):
        def compose(self) -> ComposeResult:
            yield Container(
                DateSelect(picker_mount="#main_container"),
                id="main_container"
            )

    app = OpenDateSelectApp()

    async with app.run_test() as pilot:
        date_select = app.query_one(DateSelect)
        click = events.Click(sender=date_select, x=0, y=0, screen_x=0, screen_y=0,
                             delta_x=0, delta_y=0, button=1,
                             shift=False, meta=False, ctrl=False)
        await app.post_message(click)
        await pilot.press("tab")
