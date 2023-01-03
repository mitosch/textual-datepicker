# Textual: DatePicker

A DatePicker widget for [textual](https://github.com/Textualize/textual). It can be used standalone or with a DateSelect opening the dialog.

DateSelect with DatePicker example:

![DateSelect with DatePicker](https://user-images.githubusercontent.com/922559/209947716-3ee53f74-4d98-4d9c-a261-afb84955d519.png)


## Usage

```python
from textual_datepicker import DateSelect

DateSelect(
  placeholder="please select",
  format="YYYY-MM-DD",
  picker_mount="#main_container"
)
```

Define an inital value:

```python
import pendulum
from textual_datepicker import DateSelect

DateSelect(
  placeholder="please select",
  format="YYYY-MM-DD",
  date=pendulum.parse("2023-02-14"),
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

* It can only open below, not above: Make sure to reserve space below for the dialog.
* It needs a specific mount point (`picker_mount`) where the dialog
  shall appear. This is needed because the container widget with the select
  itself could be too small. Maybe in future versions this will no longer be
  needed.
