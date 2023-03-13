"""
This module contains classes and methods relevant to reading/parsing/displaying
OpenStreetMap (OSM) data

Author: Chris Harris
"""

import json

from math import sqrt
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import requests

class MapReader:
    """
    Class handles accessing OpenStreetMap data and returning relevant road/street data
    """
    def __init__(self):
        self._overpass_url = "http://overpass-api.de/api/interpreter"
        self._step_size = 0.0001
        self._overpass_result = {}
        self._node_coordinates = {}
        self._save_location = Path.home() / "strava-art-generator" / "osm-data"

    # Getter/setters
    @property
    def step_size(self) -> float:
        """
        Get the step size to be used between consecutive nodes
        """
        return self._step_size

    @step_size.setter
    def step_size(self, new_step_size: float) -> None:
        """
        Set the step size to be used between consecutive nodes
        """
        self._step_size = new_step_size

    @property
    def save_location(self) -> str:
        """
        Get the save location for any overpass results
        """
        return self._save_location

    @save_location.setter
    def save_location(self, new_save_location: str) -> None:
        """
        Set the new save location for any overpass results
        """
        self._save_location = new_save_location

    # Public methods
    def get_highway_data_from_bbox(self, south_latitude: float, west_longitude: float,
                                    north_latitude: float, east_longitude: float,
                                    write_to_file: bool=False) -> None:
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

        if write_to_file:
            json_object = json.dumps(self._overpass_result, indent=4)
            with open(self.save_location / "osm-output.json", "w", encoding="utf8") as output:
                output.write(json_object)

    def get_highway_data_from_file(self, file_location: Path) -> None:
        """
        Read json formatted overpass result from saved file
        """
        with open(file_location, "r", encoding="utf8") as input_file:
            self._overpass_result = json.load(input_file)

    def interpolate_nodes(self, write_to_file: bool=False) -> None:
        """
        Since OSM ways are defined by straight lines between consecutive nodes, it is possible
        that for long straight sections, there are no nodes for a significant distance, which makes
        it difficult to find the shape of the way visually.

        This method adds additional nodes space `_step_size` apart to fill in straight ways.
        """
        modified_overpass_result = self._overpass_result.copy()

        for element in self._overpass_result["elements"]:
            if element["type"] != "way":
                continue

            way_nodes = element["nodes"]
            way_id = element["id"]
            new_way_nodes = way_nodes.copy()

            for idx, curr_node in enumerate(way_nodes):
                new_way_nodes.append(curr_node)

                if idx == len(way_nodes) - 1:
                    continue

                next_node = way_nodes[idx + 1]
                next_node_coord = self._node_coordinates.get(next_node, None)
                curr_node_coord = self._node_coordinates.get(curr_node, None)

                if not curr_node_coord:
                    curr_node_data = self._get_node_lat_lon(curr_node)["elements"][0]
                    curr_node_coord = [curr_node_data["lat"], curr_node_data["lon"]]

                if not next_node_coord:
                    next_node_data = self._get_node_lat_lon(next_node)["elements"][0]
                    next_node_coord = [next_node_data["lat"], next_node_data["lon"]]

                dist = distance(curr_node_coord, next_node_coord)

                if dist > self.step_size:
                    n_divisions = int((dist // self.step_size) + 1)
                    additional_nodes_lat = np.linspace(curr_node_coord[0],
                                                       next_node_coord[0],
                                                       n_divisions)
                    additional_nodes_lon = np.linspace(curr_node_coord[1],
                                                       next_node_coord[1],
                                                       n_divisions)
                    additional_nodes = zip(additional_nodes_lat, additional_nodes_lon)
                    additional_node_ids = [int(str(curr_node) + f"{sub_id:03}") \
                                           for sub_id in range(len(additional_nodes_lat))]

                    for additional_node_id, additional_node in zip(additional_node_ids,
                                                                   additional_nodes):
                        new_node = {
                            "type": "node",
                            "id": additional_node_id,
                            "lat": additional_node[0],
                            "lon": additional_node[1]
                        }
                        # add new node to end of elements
                        modified_overpass_result["elements"].append(new_node)

                        # add new node id to way
                        new_way_nodes.append(additional_node_id)

                        # add new node to _node_coordinates
                        self._node_coordinates[additional_node_id] = tuple([new_node["lat"],
                                                                            new_node["lon"]])

            new_way_nodes.append(way_nodes[-1]) # manually added since it is skipped in the loop

            # assign new way nodes to result
            for element in modified_overpass_result["elements"]:
                if element["id"] == way_id:
                    element["nodes"] = new_way_nodes

        self._overpass_result = modified_overpass_result

        if write_to_file:
            json_object = json.dumps(self._overpass_result, indent=4)
            with open(self.save_location / "osm-interpolated-output.json", "w", encoding="utf8") \
                as output:
                output.write(json_object)

    def plot_response_data(self) -> None:
        """
        Plot the lat/long of each node, nodes in ways and nodes in relations
        """
        lat_lon = []
        for _node, pair in self._node_coordinates.items():
            lat_lon.append(pair)
        lat_lon = np.array(lat_lon)
        latitudes, longitudes = lat_lon[:, 0], lat_lon[:, 1]

        plt.plot(longitudes, latitudes, "o")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.axis("equal")
        plt.show()

    def extract_coordinates(self) -> None:
        """
        Extract the lat/lon of each node, nodes in ways and nodes in relations from the query result
        """

        for element in self._overpass_result["elements"]:
            if element["type"] == "node":
                node_id = element["id"]
                lat = element["lat"]
                lon = element["lon"]
                self._node_coordinates[node_id] = tuple([lat, lon])

    # Private methods
    def _query_overpass(self, query: str, timeout: int=30) -> dict:
        """
        Send query to Overpass API and return json formatted result
        """
        response = requests.get(self._overpass_url, params={"data": query}, timeout=timeout)
        response_data = response.json()
        return response_data

    def _get_node_lat_lon(self, node_id: int) -> dict:
        """
        Get the lat, lon for a node given its id
        """
        query = f"""
        [out:json];
        (
        node({node_id});
        );
        (._;>;);
        out;"""
        return self._query_overpass(query)

def distance(a_lat_lon: tuple[float], b_lat_lon: tuple[float]) -> float:
    """
    Calculate the distance between 2 points
    """
    a_x, a_y = a_lat_lon
    b_x, b_y = b_lat_lon
    return sqrt((a_x - b_x)**2 + (a_y - b_y)**2)

def metres_to_degrees(metres: float) -> float:
    """
    An **approximate** conversion between metres to lat/lon degrees
    e.g. Helpful if calculating a change in 20m results in a change in x degrees

    Source: https://www.usna.edu/Users/oceano/pguth/md_help/html/approx_equivalents.htm
    """
    return metres / (111*10**3)

if __name__ == "__main__":
    reader = MapReader()
    reader.get_highway_data_from_bbox(-33.83842,150.93879,-33.83621,150.94294)
    reader.extract_coordinates()
    reader.interpolate_nodes()
    reader.plot_response_data()
