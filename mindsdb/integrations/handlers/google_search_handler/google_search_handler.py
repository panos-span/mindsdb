import os
import pandas as pd
from pandas import DataFrame
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from mindsdb.api.mysql.mysql_proxy.libs.constants.response_type import RESPONSE_TYPE
from .google_search_tables import SearchAnalyticsTable, SiteMapsTable
from mindsdb.integrations.libs.api_handler import APIHandler, FuncParser
from mindsdb.integrations.libs.response import (
    HandlerStatusResponse as StatusResponse,
    HandlerResponse as Response,
)
from mindsdb.utilities import log


class GoogleSearchConsoleHandler(APIHandler):
    """
        A class for handling connections and interactions with the Google Search API.
    """
    name = 'google_search'

    def __init__(self, name: str, **kwargs):
        """
        Initialize the Google Search API handler.
        Args:
            name (str): name of the handler
            kwargs (dict): additional arguments
        """
        super().__init__(name)
        self.token = None
        self.service = None
        self.connection_data = kwargs.get('connection_data', {})
        self.credentials_file = self.connection_data.get('credentials', None)
        self.credentials = None
        self.scopes = ['https://www.googleapis.com/auth/webmasters.readonly',
                       'https://www.googleapis.com/auth/webmasters']
        self.is_connected = False
        analytics = SearchAnalyticsTable(self)
        self.analytics = analytics
        self._register_table('Analytics', analytics)
        sitemaps = SiteMapsTable(self)
        self.sitemaps = sitemaps
        self._register_table('Sitemaps', sitemaps)

    def connect(self):
        """
        Set up any connections required by the handler
        Should return output of check_connection() method after attempting
        connection. Should switch self.is_connected.
        Returns:
            HandlerStatusResponse
        """
        if self.is_connected is True:
            return self.service
        if self.credentials_file:
            if os.path.exists('token_search.json'):
                self.credentials = Credentials.from_authorized_user_file('token_search.json', self.scopes)
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.scopes)
                    self.credentials = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token_search.json', 'w') as token:
                token.write(self.credentials.to_json())
            self.service = build('webmasters', 'v3', credentials=self.credentials)
        return self.service

    def check_connection(self) -> StatusResponse:
        """
        Check connection to the handler
        Returns:
            HandlerStatusResponse
        """
        response = StatusResponse(False)

        try:
            service = self.connect()
            response.success = True
        except Exception as e:
            log.logger.error(f'Error connecting to Google Search Console API: {e}!')
            response.error_message = e

        self.is_connected = response.success
        return response

    def native_query(self, query: str = None) -> Response:
        """
        Receive raw query and act upon it somehow.
        Args:
            query (Any): query in native format (str for sql databases,
                dict for mongo, api's json etc)
        Returns:
            HandlerResponse
        """
        method_name, params = FuncParser().from_string(query)

        df = self.call_application_api(method_name, params)

        return Response(
            RESPONSE_TYPE.TABLE,
            data_frame=df
        )

    def get_traffic_data(self, params: dict = None) -> DataFrame:
        """
        Get traffic data from Google Search Console API
        Args:
            params (dict): query parameters
        Returns:
            DataFrame
        """
        service = self.connect()
        accepted_params = ['start_date', 'end_date', 'dimensions', 'row_limit', 'aggregation_type']
        search_analytics_query_request = {
            key: value for key, value in params.items() if key in accepted_params and value is not None
        }
        response = service.searchanalytics(). \
            query(siteUrl=params['siteUrl'], body=search_analytics_query_request). \
            execute()
        df = pd.DataFrame(response['rows'], columns=self.analytics.get_columns())
        return df

    def get_sitemaps(self, params: dict = None) -> DataFrame:
        """
        Get sitemaps data from Google Search Console API
        Args:
            params (dict): query parameters
        Returns:
            DataFrame
        """
        service = self.connect()
        if params['sitemapIndex']:
            response = service.sitemaps().list(siteUrl=params['siteUrl'], sitemapIndex=params['sitemapIndex']).execute()
        else:
            response = service.sitemaps().list(siteUrl=params['siteUrl']).execute()
        df = pd.DataFrame(response['sitemap'], columns=self.sitemaps.get_columns())

        # Get as many sitemaps as indicated by the row_limit parameter
        if params['row_limit']:
            if params['row_limit'] > len(df):
                row_limit = len(df)
            else:
                row_limit = params['row_limit']

            df = df[:row_limit]

        return df

    def submit_sitemap(self, params: dict = None) -> DataFrame:
        """
        Submit sitemap to Google Search Console API
        Args:
            params (dict): query parameters
        Returns:
            DataFrame
        """
        service = self.connect()
        response = service.sitemaps().submit(siteUrl=params['siteUrl'], feedpath=params['feedpath']).execute()
        df = pd.DataFrame(response, columns=self.sitemaps.get_columns())
        return df

    def delete_sitemap(self, params: dict = None) -> DataFrame:
        """
        Delete sitemap from Google Search Console API
        Args:
            params (dict): query parameters
        Returns:
            DataFrame
        """
        service = self.connect()
        response = service.sitemaps().delete(siteUrl=params['siteUrl'], feedpath=params['feedpath']).execute()
        df = pd.DataFrame(response, columns=self.sitemaps.get_columns())
        return df

    def call_application_api(self, method_name: str = None, params: dict = None) -> DataFrame:
        """
        Call Google Search API and map the data to pandas DataFrame
        Args:
            method_name (str): method name
            params (dict): query parameters
        Returns:
            DataFrame
        """
        if method_name == 'get_traffic_data':
            return self.get_traffic_data(params)
        elif method_name == 'get_sitemaps':
            return self.get_sitemaps(params)
        elif method_name == 'submit_sitemap':
            return self.submit_sitemap(params)
        elif method_name == 'delete_sitemap':
            return self.delete_sitemap(params)
        else:
            raise NotImplementedError(f'Unknown method {method_name}')
