# Databricks notebook source
# MAGIC %md
# MAGIC ## Interactive Data Analysis
# MAGIC In this notebook we show simple analysis of the data by looking at average daily cigartes smoked within each primary diagnosis groups. 

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

# MAGIC %pip install pyspark_ai

# COMMAND ----------

# MAGIC %run ./util/notebook-config 

# COMMAND ----------

import json
with open('./util/configs.json', 'r') as f:
    configs = json.load(f)
catalog_name = configs['catalog']['ctalog_name']
schema_name = configs['catalog']['schema_name']
staging_path = configs['paths']['staging_path']
expression_files_path = configs['paths']['expression_files_path']


# COMMAND ----------

# DBTITLE 1,look at available tables
sql(f'show tables in {catalog_name}.{schema_name}').display()

# COMMAND ----------

sql(f'describe {catalog_name}.{schema_name}.diagnoses').display()

# COMMAND ----------

# DBTITLE 1,top 20 diagnosis
sql(f"""
    select primary_diagnosis, count(*) as cnt
    from {catalog_name}.{schema_name}.diagnoses
    group by primary_diagnosis
    order by 2 desc
    limit 20
""").display()

# COMMAND ----------

sql(f'describe {catalog_name}.{schema_name}.exposures').display()

# COMMAND ----------

# DBTITLE 1,create an exposure history view
sql(f"""
    CREATE OR REPLACE TEMPORARY VIEW EXPOSURE_HISTORY
    AS
    select e.case_id, int(e.cigarettes_per_day), e.alcohol_intensity, int(e.years_smoked), d.primary_diagnosis
    from {catalog_name}.{schema_name}.exposures e
    join {catalog_name}.{schema_name}.diagnoses d
    on e.case_id = d.case_id
""")

# COMMAND ----------

# DBTITLE 1,average cigarettes smoked by primary diagnois 
# MAGIC %sql
# MAGIC select primary_diagnosis, avg(int(cigarettes_per_day)) as avg_pack_day_smoked
# MAGIC from EXPOSURE_HISTORY
# MAGIC where cigarettes_per_day is not null
# MAGIC group by primary_diagnosis
# MAGIC order by 2 desc
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Query using natural langauge 
# MAGIC If you have an OpenAI API key, you can use [pyspark_ai](https://github.com/databrickslabs/pyspark-ai) API to interact with any given table using natural language.

# COMMAND ----------

# DBTITLE 1,enter openAI api key
import getpass
os.environ["OPENAI_API_KEY"] = getpass.getpass()

# COMMAND ----------

# MAGIC %md
# MAGIC Alternatively you can securely store your API key using a secret scope and use the key.

# COMMAND ----------

import os
os.environ["OPENAI_API_KEY"] = dbutils.secrets.get(scope="amir-tokens", key="openAI")

# COMMAND ----------

from pyspark_ai import SparkAI
spark_ai = SparkAI(verbose=True)
spark_ai.activate()  #
df = sql('select * from EXPOSURE_HISTORY')

# COMMAND ----------

# DBTITLE 1,repeat the analysis using natural language
df.ai.plot('plot a bar chart of averegae cigarretes smoked vs primary diagnosis for the top 20 primary diagnosis')
