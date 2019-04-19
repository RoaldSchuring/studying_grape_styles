# Exploring Grape Styles

### Introduction

In this repository, we study the different types of wine within a given grape variety - in this case, Chardonnay. The repository contains the following notebooks and scripts:

- scraping_wine_reviews.py: this is a web scraper used to mine wine reviews from www.winemag.com
- normalizing_text.py: this is a file that contains functions for normalizing the text in the wine reviews
- wine_visuals.py: this file contains functions used to produce various data visualizations throughout the notebook
- Studying Grape Variety.ipynb: this is the notebook file containing the analysis

The data obtained from the web scraping exercise has been stored in the following file:

- data/all_scraped_wine_info_chardonnay.csv

The following file contains the full mapping of preprocessed wine descriptors to the level 1, 2 and 3 descriptors mentioned in the notebook.

- wine_term_mapping.csv

### Technologies

- Python
- Jupyter Notebook
- The necessary Python package versions needed to run the various files in this repository have been listed out in the accompanying requirements.txt file

### Project Description

As mentioned above, in this project we use We cover a new & refined way of generating descriptors from our raw dataset based on wine theory. Subsequently, we generate features from the extracted set of descriptors, and use clustering methods friendly to categorical data to find how many distinct types of Chardonnay may exist. Finally, we do some exploratory data analysis to learn more about the characteristics of each of the derived clusters. 

### Getting Started

1. Clone this repo

2. Run scraping_wine_reviews.py to get a fresh set of wine descriptions, or alternatively just use the data file data/all_scraped_wine_info_chardonnay.csv containing the already-scraped data.

3. Run the notebook file as you please!

### Authors

Roald Schuring
