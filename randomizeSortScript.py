# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 20:05:45 2024

@author: Nathan
"""

import pandas as pd
import numpy as np
from datetime import datetime as dt, timedelta

WEEKS_BACK = 3
f = "%Y-%m-%dT%H:%M:%S.%fZ"


#create list of names from specific session
#inputs: filename, date, session, category (eg. Lottery, Waitlist, )
#output: string
def read_names_from_csv(filepath, date, session_name, join_type):
    df = pd.read_csv(filepath)
    df['start date'] = pd.to_datetime(df['start date'], format=f)
    # Find the row with the specified date
    rows = df[df['start date'] == date]
    if rows.empty:
        return []
    # Extract the rsvpers column
    row = rows[rows['name'] == skill_level]
    rsvpers = row.iloc[0]['rsvpers']
    
    # Parse the rsvpers string
    if join_type + ":" in rsvpers:
        start_index = rsvpers.index(join_type + ":") + len(join_type + ":")
        names_string = rsvpers[start_index:].strip()
        # Split by comma and strip extra whitespace
        names_list = [name.strip() for name in names_string.split(',')]
        return names_list
    return []

# add randomization of 0-1 for all prospects
#input: dataframe
#output: dataframe
def randomize_weights(df):
    # Add a column with random numbers between 0 and 1
    df['position'] += np.random.rand(len(df))
    return df

# create dataframe for all prospects
#input: string
#output: dataframe
def create_dataframe(names_list):
    # Create a DataFrame from the list of names
    df = pd.DataFrame(names_list, columns=['names'])
    # Add a column with random numbers between 0 and 1
    df['position'] = np.zeros(len(names_list))
    df['previous dates'] = pd.Series(dtype='str')
    return df

# reduce priority for prospects who attended a session recently
def subtract_from_matches(df, names, weight):
    for name in names:
        if name in df['names'].values:
            df.loc[df['names'] == name, 'position'] -= weight
    
    return df

#Find the all sessions of a single name that occurred within the last x weeks
#output: series object of dates
def find_last_weeks(filepath, date, session_name, weeks_back):
    df = pd.read_csv(filepath)
    
    # Find the row with the specified name and date
    rows = df[df['name'] == session_name]
    rows['date'] = pd.to_datetime(rows['start date'], format=f)
    
    #filter rows to make sure they're before the desired date but within the last x weeks
    before_date = rows['date'] < date
    within_delta = date - rows['date'] <= timedelta(weeks=weeks_back)
    rows = rows[before_date & within_delta]
    
    rows['date_diff'] = date - rows['date']
    
    closest_rows = rows.nsmallest(weeks_back, 'date_diff')
        
    return closest_rows['date']

def print_output(dataframe, attendee_count):
    print("Attendees:\nName\tWeight")
    i = 0
    for index, row in sorted_output.iterrows():
        print(row['names'] + ", " + str(row['position']) + "\n")
        if i < attendee_count:
            i += 1
        else:
            print("\nWaitlist:\n")


filename = "events_1059745565136654406.csv"
date_string = '2024-07-26T20:45:00.000Z'
date = dt.strptime(date_string, f)
skill_level = 'DUPR Matches 2.75 to  3.75'
attendee_count = 8

names = read_names_from_csv(filename, date, skill_level, "Lottery")
lottery = create_dataframe(names)
lottery = randomize_weights(lottery)

# go back three weeks and take list of all attendees in each of the three weeks
lastweeks = find_last_weeks(filename, date, skill_level, WEEKS_BACK)
num_sessions = lastweeks.size

for i in range(num_sessions):
    #assumes attendees are all in category "Attendees" not "Attendee"
    lastweek_names = read_names_from_csv(filename, lastweeks.iloc[i], skill_level, "Attendees")
    week_diff = (date - lastweeks.iloc[i]) / pd.Timedelta(weeks=1)
    output = subtract_from_matches(lottery, lastweek_names, WEEKS_BACK - week_diff + 1)

# add to attendees and waitlist whoever has highest number (weight)
sorted_output = output.sort_values(by='position', ascending=False)

print_output(sorted_output, attendee_count)    
sorted_output.to_csv('out.csv', index = False)
#print(names_array)