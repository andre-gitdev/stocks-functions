#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# bigquery_upload.py

from google.cloud import bigquery
import pandas as pd

def upload_data_to_bigquery(final_data, project_id, dataset_id, table_id, truncate=False):
    client = bigquery.Client(project=project_id)
    table_ref = client.dataset(dataset_id).table(table_id)

    # Load the final data into a DataFrame
    df = pd.DataFrame(final_data)

    # Configure the job based on whether to truncate the table or append
    if truncate:
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            autodetect=False  # Do not auto-detect schema; use the current table schema.
        )
    else:
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            autodetect=False,  # Do not auto-detect schema.
            schema_update_options=[  # Specify schema update options.
                bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION,
                bigquery.SchemaUpdateOption.ALLOW_FIELD_RELAXATION
            ]
        )

    # Load the DataFrame into the table
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)

    # Wait for the job to complete
    job.result()

    print(f"Table {table_ref} updated with DataFrame data.")

