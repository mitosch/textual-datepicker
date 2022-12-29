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

# from textual import log


class MonthControl(Button, can_focus=True):
    DEFAULT_CSS = """
    MonthControl {
        height: 1;
        border: none;
    }
    MonthControl.-active,
    MonthControl:hover {
        border: none;
    }
    """
    pass


class WeekdayContainer(Horizontal):
    pass


class DayContainer(Horizontal):
    pass


class WeekdayLabel(Static):
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


class DatePickerDialog(Widget):
    """The dialog/menu which opens below the DateSelect."""

    DEFAULT_CSS = """
    DatePickerDialog {
        layer: dialog;
        background: $boost;
        width: 30;
        height: 17;
        border: tall $accent;
        display: none;
    }
    """

    # The DatePicker mounted in this dialog.
    date_picker = None

    # A target where to send the message for a selected date
    target = None

    def compose(self) -> ComposeResult:
        self.date_picker = DatePicker()
        self.date_picker.target = self.target
        yield Vertical(self.date_picker)

    def on_date_picker_selected(self, event: DatePicker.Selected) -> None:
        self.display = False

        if self.target is not None:
            self.target.focus()


class DateSelect(Widget, can_focus=True):
    """A select widget which opens the DatePicker and displays the selected date."""

    # TODO: implement given date

    DEFAULT_CSS = """
    DateSelect {
      background: $boost;
      color: $text;
      padding: 0 2;
      border: tall $background;
      height: 1;
      min-height: 1;
    }
    DateSelect:focus {
      border: tall $accent;
    }
    """

    # The value displayed in the select (which is the date)
    # value = reactive("", layout=True, init=False)

    # Date of the month which shall be shown when opening the dialog
    date: reactive[pendulum.DateTime | None] = reactive(None)

    def __init__(
        self,
        picker_mount: str,
        date: pendulum.DateTime | str | None = None,
        format: str = "YYYY-MM-DD",
        placeholder: str = "",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.picker_mount = picker_mount
        self.placeholder = placeholder
        self.format = format

        # DatePickerDialog widget
        self.dialog = None

    @property
    def value(self) -> pendulum.DateTime:
        """Value of the current date."""
        return self.date

    def render(self) -> str:
        chevron = "\u25bc"
        width = self.content_size.width
        text_space = width - 2

        if not self.date:
            text = self.placeholder
        else:
            text = self.date.format(self.format)

        if len(text) > text_space:
            text = text[0:text_space]

        text = f"{text:{text_space}} {chevron}"

        return text

    def on_mount(self) -> None:
        if self.dialog is None:
            self.dialog = DatePickerDialog()
            self.dialog.target = self
            self.app.query_one(self.picker_mount).mount(self.dialog)

    def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            self._show_date_picker()

    def on_date_picker_selected(self, event: DatePicker.Selected) -> None:
        self.date = event.date

    def _show_date_picker(self) -> None:
        mnt_widget = self.app.query_one(self.picker_mount)
        self.dialog.display = True

        # calculate offset of DateSelect and apply it to DatePickerDialog
        self.dialog.offset = self.region.offset - mnt_widget.content_region.offset

        # move down 3 (height of input)
        # TODO: should be dynamic for smaller inputs
        self.dialog.offset = (
            self.dialog.offset.x, self.dialog.offset.y + 3)

        # TODO: this could not work by a given default
        if self.date is not None:
            for day in self.dialog.query("DayLabel.--day"):
                if day.day == self.date.day:
                    day.focus()
                    break
        else:
            try:
                self.dialog.query_one("DayLabel.--today").focus()
            except NoMatches:
                self.dialog.query("DayLabel.--day").first().focus()


class DatePicker(Widget):
    DEFAULT_CSS = """
    DatePicker {
        width: 26;
        height: 15;
        box-sizing: content-box;
        /*border: solid $panel;*/
        padding: 0 1;
    }
    DatePicker .header {
        height: 2;
    }
    DatePicker .header .month {
        width: 20;
        content-align: center top;
        text-align: center;
        text-style: bold;
    }
    DatePicker WeekdayContainer,
    DatePicker DayContainer {
        layout: grid;
        grid-size: 7;
        grid-columns: 2;
        grid-rows: 1;
        grid-gutter: 1 2;
    }
    DatePicker MonthControl {
        width: 3;
        max-width: 3;
    }
    DatePicker WeekdayContainer {
        height: 2;
    }
    DatePicker WeekdayLabel {
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
    """

    # label on the top with month and year
    month_label = Static("", classes="month")

    # the displayed month (always the first of the month)
    date = reactive(pendulum.today().start_of("month"))

    # The index of the focused day as int (including empty leading days)
    focused: reactive[int | None] = reactive(None)

    # The selected date (on enter, click)
    # selected_date: reactive[pendulum.DateTime | None] = reactive(None)
    selected_date: None

    # Container with all the selectable days
    day_container = None

    # A target widget where to send the message for a selected date
    target: Widget | None = None

    @property
    def focused_day(self) -> DayLabel | None:
        if self.focused is None:
            return None

        if self.focused >= 0:
            container = self.day_container
            return container.children[self.focused]

        return None

    def compose(self) -> ComposeResult:
        self.day_container = DayContainer(*self._build_day_widgets())
        yield Vertical(
            Horizontal(
                MonthControl("<", classes="left"),
                Static(self._build_month_label(), classes="month"),
                MonthControl(">", classes="right"),
                classes="header"
            ),
            WeekdayContainer(*self._build_weekday_widgets()),
            self.day_container
        )

    def watch_date(self, _old_date, _new_date) -> None:
        self._update_month_label()
        self._update_day_widgets()

    def watch_focused(self, index) -> None:
        # FIXME: fast forward could blink between two dates. possible race-condition
        if index is None:
            return
        container = self.day_container
        container.children[index].focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.has_class("left"):
            self._prev_month()
        if event.button.has_class("right"):
            self._next_month()

    def on_day_label_focused(self, event: DayLabel.Focused) -> None:
        container = self.day_container
        self.focused = container.children.index(event.sender)

    def on_day_label_focus_lost(self, event: DayLabel.FocusLost) -> None:
        """The previous focused day is no longer on this position.
        Try to find a better one: Same day as before, or last one.
        """
        # OPTIMIZE: should focus first or last, not the exact one
        nearest = None
        for day_label in self.query("DayContainer DayLabel"):
            if int(day_label.label) > 0:
                nearest = day_label
            if int(day_label.label) == event.day:
                break
        nearest.focus()

    def on_day_label_selected(self, event: DayLabel.Selected) -> None:
        self.selected_date = pendulum.datetime(
            self.date.year, self.date.month, event.day
        )

        self.emit_no_wait(self.Selected(self, self.selected_date))

        if self.target is not None:
            self.target.post_message_no_wait(self.Selected(self, self.selected_date))

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
        focused_day = self._ensure_focused_day()
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
            self.focused -= 1

    def _handle_right(self) -> None:
        focused_day = self._ensure_focused_day()
        if focused_day is None:
            return

        nudging = False

        if self.focused % 7 == 6:
            nudging = True
        elif focused_day.day >= 28:
            # 28 could be last day of month, check for an empty day at next index.
            # index can't be out of range because there is always an empty day
            # at the right
            container = self.day_container
            if container.children[self.focused + 1].day is None:
                nudging = True

        if nudging:
            self._next_month()
        else:
            self.focused += 1

    def _handle_down(self) -> None:
        focused_day = self._ensure_focused_day()
        if focused_day is None:
            return

        nudging = False

        if focused_day.day >= 28 - 7:
            # from 21, we always can go to 28. only check for days after.
            container = self.day_container
            try:
                # if day at index +7 is None, it's nudging
                # also if there is no index
                if container.children[self.focused + 7].day is None:
                    nudging = True
            except IndexError:
                nudging = True

        if nudging:
            return

        self.focused += 7

    def _handle_up(self) -> None:
        focused_day = self._ensure_focused_day()
        if focused_day is None:
            return

        nudging = False

        if focused_day.day <= 7:
            nudging = True

        if nudging:
            return

        self.focused -= 7

    def _handle_home(self) -> None:
        self.date = pendulum.today()
        self.query_one("DayLabel.--today").focus()

    def _ensure_focused_day(self) -> DayLabel | None:
        # for performance purposes, only query once
        focused_day = self.focused_day
        if self.focused is None:
            return None
        if focused_day is None:
            return None

        return focused_day

    def _update_month_label(self) -> None:
        try:
            month_label = self.query_one("Static.month")
        except NoMatches:
            # not yet composed, do nothing
            return
        month_label.update(self._build_month_label())

    def _build_month_label(self) -> str:
        month = self.date.format("MMMM")
        year = self.date.format("YYYY")
        return f"{month}\n{year}"

    def _build_weekday_widgets(self) -> [WeekdayLabel]:
        widgets = []
        weekdays = calendar.weekheader(2).split(" ")
        for day in weekdays:
            widgets.append(WeekdayLabel(day))

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
