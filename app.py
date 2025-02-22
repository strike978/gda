import streamlit as st
import pandas as pd
import csv
import os

st.set_page_config(page_title="Genetic Data Analyzer", page_icon="🧬")

def read_target_snps(file_obj):
    """Read target SNPs and genes from file"""
    target_data = {}
    if file_obj is not None:
        try:
            # Handle both uploaded files and local files
            if hasattr(file_obj, 'read'):
                if hasattr(file_obj, 'decode'):  # Uploaded file through Streamlit
                    content = file_obj.read().decode()
                else:  # Local file opened with open()
                    content = file_obj.read()
                    
            for line in csv.reader(content.splitlines()):
                if len(line) == 2:
                    gene = line[0].strip()
                    snp = line[1].strip().lower()
                    if not snp.startswith('rs'):
                        snp = 'rs' + snp
                    target_data[snp] = gene
        except Exception as e:
            st.error(f"Error reading target SNPs file: {str(e)}")
    return target_data

def read_genetic_data(uploaded_file, target_data):
    """Extract genetic data and return as DataFrame"""
    data = []
    
    if uploaded_file is not None:
        try:
            content = uploaded_file.read().decode()
            for line in content.splitlines():
                if line.startswith('#'):
                    continue
                    
                parts = line.strip().split()
                if len(parts) >= 4:
                    rsid = parts[0].lower()
                    if not rsid.startswith('rs'):
                        rsid = 'rs' + rsid
                        
                    if rsid in target_data:
                        chromosome = parts[1]
                        position = parts[2]
                        genotype = parts[3] if len(parts) == 4 else parts[3] + parts[4]
                        data.append({
                            'rsid': rsid,  # Removed .upper() to keep original case
                            'chromosome': chromosome,
                            'position': position,
                            'genotype': genotype,
                            'gene': target_data[rsid]
                        })
        except Exception as e:
            st.error(f"Error processing genetic data: {str(e)}")
    
    return pd.DataFrame(data)

def generate_raw_format(df):
    """Generate 23andMe style raw data format"""
    header = "# rsid\tchromosome\tposition\tgenotype\n"
    rows = []
    for _, row in df.iterrows():
        rows.append(f"{row['rsid']}\t{row['chromosome']}\t{row['position']}\t{row['genotype']}")
    return header + "\n".join(rows)

def main():
    st.title("Genetic Data Analyzer")
    
    st.header("Upload Files")
    genetic_file = st.file_uploader("Upload genetic data file", type=['txt'])
    
    target_file = None
    if os.path.exists("snps.txt"):
        target_file = open("snps.txt", "r")
    
    if target_file and genetic_file:
        target_data = read_target_snps(target_file)
        target_file.close()  # Clean up the file handle
        
        if target_data:
            genetic_file.seek(0)
            results_df = read_genetic_data(genetic_file, target_data)
            
            if not results_df.empty:
                st.header("Results")
                
                # Display summary
                st.write(f"Found {len(results_df)} matching SNPs")
                
                # Display detailed table
                st.subheader("Detailed View")
                st.dataframe(results_df)
                
                # Display 23andMe style format
                st.subheader("Raw Data Format")
                raw_format = generate_raw_format(results_df)
                st.text_area("", raw_format, height=400)
                
                # Add download buttons
                st.download_button(
                    label="Download Results CSV",
                    data=results_df.to_csv(index=False),
                    file_name="results.csv",
                    mime="text/csv"
                )
                
                st.download_button(
                    label="Download Raw Format TXT",
                    data=raw_format,
                    file_name="raw_format.txt",
                    mime="text/plain"
                )
            else:
                st.warning("No matching SNPs found in the genetic data file")
        else:
            st.error("No target SNPs loaded from the file")

if __name__ == "__main__":
    main()
