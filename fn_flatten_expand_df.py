import pandas as pd

def flatten_and_expand_df(df):
    """
    Flattens columns in a DataFrame that contain dictionary objects or lists of dictionaries into separate columns,
    and expands columns that contain simple lists into separate columns.
    
    :param df: Original DataFrame with columns that contain dictionaries, lists of dictionaries, or lists to be processed.
    :return: DataFrame with processed columns.
    """
    result_df = df.copy()

    # Process each column
    for column in df.columns:
        # Drop NaN values and check if there are any elements left before trying to access them
        series = df[column].dropna().reset_index(drop=True)
        if len(series) > 0:
            first_element = series[0]
            # Check if the column contains dictionaries
            if isinstance(first_element, dict):
                flattened_col_df = pd.json_normalize(series)
                flattened_col_df.columns = [f"{column}_{subcol}" for subcol in flattened_col_df.columns]
                result_df = result_df.drop(column, axis=1).join(flattened_col_df, how='outer')
            # Check if the column contains a list of dictionaries
            elif isinstance(first_element, list) and all(isinstance(x, dict) for x in first_element):
                flattened_list = series.apply(lambda x: pd.json_normalize(x) if isinstance(x, list) else x)
                # Concatenate all the flattened list DataFrames
                flattened_df = pd.concat(flattened_list.tolist(), ignore_index=True)
                flattened_df.columns = [f"{column}_{subcol}" for subcol in flattened_df.columns]
                result_df = result_df.drop(column, axis=1).join(flattened_df, how='outer')
            # Check if the column contains simple lists
            elif isinstance(first_element, list):
                # Expand the list into separate columns
                expanded_col_df = series.apply(pd.Series)
                expanded_col_df.columns = [f"{column}_{i+1}" for i in range(expanded_col_df.shape[1])]
                result_df = result_df.drop(column, axis=1).join(expanded_col_df, how='outer')
        else:
            # If the column is empty after dropping NaN, just keep it as it is
            result_df[column] = df[column]

    return result_df
