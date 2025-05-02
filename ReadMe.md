[日本語はこちら](ReadMe_ja.md)

## Code Description
- This script scrapes store information (such as address, phone number, etc.) in bulk from the NAVITIME website using `beautifulsoup4`.
- You can target any category listed on NAVITIME, such as convenience stores, schools, etc.

## How to Use
- Simply run the script, and a result file named `kekka_yymmdd_hhmm.txt` will be generated in the same folder where `navitime_sc.py` is located.
- The output file will contain facility names, addresses, and phone numbers, separated by the delimiter `|`.
- **Important:** As noted in the comments in the code, the URL marked with `★★★` must be updated based on the target category you wish to scrape.

```python
# -------------Usage Notes--------------
# To change the target category (e.g., Seven-Eleven, pachinko, etc.),
# go to this NAVITIME page: https://www.navitime.co.jp/category/
# Select the desired category and replace the URL in the script marked with ★★★.
# The current setting uses the URL for amusement parks.
# --------------------------------------
```

- In other words, visit the [NAVITIME category page](https://www.navitime.co.jp/category/),  
  choose the category you want (e.g., amusement parks, Seven-Eleven, golf, etc.), and copy its URL.

- For example, if you select "Amusement Parks", click here:

![Screenshot 2025-05-02 202010](https://github.com/user-attachments/assets/6f5c31b6-dbe7-495f-99b0-fe16d2c00867)

- Then copy the URL:

![Screenshot 2025-05-02 202327](https://github.com/user-attachments/assets/7ac5df30-2f0f-4d30-9117-c3b89647fe7a)

- And paste it into the following part of the script:

```python
# Set the base URL for the target category as a global variable ★★★
BASE_CATEGORY_URL = "https://www.navitime.co.jp/category/0101001/"
```

- After that, just run the script normally.

## Technical Considerations
- NAVITIME limits search results to a maximum of 50 pages.  
  Since each page shows 15 entries, the maximum total per query is 750 results.
- For prefectures that exceed 750 results, the script switches to a separate process that collects data by municipality.
- Since municipality codes vary by prefecture and retrieving data by municipality is time-consuming,  
  the script smartly chooses between prefecture-level and municipality-level scraping to balance speed and completeness (as much as possible).
