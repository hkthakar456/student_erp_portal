import os
from dotenv import load_dotenv
from app import create_app
from seed import seed_database

load_dotenv()

config_name = os.environ.get("FLASK_ENV", "development")
app = create_app(config_name)

@app.cli.command("seed-db")
def seed_db_command():
    """CLI command to seed the database with fictional records."""
    seed_database(app.config["DATABASE_PATH"])
    print("Database seeding completed.")

if __name__ == "__main__":
    # Ensure database exists and is seeded if not present
    db_file = app.config.get("DATABASE_PATH")
    if db_file != ":memory:" and not os.path.exists(db_file):
        print(f"Database not found at {db_file}. Running initial seed...")
        seed_database(db_file)

    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "True").lower() in ("true", "1", "t")
    print(f"Starting Student Management Portal on http://127.0.0.1:{port} (Debug={debug})")
    app.run(host="127.0.0.1", port=port, debug=debug)
