from processor import BankProcessor
import os

def test():
    file_path = r'c:\Users\Sebastian\Desktop\formatter\data.xlsx'
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
        
    with open(file_path, 'rb') as f:
        content = f.read()
        
    # We need to import pandas to inspect the result
    import pandas as pd
    from io import BytesIO
    
    processed = BankProcessor.process_excel(content)
    if not processed:
        print("FAILED: Processed content is empty")
    else:
        df_result = pd.read_excel(BytesIO(processed))
        print("SUCCESS: Processed data sample:")
        print(df_result.head())
        print(f"Columns: {df_result.columns.tolist()}")
        with open('test_out.xlsx', 'wb') as out:
            out.write(processed)

if __name__ == "__main__":
    test()
