import streamlit as st
from business_logic import process_reviews, save_results, client
import logging
import time
from utils import total_cost_calc

def main():
    st.title("Academic Paper Analyzer")
    uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])
    
    if uploaded_file is not None:
        with st.spinner("Processing..."):
            start_time = time.time()

            logging.basicConfig(filename="log_file.log", level=logging.DEBUG, filemode="w",
                                format="%(asctime)s - %(levelname)s - %(message)s")
            logging.debug("Starting review processing...")
            
            total_prompt_tokens, total_completion_tokens, successful_responses, failed_responses = process_reviews(client, uploaded_file)
            total_cost, input_cost, output_cost = total_cost_calc(total_prompt_tokens, total_completion_tokens)
            save_results(successful_responses, failed_responses)
            logging.debug("Processing complete. Check the output files for results.")
            
            end_time = time.time()
            duration = (end_time - start_time) / 60
            st.success(f"Processing complete! Duration: {duration:.2f} mins")

            st.write("Successful responses:")
            st.dataframe(successful_responses)
            st.markdown(f"""
                        Input cost : {input_cost:.5f}  
                        Output cost: {output_cost:.5f}
                        Total cost : {total_cost:.5f} 
                        """)

            if failed_responses:
                st.write("Failed responses:")
                st.dataframe(failed_responses)

if __name__ == "__main__":
    main()
