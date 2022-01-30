import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import pandas as pd
import numpy as np
from datetime import datetime

chore_schedule = pd.read_csv("chore_schedule.csv")
chore_schedule = chore_schedule.drop("Unnamed: 0", axis=1)
idx = ["Frequency", "Countdown", "Calendar", "Turn"]
chore_schedule.index = idx

chore_schedule.loc["Frequency"] = chore_schedule.loc["Frequency"].apply(int)
chore_schedule.loc["Countdown"] = chore_schedule.loc["Countdown"].apply(int)
chore_schedule.loc["Calendar"] = chore_schedule.loc["Calendar"].apply(int)

print(chore_schedule)

def chore_manager():
    chore_schedule.loc["Countdown"] = chore_schedule.loc["Countdown"] -1

    chores_today = determine_chores()
    reset_countdowns(chores_today)

    iterate_turns(chores_today)
    return assign_chores(chores_today)

def determine_chores():
    chores_today = {"Trash" : False, "Counters" : False, "Stove" : False, "Sweep/Swiffer" : False,
                    "Dish Rack" : False, "Mop Kitchen" : False, "Wipe Living/Dining Room Surfaces"  : False,
                    "Bathroom Counters/Sink" : False, "Toilet" : False, "Dish Towels" : False}
    
    frq_chores = chore_schedule.loc["Countdown"][chore_schedule.loc["Countdown"] < 0].index
    cal_chores = chore_schedule.loc["Calendar"][chore_schedule.loc["Calendar"] == datetime.today().weekday()].index
    
    for c in frq_chores:
        chores_today[c] = True
    for c in cal_chores:
        chores_today[c] = True
        
    return chores_today

def iterate_turns(ct):
    for c in ct.keys():
        if (ct[c] == True):
            chore_schedule.at["Turn", c] = iterate_turns_helper(chore_schedule.at["Turn", c])

def iterate_turns_helper(name):
    if name == "Ava":
        return "Cara"
    elif name == "Cara":
        return "Molly"
    else:
        return "Ava"

def reset_countdowns(ct):
    for c in ct.keys():
        if (ct[c] == True):
            chore_schedule.at["Countdown", c] = chore_schedule.at["Frequency", c]

def assign_chores(ct):
    assignments = {}
    for c in ct:
        if (ct[c] == True):
            assignments[c] = chore_schedule.at["Turn", c]
    
    return assignments

chores = chore_manager()
chore_schedule.to_csv("chore_schedule.csv")

def html_list(chores):
    html = ""
    for c in chores.keys():
        html += f"<ul>{c}: {chores[c]}.</ul>"
    return html

def get_adjective():
    adjectives_file = open("english-adjectives.txt", "r")
    adjectives = adjectives_file.readlines()

    return np.random.choice(adjectives)[:-1]

email_file = open("email.txt", "r")
email_text = email_file.read()

email_text = email_text.replace("CHORE_LIST", html_list(chores))
email_text = email_text.replace("WEEKDAY", datetime.today().strftime('%A'))
email_text = email_text.replace("ADJECTIVE", get_adjective())

smtp_server = "smtp.gmail.com"
port = 587  # For starttls
sender_email = "arthur.the.ai.assistant@gmail.com"
password = "aRtHuR_AI"

recipient_emails = ['augustus.lewis.doricko@gmail.com']
for recipient in recipient_emails:
    message = MIMEMultipart("alternative")
    message["Subject"] = "Daily Chores (from Arthur)"
    message["From"] = sender_email
    message["To"] = recipient

    text = "Something went wrong, I'm sorry. -Arthur"
    html = email_text.replace("\n", "")

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
        sender_email, recipient, message.as_string()
    )