from bs4 import BeautifulSoup
import requests
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor
from timeit import default_timer
import re #split op basis van reguliere expressie

import asyncio
import nest_asyncio

from tornado.platform.asyncio import AnyThreadEventLoopPolicy
asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())

nest_asyncio.apply()
#https://stackoverflow.com/questions/46827007/runtimeerror-this-event-loop-is-already-running-in-python

results = {} #Dictionary

def getSiteSubjects(series):
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(getSiteSubjects_asynchronous(series))
    loop.run_until_complete(future)
    return results


async def getSiteSubjects_asynchronous(series):
    with ThreadPoolExecutor(max_workers=10) as executor:
        with requests.Session() as session:
            # Set any session parameters here before calling `fetch`

            # Initialize the event loop        
            loop = asyncio.get_event_loop()
            
            # Set the START_TIME for the `fetch` function
            START_TIME = default_timer()
            
            # Use list comprehension to create a list of
            # tasks to complete. The executor will run the `fetch`
            # function for each csv in the csvs_to_fetch list
            tasks = [
                loop.run_in_executor(
                    executor,
                    fetch,
                    *(session, domain)
                )
                for domain in series
            ]
            
            # Initializes the tasks to run and awaits their results
            for response in await asyncio.gather(*tasks):
                pass

def fetch(session, domain):
    try:
        url = 'https://' + domain
        with session.get(url) as response:
            soup = BeautifulSoup(response.content, "html")
            meta = soup.findAll('meta')
            subjects = []
            for tag in meta:
                if 'name' in tag.attrs.keys() and tag.attrs['name'].strip().lower() in ['keywords', 'description']:
                    subjects.append(re.split('\s|(?<!\d)[,.](?!\d)', tag.attrs['content'].lower()))
            results[domain] = subjects
    except Exception as exc:
        print("Someting went wrong when retrieving tags for " + domain)