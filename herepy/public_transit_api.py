#!/usr/bin/env python

from __future__ import division

import sys
import json
import requests

from herepy.here_api import HEREApi
from herepy.utils import Utils
from herepy.error import HEREError
from herepy.models import PublicTransitResponse
from herepy.here_enum import PublicTransitSearchMethod

class PublicTransitApi(HEREApi):
    """A python interface into the HERE Public Transit API"""

    def __init__(self,
                 app_id=None,
                 app_code=None,
                 timeout=None):
        """Return a PublicTransitApi instance.
        Args:
          app_id (string): App Id taken from HERE Developer Portal.
          app_code (string): App Code taken from HERE Developer Portal.
          timeout (int): Timeout limit for requests.
        """

        super(PublicTransitApi, self).__init__(app_id, app_code, timeout)
        self._base_url = 'https://cit.transit.api.here.com/v3/'

    def __get(self, data, path, json_node):
        url = Utils.build_url(self._base_url + path, extra_params=data)
        response = requests.get(url, timeout=self._timeout)
        json_data = json.loads(response.content.decode('utf8'))
        if json_node in json_data.get('Res', {}):
            return PublicTransitResponse.new_from_jsondict(json_data)
        elif 'text' in json_data.get('Res', {}).get('Message', {}):
            return HEREError(json_data['Res']['Message']['text'], 'Error occured on ' + sys._getframe(1).f_code.co_name)
        else:
            return HEREError('Error occured on ' + sys._getframe(1).f_code.co_name)

    def find_stations_by_name(self,
                              center,
                              name,
                              max_count=5,
                              method=PublicTransitSearchMethod.fuzzy,
                              radius=20000):
        """Request a list of public transit stations based on name.
        Args:
          center (array): array including latitude and longitude in order.
          name (string): station name.
          max_count (int): maximum number of stations  (Default is 5).
          method (enum): Matching method from PublicTransitSearchMethod (Default is fuzzy).
          radius (int): specifies radius in kilometers (Default is 20000km).
        """

        data = {'center': str.format('{0},{1}', center[0], center[1]),
                'name':  name,
                'app_id': self._app_id,
                'app_code': self._app_code,
                'max': max_count,
                'method': method.__str__(),
                'radius': radius}
        return self.__get(data, 'stations/by_name.json', 'Stations')

    def find_stations_nearby(self, center, radius=500, max_count=5):
        """Request a list of public transit stations within a given geo-location.
        Args:
          center (array): array including latitude and longitude in order.
          radius (int): specifies radius in meters (Default is 500m).
          max_count (int): maximum number of stations  (Default is 5).
        """

        data = {'center': str.format('{0},{1}', center[0], center[1]),
                'radius': radius,
                'app_id': self._app_id,
                'app_code': self._app_code,
                'max': max_count}
        return self.__get(data, 'stations/by_geocoord.json', 'Stations')

    @classmethod
    def __prepare_station_ids(cls, ids):
        station_ids = ""
        for stn_id in ids:
            station_ids += str.format('{0},', stn_id)
        station_ids = station_ids[:-1]
        return station_ids

    def find_stations_by_id(self, ids, lang):
        """Request details of a specific transit station based on a previous request.
        Args:
          ids (array): array contains station ids.
          lang (string): language code for response like `en`.
        """

        data = {'stnIds': self.__prepare_station_ids(ids),
                'lang': lang,
                'app_id': self._app_id,
                'app_code': self._app_code}
        return self.__get(data, 'stations/by_ids.json', 'Stations')

    def find_transit_coverage_in_cities(self, center, political_view, radius):
        """Request a list of transit operators available in cities nearby.
        Args:
          center (array): array including latitude and longitude in order.
          political_view (string): switch for grouping results like `CHN`.
          radius (int): specifies radius in meters.
        """

        data = {'center': str.format('{0},{1}', center[0], center[1]),
                'politicalview': political_view,
                'radius': radius,
                'app_id': self._app_id,
                'app_code': self._app_code}
        return self.__get(data, 'coverage/city.json', 'Coverage')

    def next_nearby_departures_of_station(self, station_id, time, lang='en'):
        """Request a list of next departure times and destinations of a particular station.
        Args:
          lang (string): language code for response like `en` Default is `en`.
          station_id (int): station id for departures.
          time (string): time formattes in yyyy-mm-ddThh:mm:ss.
        """

        data = {'lang': lang,
                'stnId': station_id,
                'time': time,
                'app_id': self._app_id,
                'app_code': self._app_code}
        return self.__get(data, 'board.json', 'NextDepartures')

    def next_departures_from_location(self,
                                      center,
                                      time,
                                      lang='en',
                                      max=40,
                                      max_station=40):
        """Request a list of all next departure times and destinations from a given location.
        Args:
          center (array): array including latitude and longitude in order.
          time (string): time formattes in yyyy-mm-ddThh:mm:ss.
          lang (string): language code for response like `en`. Default is `en`.
          max (int): maximum number of next departures per station. Default is 40.
          max_station (int): maximum number of stations for which departures are required. Default is 40.
        """

        data = {'lang': lang,
                'center': str.format('{0},{1}', center[0], center[1]),
                'time': time,
                'app_id': self._app_id,
                'app_code': self._app_code,
                'max': max,
                'maxStn': max_station}
        return self.__get(data, 'multiboard/by_geocoord.json', 'MultiNextDepartures')

    def next_departures_for_stations(self,
                                     station_ids,
                                     time,
                                     lang='en',
                                     max=40,
                                     max_station=40):
        """Request a list of all next departure times and destinations for a give list of stations.
        Args:
          station_ids (array): a list of stop ids.
          time (string): time formattes in yyyy-mm-ddThh:mm:ss.
          lang (string): language code for response like `en`. Default is `en`.
          max (int): maximum number of next departures per station. Default is 40.
          max_station (int): maximum number of stations for which departures are required. Default is 40.
        """

        data = {'lang': lang,
                'time': time,
                'app_id': self._app_id,
                'app_code': self._app_code,
                'max': max,
                'maxStn': max_station,
                'stnIds': self.__prepare_station_ids(station_ids)}
        return self.__get(data, 'multiboard/by_stn_ids.json', 'MultiNextDepartures')