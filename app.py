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
                df.to_excel(writer, sheet_name='Sheet1')
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
    df = pd.DataFrame({"Sr. No":range(1, len(content1)+1), "content1": header_data, "content2":content1, "content3": content2})
    return df

st.header("Unknow Application")
search_term = st.text_input("Enter your search word")
download = st.button("Get Data")
class FileDownloader(object):

    def __init__(self, data,filename='myfile',file_ext='txt'):
        super(FileDownloader, self).__init__()
        self.data = data
        self.filename = filename
        self.file_ext = file_ext

    def download(self):
        b64 = base64.b64encode(self.data.encode()).decode()
        new_filename = "{}_{}.{}".format(self.filename,timestr,self.file_ext)
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

        download = FileDownloader(df.to_csv(index = False),filename = search_term,file_ext='csv').download()
    else:
        st.error("Wrong Search keyword, Please enter correct Search keyword.")

