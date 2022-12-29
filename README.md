# Textual: DatePicker

A DatePicker widget for [textual](https://github.com/Textualize/textual). It can be used standalone or with a DateSelect opening the dialog.

**NOTE:** This package is in a concept phase. It is already testable and running.
A working version (>= 0.1.0) will be released in January 2023. I'm happy
to receive feedback.

DateSelect with DatePicker example:

![DateSelect with DatePicker](https://user-images.githubusercontent.com/922559/209936036-22ecb6e9-0d14-4336-b360-67c37e2ccbda.png)

## Usage

```python
from textual_datepicker import DateSelect

DateSelect(
  placeholder="please select",
  format="YYYY-MM-DD",
  picker_mount="#main_container"
)
```

## Installation

```bash
pip install textual-datepicker
```

Requires textual 0.6.0 or later.

## Limitations

This textual widget is in early stage and has some limitations:

* Mouse interaction is not yet implemented.
* The default given date will probably not working at this time. Planned for 0.1.0.
* It can only open below, not above: Make sure to reserve space below for the dialog.
* It needs a specific mount point (`picker_mount`) where the dialog
  shall appear. This is needed because the container widget with the select
  itself could be too small. Maybe in future versions this will no longer be
  needed.
