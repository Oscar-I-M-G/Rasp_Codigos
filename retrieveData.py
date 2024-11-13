import mysql.connector as mariadb

# Database configuration
db_config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': 'temperaturasdb'
}

def retrieve_data():
    try:
        # Establish a connection to the database
        conn = mariadb.connect(**db_config)
        cursor = conn.cursor()

        # Execute a SQL query to retrieve data
        query = "SELECT FECHA, HORA, HUMEDAD, TEMPERATURA FROM temperature_readings"
        cursor.execute(query)

        # Fetch all rows from the executed query
        rows = cursor.fetchall()

        # Print the data
        print("FECHA\t\tHORA\t\tHUMEDAD\t\tTEMPERATURA")
        print("------------------------------------------------------------")
        for row in rows:
            print(f"{row[0]}\t{row[1]}\t{row[2]}\t{row[3]}")

    except mariadb.Error as err:
        print(f"Error: {err}")
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    retrieve_data()