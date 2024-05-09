import requests
import discord
from discord.ext import commands 
from bs4 import BeautifulSoup

# Webscrape a bracket url and return the seeds and team members
# Format for teams in the bracket need to be inputted as follows:
# [Seed 1] discordID/discordID
# [Seed 2] discordID/discordID
# [Seed 3] discordID/discordID
# ...
def scrape_bracket(client):
    # url = "https://brackethq.com/b/8lovb/"
    url = "https://brackethq.com/b/f2mzb/"
    html = requests.get(url)

    # Write the HTML content to a file
    with open("html_content.html", "w", encoding="utf-8") as file:
        file.write(html.text)

    soup = BeautifulSoup(html.content, "html.parser")

    # Find specific elements by their tags, attributes, or classes
    # For example, let's say you want to extract all <div> tags with class="participant-name"
    div_tags_with_class = soup.find_all("div", class_="participant-name")

    # Once you have found the desired elements, you can extract their text or attributes
    for i, tag in enumerate(div_tags_with_class, start=1):
        input_tag = tag.find("input")  # Find the <input> tag within the <div> tag
        name = f"Seed {i}"  # Set the name as "seed #" where # is the index
        value = input_tag["value"]  # Get the value of the "value" attribute
        print(f"{name}: {value}")

    # Write the HTML content to a file
    with open("html_content.html", "w", encoding="utf-8") as file:
        file.write(html.text)

    print("HTML content has been written to html_content.html")

    return div_tags_with_class