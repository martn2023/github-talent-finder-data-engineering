# I. Author's context:
- While doing 2 data analytics projects, I was pulling data to my local machine on an ad hoc basis. That strategy lacks the automation, reliability, scalability, integration ease, and security needed for a continuous stream of data.

- This __data engineering__ project addresses all 5 concerns by __upgrading to a 100% cloud-based solution__. The resulting tool helps technical recruiters identify candidates with relevant GitHub repos.

# II. What I built/New tech used:
## 1. Fully cloud-based ETL pipeline (80%)
### Data Ingestion
Runs my scripts in __Google Cloud Function__ instead of a local machine i.e. no downtime from machine crashed, power outages, or internet disruptions
<br>
<br>
### Data Storage
Runs an expandable database __Google Cloud SQL__, which is no longer limited by a machine's disk space
<br>
<br>
### Data Preparation
Does large-scale data cleanings and transformations __BigQuery__, where a local solution was constrained by processing power, memory, or the Pandas' use case
<br>
<br>
### Automated Task Management
Uses __Google Cloud Scheduler__ to invoke aforementioned processes on a schedule and deal with retries
<br>
<br>
## 2. Leveraging resulting data (20%)
### Dashboards
Uses __Graphana__ for real-time data visualization without uptime concerns
<br>
<br>
### Data Analysis
- Which are topics were most updated in the last 30 days?
- How does this compare with what people are appreciating through stars?
- Which engineers appear to be the ripest, underrated, and approachable candidates?
- Do repo updates spike during a certain time(s) of day?
<br>
<br>

# III. Defining "good" engineers:
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

# IV. Screenshots (illustrative, but not comprehensive):
Findings are presented in screenshots below:


# V. Learnings:
- Hosting can get expensive!

# VI. Potential improvements:
>**Product/UI:**<br>
- This was run on a budget. With the larger needs and budget of a Big Tech employer, we could have done grabbed more videos (searching further back in time) or grabbed videos about even more topics, for example:<br>
  - every single politician running for a presidency, governorship, senate seat, house rep, or mayoral position<br>
  - spread across every most countries

>**Tools**<br>
- Introducing __NiFI__ to the start of the process chain
- Introducing __Hadoop__ to the end of the process chain
