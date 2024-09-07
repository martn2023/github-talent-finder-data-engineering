# Emerging-Tech Talent (Data Engineering)
This is a tool helps identify discover engineering talent. If I were a technical recruiter hunting for a "machine learning" engineer, I might want a list of engineers who:

1. have relevant repos:
   a) tags match my searched keywords e.g. "machine learning"
   b) repo was updated recently
   c) repo has at least 10 commits, a minimum file size, and was created at least 4 days ago, as a heuristic for intensity and depth 
   d) repo is externally validated by at least 1 star
   e) priority given to profiles with 2 or more relevant repos 
2. who are accessible:
   a) profiles are from an individual, not an organization
   b) GitHub profiles show a method for contacting e.g.e-mail address, personal web site, LinkedIn pages, or Twitter handles
   c) profiles deprioritized if too many followers or stars

that have relevant skills, but other recruiters haven't seen yet.

## I. Author's context:
I just finished my 1st machine learning project ([posted on GitHub](https://github.com/martn2023/housing-prices-ML-supervised-learning)), which really opened my eyes to how coming up with good systems for delivering clean data is such a big part of the data science/ML functions. My previous data engineering projects successfully collected data, but were run manually off a local machine. That created 5 issues, risks that this  __data engineering__ project addresses by escalating to a cloud-based solution:<br>
<br>
__AUTOMATION__: I'm not awake 24/7 to manually run scripts<br>
__RELIABILITY__: Automation is useless if my computer crashed between pings, or the internet connection dies<br>
__SCALABILITY__: Traffic may overwhelm my machine, which has hard limits its CPU, RAM, and hard disk space<br>
__INTEGRATION__: The addition of other tools/services may require clunky installations and management<br>
__SECURITY__: I don't want to worry about manually configuring security settings or defending against malware<br>


## II. New technologies demonstrated (100% cloud-based, not local):
#### 1. Google Cloud Function (data ingestion)
#### 2. Google Cloud SQL (data storage)
#### 3. Google BigQuery (scalable data transformation)
#### 4. Google Cloud Scheduler (task management for 1 through 4)
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
  - 80% of videos go up during only 25% of the day: 11:00 to 14:00 EST and 21:00 to 00:00 EST **WARNING: HYPOTHETICAL PLACEHOLDER VALUES**
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
