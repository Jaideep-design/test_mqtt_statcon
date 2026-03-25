import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pandas as pd
import streamlit as st
from dictionary_utils import excel_to_json
from backend.parser_logic import parse_packet


st.set_page_config(page_title="Manual Raw Hex Parser", layout="wide")

st.title("📝 Manual Raw Hex Parser (Dictionary → Parse Raw Packet)")
st.write("Upload a dictionary Excel and paste a raw packet to parse it locally.")


# ------------------------------------------------------------------------------
# Upload dictionary
# ------------------------------------------------------------------------------

st.header("1️⃣ Upload Dictionary Excel")

uploaded_excel = st.file_uploader("Upload Dictionary Excel", type=["xlsx"])

if uploaded_excel and st.button("Convert Excel → JSON"):

    try:
        registers = excel_to_json(uploaded_excel)

        st.session_state.manual_registers = registers

        st.success("Dictionary loaded successfully!")

        st.subheader("Dictionary Preview")
        st.json(registers[:5])

    except Exception as e:
        st.error(f"Error converting dictionary: {e}")


# ------------------------------------------------------------------------------
# Raw packet input
# ------------------------------------------------------------------------------

st.header("2️⃣ Paste Raw Packet")

raw_hex = st.text_area(
    "Raw Hex Packet",
    height=150,
    key="packet_input"
)
packet = st.session_state.packet_input


# ------------------------------------------------------------------------------
# Parse
# ------------------------------------------------------------------------------

st.header("3️⃣ Parse Packet")

if st.button("Parse Raw Packet"):

    if raw_hex == "":
        st.error("Please paste a raw packet!")

    elif "manual_registers" not in st.session_state:
        st.error("Please upload and convert a dictionary first!")

    else:

        try:

            registers_df = pd.DataFrame(st.session_state.manual_registers)

            st.write("Packet length:", len(packet))
            st.write("First 50 chars:", packet[:50])

            parsed = parse_packet(packet, registers_df)

            if not parsed:
                st.warning("Parsed output is empty.")

            else:
                df = pd.DataFrame(parsed)

                st.subheader("Parsed DataFrame")

                st.dataframe(
                    df,
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"Error parsing raw packet: {e}")
