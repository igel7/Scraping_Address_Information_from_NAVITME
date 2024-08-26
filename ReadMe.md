# Code Description
- Scrapes and collectively retrieves the store address information of specific types of businesses from the NAVITIME website.
- Any category listed on NAVITIME, such as convenience stores or schools, can be targeted.

# Technical Innovations
- Since NAVITIME displays results on a maximum of 50 pages, dealing with prefectures that have more than 750 results (15 entries per page multiplied by 50 pages) requires a different approach.
- Prefectures with more than 750 search results are handled with a separate process, where information is retrieved on a city, town, or village basis.
- As city, town, and village codes vary by prefecture and processing at this level is time-consuming, using both prefecture-level and local-level processing helps to balance speed and comprehensiveness (hopefully).
