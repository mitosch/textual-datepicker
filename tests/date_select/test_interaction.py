import pytest
import pendulum

from textual.app import App, ComposeResult
from textual.containers import Container

from textual_datepicker import DateSelect


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
        assert len(app.query("DateSelect")) == 1
        assert len(app.query("DatePicker")) == 1
        date_select = app.query_one("DateSelect")
        # date_picker = app.query_one("DatePicker")
        assert date_select.date is None

        await pilot.press("tab")
        assert date_select.dialog.display is False

        await pilot.press("enter")
        assert date_select.dialog.display is True
        assert date_select.date is None

        await pilot.press("enter")
        assert date_select.dialog.display is False
        assert date_select.date == pendulum.today(tz="UTC")
