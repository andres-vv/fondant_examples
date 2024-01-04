from fondant.pipeline import Pipeline
import pandas as pd
import numpy as np
import pyarrow as pa
import dask.dataframe as dd

pipeline = Pipeline(
    name="test_es_component",
    base_path="./data"
)

pandas_df = pd.DataFrame(
    [
        ("hello abc", np.array([1.0, 2.0])),
        ("hifasioi", np.array([2.0, 3.0])),
    ],
    columns=["text_chunk", "embedding"],
)

pandas_df.to_parquet("./data/sample.parquet")

dataset = pipeline.read(
    "load_from_parquet",
    arguments={
        # Add arguments
        "dataset_uri": "../../data/sample.parquet",
    },
    produces={
        'text_chunk': pa.string(),
        'embedding': pa.list_(pa.float32()),
    },
)

_ = dataset.write(
    'components/index_elasticsearch',
    consumes={
        'text': 'text_chunk',
        'embedding': 'embedding'
    },
    arguments={
        'index_name': 'test_index',
        'index_body': {
            "settings": {
                "number_of_shards": 4,
            }
        },
        'hosts': ['localhost:9200'],
        'basic_auth': {'username': 'elastic', 'password': 'admin'},

    }
)

