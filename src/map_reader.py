"""
This module contains classes and methods relevant to reading/parsing/displaying
OpenStreetMap (OSM) data

Author: Chris Harris
"""

import requests

class MapReader:
    """
    Class handles accessing OpenStreetMap data and returning relevant road/street data
    """
    def __init__(self):
        self._overpass_url = "http://overpass-api.de/api/interpreter"

    def _get_highway_data_from_bbox(self, south_latitude: float, west_longitude: float,
                                    north_latitude: float, east_longitude: float) -> dict:
        """
        Return all OSM nodes, ways and relations within the box defined by the latitudes/longitudes.
        """
        roi = f"({south_latitude}, {west_longitude}, {north_latitude}, {east_longitude})"
        feature = "highway"

        query = f"""
        [out:json];
        (
        node["{feature}"]
            {roi};
        way["{feature}"]
            {roi};
        relation["{feature}"]
            {roi};
        )
        (._;>;);
        out center;
        """
        return self._query_overpass(query)

    def _query_overpass(self, query: str, timeout=30) -> dict:
        """
        Send query to Overpass API and return json formatted result
        """
        response = requests.get(self._overpass_url, params={"data": query}, timeout=timeout)
        response_data = response.json()
        return response_data
