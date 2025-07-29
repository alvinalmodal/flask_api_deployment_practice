# app.py
# A sample Flask API with endpoints to interact with a PostgreSQL database.

import os
import psycopg2
from flask import Flask, request, jsonify

# Initialize the Flask application
os.environ['DATABASE_HOST'] = 'flask-db-instance.cw16m6ouk4nw.us-east-1.rds.amazonaws.com'
os.environ['DATABASE_NAME'] = 'flaskdb'
os.environ['DATABASE_USER'] = 'flaskadmin'
os.environ['DATABASE_PASSWORD'] = 'Admin123456!'

app = Flask(__name__)


def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=os.environ.get('DATABASE_HOST'),
            database=os.environ.get('DATABASE_NAME'),
            user=os.environ.get('DATABASE_USER'),
            password=os.environ.get('DATABASE_PASSWORD'),
            connect_timeout=5  # Add a connection timeout
        )
        return conn
    except psycopg2.OperationalError as e:
        # This error is caught if the database is not available
        print(f"Could not connect to database: {e}")
        return None


@app.route('/')
def index():
    """Root endpoint to check if the API is running."""
    return "<h1>Flask API is running!</h1><p>Use the /items endpoint to interact with the database.</p>"


@app.route('/init_db')
def init_db():
    """
    An endpoint to initialize the database by creating an 'items' table.
    This is useful for the first run.
    """
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with conn.cursor() as cur:
            # Drop table if it exists to start fresh
            cur.execute('DROP TABLE IF EXISTS items;')
            # Create a new table
            cur.execute('CREATE TABLE items (id serial PRIMARY KEY,'
                        'name VARCHAR(100) NOT NULL,'
                        'description TEXT);'
                        )
            # Add some sample data
            cur.execute("INSERT INTO items (name, description) VALUES (%s, %s)",
                        ('My First Item', 'This is a sample item.'))
            cur.execute("INSERT INTO items (name, description) VALUES (%s, %s)",
                        ('Another Item', 'This is another sample item.'))
        conn.commit()
        return "Database initialized with 'items' table and sample data."
    except Exception as e:
        return f"An error occurred during DB initialization: {e}", 500
    finally:
        if conn:
            conn.close()


@app.route('/items', methods=['GET'])
def get_items():
    """Fetches all items from the database."""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id, name, description FROM items;')
            items = cur.fetchall()

            # Convert list of tuples to list of dictionaries
            item_list = []
            for item in items:
                item_list.append({
                    "id": item[0],
                    "name": item[1],
                    "description": item[2]
                })

        return jsonify(item_list)
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
    finally:
        if conn:
            conn.close()


@app.route('/items', methods=['POST'])
def add_item():
    """Adds a new item to the database."""
    new_item = request.get_json()
    if not new_item or not 'name' in new_item:
        return jsonify({"error": "Invalid request. 'name' is required."}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO items (name, description) VALUES (%s, %s) RETURNING id;",
                        (new_item['name'], new_item.get('description')))
            new_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({"id": new_id, **new_item}), 201
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
    finally:
        if conn:
            conn.close()

# --- requirements.txt ---
# Make sure your requirements.txt file includes these packages.

# Flask==2.2.2
# gunicorn==20.1.0
# psycopg2-binary==2.9.5
