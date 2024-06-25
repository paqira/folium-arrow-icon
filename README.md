# Simple arrow (vector/quiver) icon for folium

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

See document for more example.

You can install `folium-arrow-icon` from PyPI:

```shell
pip install folium-arrow-icon
```

## Licence

MIT
