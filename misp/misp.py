import mysql.connector
import logging

mysql_host = ""
mysql_user = ""
mysql_password = ""
mysql_db = ""

logging.basicConfig(filename='error.log', level=logging.INFO)

def get_domains():
    try:
        query = """
            SELECT attributes.value1
            FROM attributes
            WHERE attributes.type = 'domain';
        """
        db = None
        db = mysql.connector.connect(
            host=mysql_host, 
            user=mysql_user, 
            password=mysql_password, 
            database=mysql_db
        )
        cursor = db.cursor()
        cursor.execute(query)
        records = cursor.fetchall()

        domains = [record[0] for record in records]
        return domains

    except Exception as e:
        logging.error(f"Error retrieving domains from database: {str(e)}")
        return [
            "example.com", # dummy value
            # "httpforever.com", # dummy value
            # "instagram.com" # dummy value
            # "youtube.com"
        ]
    
    finally:
        if db:
            db.close()

def get_sha256_hashes():
    try:
        db = None
        db = mysql.connector.connect(
            host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_db
        )
        cursor = db.cursor()
        
        query = """
            SELECT attributes.value1
            FROM attributes
            WHERE attributes.type = 'sha256';
        """
        cursor.execute(query)
        records = cursor.fetchall()

        sha256_hashes = [record[0] for record in records]
        return sha256_hashes
    except Exception as e:
        print(f"Error retrieving SHA-256 hashes: {e}")
        return [
            '0d0885660bfc31c9494a5b02964296f8472f58bdc11e5a90e7c5b4c3299fb6ea' # dummy value
        ]
    finally:
        if db:
            db.close()
