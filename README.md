# Simple Vector (arrow) Icon for folium

This package provides simple vector (arrow) icon for the [folium](https://pypi.org/project/folium/) package.

The size of the icon does not change as zoom level changes.
It is useful for displaying vector field.

```python
import math

import folium
from folium_vector_icon import VectorIcon

m = folium.Map(
    location=[40.78322, -73.96551],
    zoom_start=14,
)

folium.Marker(
    [40.78322, -73.96551],
    # by length and angle
    icon=VectorIcon(100, math.pi / 2)
).add_to(m)

folium.Marker(
    [40.78322, -73.96551],
    # by components of latitude and longitude directions
    icon=VectorIcon.from_comp([100, -50])
).add_to(m)

m.save("sample.html")
```

See xxx for more example.

This is available from PyPI:

```shell
pip install folium_vector_icon
```

## Licence

MIT
