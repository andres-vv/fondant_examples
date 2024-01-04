"""IndexElasticSearch component. This component can create indexes and index documents into ElasticSearch."""

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import dask.dataframe as dd
from elasticsearch import Elasticsearch
from fondant.component import DaskWriteComponent
from tqdm import tqdm

if TYPE_CHECKING:
    import pandas as pd

logger = logging.getLogger(__name__)


class IndexElasticSearch(DaskWriteComponent):
    def __init__(
            self,
            index_name: str,
            index_body: Dict[str, Any],
            basic_auth: Optional[Dict[str, str]],
            cloud_id: Optional[str],
            api_key: Optional[Dict[str, str]],
            hosts: Optional[List[str]],
            **kwargs,
    ):
        # Reformat dictionaries as Elasticsearch object expects tuples.
        # Tuples are not supported by the component spec.
        if basic_auth:
            basic_auth = (basic_auth["username"], basic_auth["password"])
        if api_key:
            api_key = (api_key["id"], api_key["api_key"])
        self.client = Elasticsearch(
            hosts=hosts,
            basic_auth=basic_auth,
            api_key=api_key,
        )
        self.index_name = index_name
        self.create_index(index_body)

    def create_index(self, index_body: Dict[str, Any]):

        if self.client.indices.exists(index=self.index_name):
            logger.info(f"Index: {self.index_name} already exists.")
        else:
            logger.info(
                f"Creating Index: {self.index_name} with body: {index_body}")
            self.client.indices.create(index=self.index_name, body=index_body)

    def write(self, dataframe: dd.DataFrame):
        """
        Writes the data from the given Dask DataFrame to the Elasticsearch cluster index.

        Args:
            dataframe: The Dask DataFrame containing the data to be written.
        """
        for part in tqdm(dataframe.partitions):
            df: pd.DataFrame = part.compute()
            for row in df.itertuples():
                body = {"embedding": row.embedding, "text": row.text}
                self.client.index(
                    index=self.index_name,
                    id=str(row.Index),
                    body=body,
                )
