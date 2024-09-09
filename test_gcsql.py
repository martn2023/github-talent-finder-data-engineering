import mysql.connector

# Connection to Google Cloud SQL instance
connection = mysql.connector.connect(
    user='postgres',  # Your DB username (assuming you set this as 'postgres')
    password='postgres_password',  # Your DB password (replace with actual password)
    host='34.46.89.154',  # Public IP of your Cloud SQL instance
    database='first_database'  # Your database name
)

# Create a cursor object to interact with the database
cursor = connection.cursor()

# Execute a query to fetch all data from the 'github_repos' table
cursor.execute("SELECT * FROM github_repos")
results = cursor.fetchall()

# Loop through the results and print each row
for row in results:
    print(row)

# Close the connection to the database
connection.close()
