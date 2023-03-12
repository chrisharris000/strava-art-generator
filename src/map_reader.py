"""
This module contains classes and methods relevant to reading/parsing/displaying
OpenStreetMap (OSM) data

Author: Chris Harris
"""

import matplotlib.pyplot as plt
import numpy as np
import requests

class MapReader:
    """
    Class handles accessing OpenStreetMap data and returning relevant road/street data
    """
    def __init__(self):
        self._overpass_url = "http://overpass-api.de/api/interpreter"
        self._step_size = 10

    def get_highway_data_from_bbox(self, south_latitude: float, west_longitude: float,
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
        );
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

    def plot_response_data(self, response_data: dict) -> None:
        """
        Plot the lat/long of each node, nodes in ways and nodes in relations
        """
        lat_lon = self._get_lat_lon(response_data)
        latitudes, longitudes = lat_lon[:, 0], lat_lon[:, 1]

        plt.plot(longitudes, latitudes, "o")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.axis("equal")
        plt.show()

    def _get_lat_lon(self, response_data: dict) -> np.array:
        """
        Get the lat/lon of each node, nodes in ways and nodes in relations
        """
        coords = []

        for element in response_data["elements"]:
            if element["type"] == "node":
                lat = element["lat"]
                lon = element["lon"]
                coords.append((lat, lon))

            if "center" in element:
                lat = element["center"]["lat"]
                lon = element["center"]["lon"]
                coords.append((lat, lon))

        return np.array(coords)
    
    def _interpolate_nodes(self, response_data: dict) -> dict:
        """
        Since OSM ways are defined by straight lines between consecutive nodes, it is possible
        that for long straight sections, there are no nodes for a significant distance, which makes
        it difficult to find the shape of the way visually.

        This method adds additional nodes space `_step_size` apart to fill in straight ways.
        """

    @property
    def step_size(self):
        """
        Get the step size to be used between consecutive nodes
        """
        return self._step_size

    @step_size.setter
    def step_size(self, new_step_size: float):
        """
        Set the step size to be used between consecutive nodes
        """
        self._step_size = new_step_size
