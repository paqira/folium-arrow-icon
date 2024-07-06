# Simple arrow (vector/quiver) icon for folium

[![PyPI - Version](https://img.shields.io/pypi/v/folium-arrow-icon?logo=PyPI&label=PyPI)](https://pypi.org/project/folium-arrow-icon/)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?logo=Python&label=Python&tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fpaqira%2Ffolium-arrow-icon%2Fmain%2Fpyproject.toml)
[![Read the Docs](https://img.shields.io/readthedocs/folium-arrow-icon?logo=readthedocs)](https://folium-arrow-icon.readthedocs.io)
![PyPI - License](https://img.shields.io/pypi/l/folium-arrow-icon)

This package provides simple arrow (vector/quiver) icon for the [folium](https://pypi.org/project/folium/) package.

The size of the icon does not change as zoom level changes.
It is useful for displaying vector field.

```python
import math

import folium
from folium_arrow_icon import ArrowIcon

m = folium.Map(
    location=[40.78322, -73.96551],
    zoom_start=14,
)

folium.Marker(
    [40.78322, -73.96551],
    # by length and angle
    icon=ArrowIcon(100, math.pi / 2)
).add_to(m)

folium.Marker(
    [40.78322, -73.96551],
    # by components of latitude and longitude directions
    icon=ArrowIcon.from_comp([100, -50])
).add_to(m)

m.save("sample.html")
```

See [document](http://folium-arrow-icon.readthedocs.io/) for more example.

You can install `folium-arrow-icon` from PyPI:

```shell
pip install folium-arrow-icon
```

## Licence

MIT
