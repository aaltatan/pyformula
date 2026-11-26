# Installation

pyformula needs **Python 3.12 or newer**.

=== "uv"

    ```bash
    uv add pyformula
    ```

=== "pip"

    ```bash
    pip install pyformula
    ```

Its only dependency is [pyvocabulary](https://pypi.org/project/pyvocabulary/), a small
package by the same author that provides the registry and JSON Schema helpers.

## Check it works

```python
from pyformula import Formula

double = Formula(lambda number: number * 2, name="double")

assert (double + 1)(20) == 41
```
