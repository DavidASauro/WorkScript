import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

# The URL of the website you want to scrape
url = 'https://www.mpaevum.com/wrcrinkschedule/'

# Send an HTTP GET request to the URL
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content of the page using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    iframe = soup.find('iframe')

    # Check if the iframe element exists
    if iframe:
    # Get the value of the src attribute
        iframe_src = iframe['src']
        
    else:
        print("No iframe found on the page.")

    # Extract the text from the HTML
    response = requests.get(iframe_src)
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table')

    if table:
        # Extract data from the table
        data = []
        for row in table.find_all('tr'):
            columns = row.find_all('td')
            row_data = [col.get_text(strip=True) for col in columns]
            data.append(row_data)

        df=pd.DataFrame(data)
        #print(df)
        df = df.iloc[5:]
        df.reset_index(drop=True, inplace=True)
        #print(df)
        df = df.iloc[::2]
        df.reset_index(drop=True, inplace=True)
        
        rink1 = ' Molson'
        rink2 = ' Desmarais'

        df[2] = df[2] + rink1
        df[7] = df[7] + rink2

        df[1] = df[1].str.split('-').str[1].str.strip()
        df[6] = df[6].str.split('-').str[1].str.strip()

        

        print(df)

        
        
        all_times = pd.concat([df[1], df[6]])

        all_times = all_times.apply(pd.to_datetime, format='%H:%M')
        all_times = all_times.sort_values()
        
        all_times = all_times.dt.strftime('%H:%M')

        
        

        


      

        print(all_times)
        
    else:
        print("No table found on the page.")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
