import pandas as pd

def parse_packet(raw, registers):

    # Accept both list-of-dicts and dataframe
    if isinstance(registers, list):
        df = pd.DataFrame(registers)
    else:
        df = registers.copy()

    df.columns = df.columns.str.strip()
    df['Total Upto'] = pd.to_numeric(df['Total Upto'], errors='coerce')
    df = df.dropna(subset=['Index', 'Total Upto'])

    # Ensure packet length matches dictionary layout
    df['Total Upto'] = pd.to_numeric(df['Total Upto'], errors='coerce')
    required_length = int(df['Total Upto'].dropna().max())

    data_string = raw
    if len(data_string) < required_length:
        data_string = data_string.ljust(required_length)

    decoded_results = []

    for _, row in df.iterrows():
        try:
            short_name = str(row['Short name'])
            # 'Index' in Excel is 1-based; Python is 0-based
            start = int(row['Index'])
            # 'Total Upto' is used as the end of the slice
            end = int(row['Total Upto'])

            # Extract the raw string segment
            raw_segment = data_string[start:end].strip()

            # Skip if segment is empty
            if not raw_segment:
                decoded_results.append({
                    "Short name": short_name,
                    "Value": "N/A",
                    "Units": ""
                })
                continue

            data_format = str(row['Data format']).strip()
            scaling = float(row['Scaling Factor']) if pd.notnull(row['Scaling Factor']) else 1.0
            offset = float(row['Offset']) if pd.notnull(row['Offset']) else 0.0
            units = str(row['Units']) if pd.notnull(row['Units']) else ""

            segment = raw_segment.strip()

            if data_format == "ASCII":
                final_val = segment
            else:
                try:
                    numeric_val = int(segment, 16)   # ALWAYS HEX
                except:
                    numeric_val = 0
            
                final_val = (numeric_val * scaling) + offset
            
                if final_val == int(final_val):
                    final_val = int(final_val)
                else:
                    final_val = round(final_val, 4)
                # except ValueError:
                #     # If it contains hex characters (like '3D'), parse as hex
                #     try:
                #         numeric_val = int(raw_segment, 16)
                #         final_val = (numeric_val * scaling) + offset
                #     except:
                #         final_val = raw_segment  # Fallback to original string

            decoded_results.append({
                "Short name": short_name,
                "Value": final_val,
                "Units": units
            })

        except Exception as e:
            print(f"Error parsing row {row.get('Short name','Unknown')}: {e}")
            continue

    return decoded_results
