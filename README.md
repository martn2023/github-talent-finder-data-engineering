# YouTube (Data Engineering)

## I. Author's context:
After building out 3 CRUD web apps, I wanted to expand my horizons. I just finished my first 1 machine learning project ([posted on GitHub](https://github.com/martn2023/housing-prices-ML-supervised-learning)), which really opened my eyes to how coming up with good systems for delivering clean data is such a big part of the data science/ML functions. For this reason, I picked a __data engineering__ project.

## II. New technologies demonstrated (100% cloud-based, not local):
#### 1. Apache Kafka (data ingestion)
#### 2. Apache Spark (data transformation)
#### 3. Apache Airflow (task manager for 1 and 2)
#### 4. Google Cloud SQL (database)
#### 5. Grafana (data visualization)


## III. Process
### (A) DATA ENGINEERING (80%):
#### 1. Data Ingestion Pipeline:
  - YouTube has a free API
  - Used __Apache Kafka__ to look at YouTube's newest videos every hour and pull information e.g. url, title, author, description text, and video length
  - Decided on cloud-based version to demonstrate robust systems that:
    - have uptime and reliability: what happens if I try to save money by running this on my local machine, and it's turned off during the hourly data pull? Or it crashes mid-pull?
    - show fault tolerance: it handles failures (network issues, rate limiters) with retries and logging
    - are scalable: an individual search may yield 1,000 different videos, but I wanted to build the system that can handle > 1,000,000 videos a day

  #### 2. Data Processing Pipeline:
  - Data cleaning:
    - Using __Apache Spark__ in the cloud instead of manually cleaning data ad hoc with Python scripts (CAUTION)
    - Spark removes non-English results
    - Spark removes duplicates
  - Data transformation:
    - Spark encodes content
    - Outside of Spark, the NLP library __VADER conducts sentiment analysis__ on video titles

  #### 3. Data Storage Pipeline:
  - I've done Postgres and Mongo databases on my local drive before, but now I need something reliable in the cloud
  - I considered Amazon RDS due to its market share, but went with __Google Cloud SQL__ to optimize for ease-of-use
  - Prepared data, including sentiment analysis scores (video title polarity) now loaded to database

  #### 4. Task Orchestration Pipeline:
  - Configured __Apache Airflow__ to:
    - have scheduled:
      - data pulls with Kafka
      - data transformations with Spark
      - data storage with Google Cloud SQL
    - recognize failed/interrupted tasks and re-invoke pipelines
 
### (b) DATA ANALYSIS (20%):
#### 5. Statistical Analysis + Pattern Recognition:
  - It seems there is a huge gap in the tone of videos put out depending on the search topic

#### 6. Data Visualization:
  - I considered Tableau due to my past certifications in it, but went with __Graphana__
  - Volume of videos by keyword searched
  - Video title sentiment by keyword searched
  - Volume of videos throughout the day

#### 7. Findings:
  - 80% of videos go up during only 25% of the day: 11:00 to 14:00 EST and 21:00 to 00:00 EST
    - Keep in mind that YouTube is a North American company and that people in other time zones have local alternatives
    - I wonder if this is because these times are when content creators are done with their daytime work, if they're deliberately dropping videos when their AUDIENCE is done with dinner
  - Donald Trump and Kamala Harris, the 2 nominees for this election get their share of both positive and negative video titles/headlines. However, that changes dramatically when we filter for "mainstream media channels", which I define as major news outlets based in the USA that are in the top 20 of most visited news web sites. When only focusing on major news outlets: the % of opinionated video titles that are positive: **WARNING: HYPOTHETICAL PLACEHOLDER VALUES**
    - drops from 50% positive to 10% positive on "Donald Trump"
    - rises from 50% positive to 90% positive on "Kamala Harris"

## IV. Screenshots (illustrative, but not comprehensive):

Findings are presented in screenshots below:


## V. Learnings:
- Hosting can get expensive!


## VI. Potential improvements:
>**Product/UI:**<br>
- This was run on a budget. With the larger needs and budget of a Big Tech employer, we could have done grabbed more videos (searching further back in time) or grabbed videos about even more topics, for example:<br>
 -- every single politician running for a presidency, governorship, senate seat, house rep, or mayoral position<br>
 -- spread across every most countries<br>

>**Tools**<br>
- Introducing __NiFI__ to the start of the process chain
- Introducing __Hadoop__ to the end of the process chain
