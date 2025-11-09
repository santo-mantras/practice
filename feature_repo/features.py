from datetime import timedelta # <-- ADD THIS
# from google.protobuf.duration_pb2 import Duration # <-- REMOVED THIS
from feast import Entity, FeatureView, FileSource, Field, ValueType 
from feast.types import Float64, Int64, String

# 1. Define an entity
stock = Entity(name="stock_id", value_type=ValueType.STRING, description="Stock ticker symbol")

# 2. Define the FileSource
stock_data_source = FileSource(
    path="../processed_data/stock_data.parquet",
    event_timestamp_column="event_timestamp",
)

# 3. Define the FeatureView
stock_features_v1 = FeatureView(
    name="stock_features_v1",
    entities=[stock], 
    
    # THIS IS THE FIX:
    # Use datetime.timedelta(days=7) instead of Duration(...)
    ttl=timedelta(days=7),
    
    schema=[
        Field(name="rolling_avg_10", dtype=Float64),
        Field(name="volume_sum_10", dtype=Float64),
        Field(name="target", dtype=Int64),
    ],
    
    online=False,
    source=stock_data_source,
    tags={},
)
