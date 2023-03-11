"""
This module contains classes and methods relevant to reading/parsing/displaying
OpenStreetMap (OSM) data

Author: Chris Harris
"""
class MapReader:
    """
    Class handles accessing OpenStreetMap data and returning relevant road/street data
    """
    def __init__(self):
        pass

    def _get_map_data_from_bbox(self, west_longitude: float, south_latitude: float,
                                east_longitude: float, north_latitude: float):
        """
        Return all OSM nodes, ways and relations within the box defined by the latitudes/longitudes
        """
        pass
