# README.md

This is _Web of Science_ spider that can search paper detail including IF and citation with respect to given author name and paper list.

## Usage

1. Install [ChromeDriver](https://chromedriver.chromium.org/)
2. Replace `PaperList.txt` and `AuthorName` in `wos_spider.py` with your own. In `PaperList.txt`, the interested
   paper should be listed by lines

   ``` Python
   # configuration
   paper_list_name = 'PaperList.txt'
   author_name = 'AuthorName'
   ```

3. Run `wos_spider.py`

## Result format

``` YAML
paper1:
  Citation: 0
  CiteDetail: []
  IF: 2.779
  Journal: SIGNAL PROCESSING-IMAGE COMMUNICATION
  Paper: XXXXXX
  Rank: Q2
  SearchTitle: XXXXXX
  Sort:
  - ENGINEERING, ELECTRICAL & ELECTRONIC 109/266 Q2
  address:
  - XXXXXX
  authors:
  - XXXXXX
  - XXXXXX
  - XXXXXX
  date: SEP 2020
```
