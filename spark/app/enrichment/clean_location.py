"""
Get location data from staging table and clean it
"""

from pyspark.sql import SparkSession
from pyspark.sql.types import StringType
from pyspark.sql.functions import col, regexp_replace

# Connect to Postgres

spark = SparkSession.builder.appName(f"CleanLocation").getOrCreate()

# Spark Context
sc = spark.sparkContext
sc.setLogLevel("ERROR")

# Read data from staging table

database_url = "jdbc:postgresql://postgres:5432/deng_staging"
properties = {
    "user": "postgres",
    "password": "",
    "driver": "org.postgresql.Driver"
}

bus_delay_df = spark.read \
    .jdbc(url=database_url, table=f"public.staging_bus_delay", properties=properties)

bus_delay_df.show()

def slug(text):
    """
    Convert text to slug
    """
    tmp = text.lower()
    tmp = tmp.replace(" ", "-")
    tmp = tmp.replace(":", "")
    tmp = tmp.replace(";", "")
    tmp = tmp.replace(",", "")
    tmp = tmp.replace(".", "")
    tmp = tmp.replace("!", "")
    tmp = tmp.replace("'", "")
    tmp = tmp.replace('"', "")
    tmp = tmp.replace("/", "")
    tmp = tmp.replace("&", "")
    return tmp

# Define a UDF for slugify
slugify_udf = spark.udf.register("slugify_udf", slug, StringType())

# Add location slug column
bus_delay_df = bus_delay_df.withColumn("location_slug", slugify_udf(col("location")))

# Clean location data
bus_delay_df = bus_delay_df.withColumn("location", regexp_replace(col("location"), " - ", "-"))

# Show Spark df
bus_delay_df.show()

# Write to Postgres
bus_delay_df.write \
    .jdbc(url=database_url, table=f"public.enrichment_bus_delay", properties=properties, mode="overwrite")

# Stop Spark
spark.stop()