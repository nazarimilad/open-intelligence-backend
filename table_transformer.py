import argparse
from domain.table_analysis.table_processor import TableProcessor
from domain.table_analysis.bordered_table_processor import BorderedTableProcessor
from domain.table_analysis.borderless_table_processor import BorderlessTableProcessor
import pandas as pd

def parse_args():
    parser = argparse.ArgumentParser(description="Transform a table image to a Pandas Dataframe.")
    parser.add_argument(
        "-t", "--table-type", 
        help="Type of the table", 
        nargs=1, 
        choices=["bordered", "borderless"],
        required=True
    )
    parser.add_argument(
        "-i", "--image", 
        help="The image file", 
        nargs=1, 
        type=argparse.FileType('r'),
        required=True
    )
    args = parser.parse_args()
    table_type = args.table_type[0]
    image_path = args.image[0].name
    return table_type, image_path

if __name__ == "__main__":
    table_type, image_path = parse_args()
    table_processor = None
    if table_type == "bordered":
        table_processor = BorderedTableProcessor()
    else:
        table_processor = BorderlessTableProcessor()
    table = table_processor.get_table_from_image(image_path) 
    pd.set_option('display.max_columns', None)  
    pd.set_option('display.expand_frame_repr', False)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(table)
        print(table.shape)