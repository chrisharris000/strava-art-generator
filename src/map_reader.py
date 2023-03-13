"""
This module contains classes and methods relevant to reading/parsing/displaying
OpenStreetMap (OSM) data

Author: Chris Harris
"""

from math import sqrt

import matplotlib.pyplot as plt
import numpy as np
import requests

class MapReader:
    """
    Class handles accessing OpenStreetMap data and returning relevant road/street data
    """
    def __init__(self):
        self._overpass_url = "http://overpass-api.de/api/interpreter"
        self._step_size = 10.0
        self._overpass_result = {}
        self._node_coordinates = {}

    # Getter/setters
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

    # Public methods
    def get_highway_data_from_bbox(self, south_latitude: float, west_longitude: float,
                                    north_latitude: float, east_longitude: float) -> None:
        """
        Queries all OSM nodes, ways and relations within the box defined by the latitudes/longitudes
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
        out body;
        >;
        out skel qt;
        """
        self._overpass_result = self._query_overpass(query)

    def interpolate_nodes(self) -> None:
        """
        Since OSM ways are defined by straight lines between consecutive nodes, it is possible
        that for long straight sections, there are no nodes for a significant distance, which makes
        it difficult to find the shape of the way visually.

        This method adds additional nodes space `_step_size` apart to fill in straight ways.
        """

    def plot_response_data(self) -> None:
        """
        Plot the lat/long of each node, nodes in ways and nodes in relations
        """
        lat_lon = []
        for node in self._node_coordinates.items():
            pair = self._node_coordinates[node]
            lat_lon.append(pair)
        lat_lon = np.array(lat_lon)
        latitudes, longitudes = lat_lon[:, 0], lat_lon[:, 1]

        plt.plot(longitudes, latitudes, "o")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.axis("equal")
        plt.show()

    # Private methods
    def _query_overpass(self, query: str, timeout=30) -> dict:
        """
        Send query to Overpass API and return json formatted result
        """
        response = requests.get(self._overpass_url, params={"data": query}, timeout=timeout)
        response_data = response.json()
        return response_data

    def _extract_coordinates(self) -> None:
        """
        Extract the lat/lon of each node, nodes in ways and nodes in relations from the query result
        """

        for element in self._overpass_result["elements"]:
            if element["type"] == "node":
                node_id = element["id"]
                lat = element["lat"]
                lon = element["lon"]
                self._node_coordinates[node_id] = tuple([lat, lon])

def distance(a_lat_lon: tuple[float], b_lat_lon: tuple[float]) -> float:
    """
    Calculate the distance between 2 points
    """
    a_x, a_y = a_lat_lon
    b_x, b_y = b_lat_lon
    return sqrt((a_x - b_x)**2 + (a_y - b_y)**2)
