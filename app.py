import streamlit as st
import requests
from urllib.request import urlopen as ureq
from bs4 import BeautifulSoup as bs
import numpy as np
import pandas as pd
import base64
import time
import io
from typing import List

timestr = time.strftime("%Y%m%d-%H%M%S")

def find_max_pages(htmlpage):
    for div in htmlpage.find_all("div", {"class": "pagination-wrapper"}):
        div = div.find_all("input", {"class": "pagination-jump-field"})
        return int(str(div).split(" ")[2].split("=")[1][1:-1])

def to_excel(df, fname):

    def convert_df(df):
        buffer = io.BytesIO()
        with st.spinner('Writing to Excel will take few minutes to complete Please wait...'):
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index_label="Sr. No.", startrow=5, startcol=0, sheet_name='Sheet1')


                workbook  = writer.book
                worksheet = writer.sheets['Sheet1']

                # Insert an image.
                worksheet.insert_image('A1', 'logo.png')
                # Formating stuff.
                bold = workbook.add_format({'bold': True})
                cell_format = workbook.add_format({'bold': True, 'font_color': 'red'})
                
                worksheet.set_column('B:F', 35)
                worksheet.write('C2', 'Research on Germany Stroke Market', bold)
                worksheet.write('F2', 'Results for search string:', bold)
                worksheet.write('F3',search_term , cell_format)
                worksheet.write('F4',"Found: "+str(number_of_pages)+" pages")

        
                writer.save()
        return buffer

    buffer = convert_df(df)
    st.success("#### Data Downloaded Successfully ####")
    st.download_button(
        label="Download Your Output File as Excel",
        data=buffer,
        file_name=f"{fname}_data.xlsx",
        mime="application/vnd.ms-excel"
    )

def scrape_data(number_of_pages:int, keyword:str):
    keyword = keyword.lower()
    header = []
    content = []
    # st.info(f"Number of pages found {number_of_pages}")
    st.markdown("Downloading the Data. Grab a cup of coffee and wait.")
    print("Downloading Data. Please Wait..")
    
    t = st.empty()
    my_bar = st.progress(0)
    sessions = np.linspace(0, 1.0, number_of_pages)
    pages = range(1, number_of_pages + 1)

    for i, j in zip(pages, sessions):
        my_bar.progress(j)
        t.info(f"Downloaded {i} out of {number_of_pages} pages.")
        url = f"https://klinikradar.de/{keyword}/kliniken/{i}/"
        uclient = ureq(url)
        page = uclient.read()
        uclient.close()
        html_page = bs(page, "html.parser")
        
        for div in html_page.findAll('h3', {"class": "serp-card-heading"}):
            header.append(div.find('a').contents[0])
            
        for div in html_page.find_all("div", {"class": "serp-card-highlight-subline"}):
            head = div.contents[0]
            
            if not head == "Patientenbefragung der Techniker Krankenkasse":
                content.append(head)
                
    return header, content

def structuring_data_to_excel(header_data: List, content_data: List):

    content1 = []
    for i in range(0, len(content_data), 2):
        content1.append(content_data[i])
        
    content2 = [i for i in content if i not in content1]
    
    df = pd.DataFrame({"content1": header_data, "content2":content1, "content3": content2})
    df.index = df.index + 1
    
    
    
    return df

st.header("Web Scraping: Research on Germany Stroke Market")
search_term = st.text_input("Enter your search term")
download = st.button("Fetch Data")

class FileDownloader(object):

    def __init__(self, data,filename='myfile',file_ext='txt'):
        super(FileDownloader, self).__init__()
        self.data = data
        self.filename = filename
        self.file_ext = file_ext

    def download(self):
        b64 = base64.b64encode(self.data.encode()).decode()
        new_filename = "{}_{}.{}".format(timestr,self.filename,self.file_ext)
        href = f'<a href="data:file/{self.file_ext};base64,{b64}" download="{new_filename}">Click Here to download the file.!!</a>'
        st.markdown(href,unsafe_allow_html=True)
        
if download:
    oepning_url = f"https://klinikradar.de/{search_term}/kliniken/1/"

    r = requests.head(oepning_url)

    if r.status_code == 200:
        uclient = ureq(oepning_url)
        page = uclient.read()
        uclient.close()
        html_page = bs(page, "html.parser")

        number_of_pages = find_max_pages(html_page)

        header, content = scrape_data(4, search_term)

        df = structuring_data_to_excel(header, content)
                




        # to_excel(df, fname = search_term)

        download = FileDownloader(df.to_excel(index_label="Sr. No.", startrow=5, startcol=0), filename = "Research on Germany Stroke Market_"+search_term,file_ext='xlsx').download()
    else:
        st.error("Wrong Search keyword, Please enter correct Search keyword.")

