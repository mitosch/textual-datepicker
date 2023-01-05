from __future__ import annotations

import calendar
import pendulum

from textual.app import ComposeResult
from textual.widget import Widget, RenderableType, events
from textual.widgets import Static, Button
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual.css.query import NoMatches
from textual.message import Message

from textual import log


class DatePickerControl(Button, can_focus=True):
    DEFAULT_CSS = """
    DatePickerControl {
        height: 1;
        width: 3;
        max-width: 3;
        border: none;
    }
    DatePickerControl.-active,
    DatePickerControl:hover {
        border: none;
    }
    """
    pass


class DatePickerHeader(Static, can_focus=True):
    DEFAULT_CSS = """
    DatePickerHeader {
        width: 20;
        content-align: center top;
        text-align: center;
        text-style: bold;
    }
    DatePickerHeader:focus {
        text-style: bold reverse;
    }
    """

    # the date format to use for displaying the label
    format = "MMMM\nYYYY"

    def __init__(
        self,
        date: pendulum.DateTime,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.renderable = date.format(self.format)

    def update(self, date: pendulum.DateTime) -> None:
        super().update(date.format(self.format))

    def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            self.emit_no_wait(self.Selected(self))

    class Selected(Message):
        """The DatePickerHeader was selected."""
        pass


class WeekheaderContainer(Horizontal):
    pass


class MonthSelectionContainer(Vertical):
    pass


class DateSelectionContainer(Vertical):
    pass


class DayContainer(Horizontal):
    pass


class MonthContainer(Horizontal):
    def compose(self) -> ComposeResult:
        for m in range(1, 13):
            yield MonthLabel(m)


class MonthLabel(Widget, can_focus=True):
    def __init__(
        self,
        month: 0,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.month = month

    def render(self) -> RenderableType:
        return calendar.month_abbr[self.month]

    def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            self.emit_no_wait(self.Selected(self, self.month))

    class Selected(Message):
        """A month was selected."""

        def __init__(self, sender: MonthLabel, month: int) -> None:
            self.month = month
            super().__init__(sender)


class WeekheaderLabel(Static):
    pass


class DayLabel(Widget):
    def __init__(
        self,
        label: str,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ):
        super().__init__(name=name, id=id, classes=classes)
        self.label = label
        if int(label) == 0:
            self.can_focus = False
        else:
            self.can_focus = True
            self.add_class("--day")

    @property
    def day(self):
        if int(self.label) > 0:
            return int(self.label)
        return None

    def render(self) -> RenderableType:
        if int(self.label) == 0:
            output = "  "
        else:
            output = f"{self.label:>2}"

        return output

    def update(self, label: str) -> None:
        if int(label) == 0:
            if self.has_focus:
                self.emit_no_wait(self.FocusLost(self, int(self.label)))
            self.can_focus = False
            self.remove_class("--day")
        else:
            self.can_focus = True
            self.add_class("--day")
        self.label = label
        self.refresh(layout=True)

    async def on_focus(self, _event: events.Focus) -> None:
        await self.emit(self.Focused(self))

    def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            self.emit_no_wait(self.Selected(self, int(self.label)))

    def on_click(self, event: events.MouseEvent) -> None:
        if int(self.label) == 0:
            return

        self.emit_no_wait(self.Selected(self, int(self.label)))

    class Focused(Message):
        pass

    class FocusLost(Message):
        """A focusable day have become an unfocusable one."""

        def __init__(self, sender: DayLabel, day: int) -> None:
            # day: the old day which had the focus
            self.day = day
            super().__init__(sender)

    class Selected(Message):
        """A day was selected."""

        def __init__(self, sender: DayLabel, day: int) -> None:
            self.day = day
            super().__init__(sender)


class DatePicker(Widget):
    DEFAULT_CSS = """
    DatePicker {
        width: 26;
        height: 15;
        box-sizing: content-box;
        padding: 0 1;
    }
    DatePicker .header {
        height: 2;
    }
    DatePicker WeekheaderContainer,
    DatePicker DayContainer {
        layout: grid;
        grid-size: 7;
        grid-columns: 2;
        grid-rows: 1;
        grid-gutter: 1 2;
    }
    DatePicker WeekheaderContainer {
        height: 2;
    }
    DatePicker WeekheaderLabel {
        color: $text-muted;
    }
    DatePicker DayLabel {
        content-align: right top;
    }
    DatePicker DayLabel:focus {
        text-style: bold reverse;
    }
    DatePicker DayLabel.--today {
        color: $secondary-lighten-1;
        text-style: bold;
    }
    DatePicker DayLabel.--today:focus {
        text-style: bold reverse;
    }
    DatePicker DayLabel.--day:hover {
        background: $surface-lighten-2;
    }

    DatePicker MonthSelectionContainer {
        display: none;
    }
    DatePicker MonthContainer {
        layout: grid;
        grid-size: 3;
        grid-columns: 7;
        grid-rows: 2;
        grid-gutter: 1 2;
        padding-top: 1;
    }
    DatePicker MonthLabel {
        height: 100%;
        content-align: center top;
    }
    DatePicker MonthLabel:focus {
        text-style: bold reverse;
    }
    """

    # label on the top with month and year
    month_label = Static("", classes="month")

    # the displayed month (always the first of the month)
    date = reactive(pendulum.today().start_of("month"))

    # The index of the focused day as int (including empty leading days)
    focused: int | None

    # The selected date (on enter, click)
    selected_date: pendulum.DateTime | None

    # Container with all the selectable days
    day_container = None

    # A target widget where to send the message for a selected date
    target: Widget | None = None

    # Type of selection: date (monthly calendar), month (12 months), year (list)
    selection_type: reactive[str] = reactive("date")

    @property
    def focused_day(self) -> DayLabel | None:
        try:
            return self.query_one("DayLabel:focus")
        except NoMatches:
            return None

    def compose(self) -> ComposeResult:
        self.day_container = DayContainer(*self._build_day_widgets())
        yield Vertical(
            Horizontal(
                DatePickerControl("<", classes="left"),
                DatePickerHeader(date=self.date),
                DatePickerControl(">", classes="right"),
                classes="header"
            ),
            MonthSelectionContainer(
                MonthContainer(),
            ),
            DateSelectionContainer(
                WeekheaderContainer(*self._build_weekheader_widgets()),
                self.day_container
            )
        )

    def watch_date(self, _old_date, _new_date) -> None:
        self._update_month_label()
        self._update_day_widgets()

    def watch_selection_type(self, selection_type) -> None:
        log("******===> selection type: ", selection_type)
        if selection_type == "date":
            self.query_one(DateSelectionContainer).display = True
            self.query_one(MonthSelectionContainer).display = False
            self.query_one(DatePickerHeader).format = "MMMM\nYYYY"
            self.query_one(DatePickerHeader).update(self.date)
        elif selection_type == "month":
            self.query_one(DateSelectionContainer).display = False
            self.query_one(MonthSelectionContainer).display = True
            self.query_one(DatePickerHeader).format = "YYYY"
            self.query_one(DatePickerHeader).update(self.date)
            for month in self.query(MonthLabel):
                if month.month == self.date.month:
                    month.focus()
                    break

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.has_class("left"):
            self._prev_month()
        if event.button.has_class("right"):
            self._next_month()

    def on_day_label_focused(self, event: DayLabel.Focused) -> None:
        self.focused = self.day_container.children.index(event.sender)

    def on_day_label_focus_lost(self, event: DayLabel.FocusLost) -> None:
        """The previous focused day is no longer focusable on this position.
        If it was at the end of a month, set it to end of the 4th row, there
        is always a focusable day. Otherwise to the first on the 2nd row.
        """
        if event.day >= 28:
            self.day_container.children[27].focus()
        else:
            self.day_container.children[7].focus()

    def on_day_label_selected(self, event: DayLabel.Selected) -> None:
        self.selected_date = pendulum.datetime(
            self.date.year, self.date.month, event.day
        )

        self.emit_no_wait(self.Selected(self, self.selected_date))

        if self.target is not None:
            self.target.post_message_no_wait(self.Selected(self, self.selected_date))

    def on_date_picker_header_selected(self, event: DatePickerHeader.Selected) -> None:
        log("DatePickerHeader selected")
        self.selection_type = "month"

    def on_key(self, event: events.Key) -> None:
        if event.key == "pageup":
            event.prevent_default()
            self._prev_month()
        if event.key == "pagedown":
            event.prevent_default()
            self._next_month()
        if event.key == "left":
            event.prevent_default()
            self._handle_left()
        if event.key == "right":
            event.prevent_default()
            self._handle_right()
        if event.key == "down":
            event.prevent_default()
            self._handle_down()
        if event.key == "up":
            event.prevent_default()
            self._handle_up()
        if event.key == "home":
            event.prevent_default()
            self._handle_home()

    def _prev_month(self) -> None:
        self._move_month(-1)

    def _next_month(self) -> None:
        self._move_month(1)

    def _move_month(self, month_count: int) -> None:
        self.date = pendulum.datetime(
            self.date.year, self.date.month, 1).add(months=month_count)

    def _handle_left(self) -> None:
        focused_day = self.focused_day
        if focused_day is None:
            return

        nudging = False

        if focused_day.day == 1:
            nudging = True
        elif self.focused % 7 == 0:
            nudging = True

        if nudging:
            self._prev_month()
        else:
            self.day_container.children[self.focused - 1].focus()

    def _handle_right(self) -> None:
        focused_day = self.focused_day
        if focused_day is None:
            return

        nudging = False

        if self.focused % 7 == 6:
            nudging = True
        elif focused_day.day >= 28:
            # 28 could be last day of month, check for an empty day at next index.
            # index can't be out of range because there is always an empty day
            # at the right
            if self.day_container.children[self.focused + 1].day is None:
                nudging = True

        if nudging:
            self._next_month()
        else:
            self.day_container.children[self.focused + 1].focus()

    def _handle_down(self) -> None:
        focused_day = self.focused_day
        if focused_day is None:
            return

        nudging = False

        if focused_day.day >= 28 - 7:
            # from 21, we always can go to 28. only check for days after.
            try:
                # if day at index +7 is None, it's nudging
                # also if there is no index
                if self.day_container.children[self.focused + 7].day is None:
                    nudging = True
            except IndexError:
                nudging = True

        if nudging:
            return

        self.day_container.children[self.focused + 7].focus()

    def _handle_up(self) -> None:
        focused_day = self.focused_day
        if focused_day is None:
            return

        nudging = False

        if focused_day.day <= 7:
            nudging = True

        if nudging:
            return

        self.day_container.children[self.focused - 7].focus()

    def _handle_home(self) -> None:
        self.date = pendulum.today()
        self.query_one("DayLabel.--today").focus()

    def _update_month_label(self) -> None:
        try:
            header = self.query_one(DatePickerHeader)
        except NoMatches:
            # not yet composed, do nothing
            return
        header.update(date=self.date)

    def _build_weekheader_widgets(self) -> [WeekheaderLabel]:
        widgets = []
        weekdays = calendar.weekheader(2).split(" ")
        for day in weekdays:
            widgets.append(WeekheaderLabel(day))

        return widgets

    def _build_day_widgets(self) -> [DayLabel]:
        day_widgets = []
        today_day = self._today_in_month()

        days = calendar.monthcalendar(year=self.date.year, month=self.date.month)
        days = [day for week in days for day in week]

        for idx in range(42):
            # 42: 6 rows with 7 days
            if idx < len(days):
                if today_day == days[idx]:
                    classes = "--today"
                else:
                    classes = ""
                day_widgets.append(DayLabel(days[idx], classes=classes))
            else:
                day_widgets.append(DayLabel(0))

        return day_widgets

    def _update_day_widgets(self) -> None:
        today_day = self._today_in_month()

        days = calendar.monthcalendar(year=self.date.year, month=self.date.month)
        days = [day for week in days for day in week]

        for idx, day_label in enumerate(self.query("DayContainer DayLabel")):
            if idx < len(days):
                day_label.set_class(today_day == days[idx], "--today")
                day_label.update(days[idx])
            else:
                day_label.update(0)

    def _today_in_month(self) -> int | None:
        """Returns todays day, if today is in the current month (self.date).
        None otherwise."""

        today = pendulum.today()
        if today.year == self.date.year and today.month == self.date.month:
            return today.day

        return None

    class Selected(Message):
        """A date was selected."""

        def __init__(self, sender: DatePicker, date: pendulum.DateTime) -> None:
            self.date = date
            super().__init__(sender)
