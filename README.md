# YouTube (Data Engineering)

## I. Author's context:
After building out 3 CRUD web apps, I wanted to expand my horizons. I just finished my first 1 machine learning project ([posted on GitHub](https://github.com/martn2023/housing-prices-ML-supervised-learning)), which really opened my eyes to how coming up with good systems for delivering clean data is such a big part of the data science/ML functions. For this reason, I picked a __data engineering__ project.

- the ability to extract data from a source
- extract it via scheduled automation
- use of scalable tools beyond what you would see in a toy project running off a local machine
- automated cleaning and transformation of data
- some novel analysis of data beyond merely reporting counts e.g. sentiment analysis of video titles
- a dashboard to visually prove the aforementioned

## II. New technologies demonstrated (100% cloud-based, not local):
#### 1. Apache Kafka (data ingestion)
#### 2. Apache Spark (data transformation)
#### 3. Apache Airflow (task manager for 1 and 2)
#### 4. Google Cloud SQL (database)
#### 5. Grafana (data visualization)


## III. Process
### (A) DATA ENGINEERING (80%):
#### 1. Data source, field selection, and extraction:
  - YouTube has a free API
  - Used Apache Kafka to look at YouTube's newest videos every hour and pull information e.g. url, title, author, description text, and video length
  - Decided on cloud-based version to demonstrate robust systems that:
    - have uptime and reliability: what happens if I try to save money by running this on my local machine, and it's turned off during the hourly data pull? Or it crashes mid-pull?
    - show fault tolerance: it handles failures (network issues, rate limiters) with retries and logging
    - are scalable: an individual search may yield 1,000 different videos, but I wanted to build the system that can handle > 1,000,000 videos a day

  #### 2. Data Preparation:
  - Using Apache Spark in the cloud instead of manually cleaning data ad hoc with Python scripts (CAUTION)
  - Cleaning data e.g. removing non-English results or removing duplicates
  - Transforming data e.g. encoding content tags and conducting sentiment analysis

  #### 3. Storing data in a cloud-based database:
  - I've done Postgres and Mongo databases on my local drive before, but now I need something reliable in the cloud
  - I considered Amazon RDS due to its market share, but went with Google Cloud SQL to optimize for ease-of-use

  #### 4. Managing above tasks:
  - Configuring Apache Airflow to have scheduled data pulls (#1) , data transformations (#2) and data storage (#3)
 
### (b) DATA ANALYSIS (20%):
#### 5. Statistical analysis, pattern recognition:
  - It seems there is a huge gap in the tone of videos put out depending on the search topic

#### 6. Data visualization:
  - I considered Tableau due to my past certifications in it, but went with Graphana


## IV. Screenshots (illustrative, but not comprehensive):

Findings are presented in 


## V. Learnings:
- Hosting can get expensive!


## VI. Potential improvements:
>**Product/UI:**<br>
- This was run on a budget. With the larger needs and budget of a Big Tech employer, we could have done grabbed more videos (searching further back in time) or grabbed videos about even more topics, for example:<br>
 -- every single politician running for a presidency, governorship, senate seat, house rep, or mayoral position<br>
 -- spread across every most countries<br>

>**Tools**<br>
- Introducing NiFI to the start of the process chain
- Introducing Hadoop to the end of the process chain
