import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


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

        #df[1] = df[1] + rink1
        #df[6] = df[6] + rink2

        df[1] = df[1].fillna('') + '    ' + rink1
        df[6] = df[6].fillna('') + ' ' +rink2

        stacked_df = pd.concat ([df[1], df[6]])
        stacked_df = stacked_df[stacked_df.str.match(r'^\d{2}:\d{2} .+$')]
        stacked_df = stacked_df.str.split(' ', n=1, expand=True)
        stacked_df.columns = ['Time', 'Rink']
        stacked_df['Time'] = pd.to_datetime(stacked_df['Time'], format='%H:%M', errors='coerce')
        stacked_df['Time'] = stacked_df['Time'].dt.strftime('%H:%M')
        stacked_df = stacked_df.dropna()
        stacked_df = stacked_df.sort_values(by='Time')

        print(stacked_df)


        # Your email configuration
        sender_email = 'DavidSau43@Gmail.com'
        sender_password = 'shhk hlcn vgwk yhze'
        recipient_email = 'DavidSau43@gmail.com'

        # Create a message object
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = 'Dataframe Attachment'

        # Attach the DataFrame as a CSV file
        csv_data = stacked_df.to_csv(index=False)
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(csv_data)
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', "attachment; filename=your_data.csv")
        msg.attach(attachment)

        # Convert the message to a string
        text = msg.as_string()

        # Establish a secure connection with the SMTP server (e.g., Gmail)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()

        # Log in to your Gmail account
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, recipient_email, text)

        # Close the server connection
        server.quit()































        #df[1] = df[1].str.split('-').str[1].str.strip()
        #df[6] = df[6].str.split('-').str[1].str.strip()
        #df.reset_index(drop=True, inplace=True)

        #stacked_df = pd.concat([df[[1, 6]], df[[2, 7]]], axis=1)
        #stacked_df = pd.melt(df, value_vars=[1, 6, 2, 7], var_name='Variable', value_name='Stacked')


        #print(df)
        
        #all_times = pd.concat([df[1], df[6]])

        #all_times = all_times.apply(pd.to_datetime, format='%H:%M')
        #all_times = all_times.sort_values()
        
        #all_times = all_times.dt.strftime('%H:%M')

        #print(all_times)
        
    else:
        print("No table found on the page.")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
