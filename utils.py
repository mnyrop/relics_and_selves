import os
import pymysql
import pandas as pd
import codecs
import configparser
from pandas.api.types import is_string_dtype


def config(conf_path):
    config = configparser.RawConfigParser()
    config.readfp(open(conf_path))
    return {'db_user': config.get('client', 'user'), 
            'db_pass': config.get('client', 'password'), 
            'db_host': config.get('client', 'host')}

def connect_all_dbs(config):
    return pymysql.connect(host=config['db_host'], 
                           user=config['db_user'], 
                           passwd=config['db_pass'], 
                           charset='utf8')
    
def connect_db(db_name, config):
    return pymysql.connect(host=config['db_host'], 
                           user=config['db_user'], 
                           passwd=config['db_pass'], 
                           db=db_name, 
                           charset='utf8')

def rowcount(connector, table):
    count = pd.read_sql("SELECT COUNT(*) FROM " + table + ";", con=connector)
    return count['COUNT(*)'][0]

def show_tables(connector):
    df = pd.read_sql("SHOW TABLES;", con=connector)
    return list(df[str(df.columns[0])].astype(str))

def markdown_table(df):
    fmt = ['---' for i in range(len(df.columns))]
    df_fmt = pd.DataFrame([fmt], columns=df.columns)
    df_formatted = pd.concat([df_fmt, df])
    return df_formatted.to_csv(sep="|", index=False, encoding='utf-8', quotechar="*")

def preview(connector, tables):
    all_tables_string = "### `declassification_cables` preview \n\n"
    for table in tables:
        df_head = pd.read_sql('SELECT * FROM ' + table + ' LIMIT 5;', con=connector)
        for col in df_head.columns:
            if is_string_dtype(df_head[col]):
                df_head[col] = df_head[col].str[:200].replace('\n',' ', regex=True)
        all_tables_string += "#### `" + table + "`\n\n" + markdown_table(df_head) + "\n\n"
    return all_tables_string

def results_to_md(name, preview):
    result_string = "# " + name +" Preview — " + "\n\n\n" + preview
    results_filepath = name + "-preview.md"
    print("Writing results of ingestion to", results_filepath, "...")

    try:
        os.remove(results_filepath)
    except OSError:
        pass

    f = codecs.open(results_filepath, encoding='utf-8', mode="w+")
    f.write(unicode(result_string,'utf-8'))
    
def df_sample(connector, table, limit):
    return pd.read_sql("SELECT * FROM " + table + " LIMIT " + str(limit) + ";", con=connector)

def df(connector, table):
    return pd.read_sql("SELECT * FROM " + table + ";", con=connector)
    
