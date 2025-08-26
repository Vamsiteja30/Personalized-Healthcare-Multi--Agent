import sqlite3, os, json, random
from pathlib import Path
from faker import Faker

# Initialize Faker for realistic data generation
fake = Faker()

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "healthcare.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Use Faker for realistic names and cities
def generate_realistic_names():
    """Generate realistic Indian names using Faker"""
    names = []
    for _ in range(50):  # Generate more names for variety
        # Mix of Indian and international names for diversity
        if random.choice([True, False]):
            # Indian names
            first_name = fake.first_name()
            last_name = fake.last_name()
        else:
            # International names
            first_name = fake.first_name()
            last_name = fake.last_name()
        names.append((first_name, last_name))
    return names

def generate_realistic_cities():
    """Generate realistic cities using Faker"""
    cities = []
    # Mix of Indian and international cities
    indian_cities = ["Mumbai", "Delhi", "Hyderabad", "Bengaluru", "Chennai", "Kolkata", "Pune", "Ahmedabad"]
    international_cities = [fake.city() for _ in range(10)]
    cities.extend(indian_cities)
    cities.extend(international_cities)
    return cities

# Generate realistic data
realistic_names = generate_realistic_names()
realistic_cities = generate_realistic_cities()

diets = ["vegetarian", "non-vegetarian", "vegan"]
conditions_pool = ["Type 2 Diabetes", "Hypertension", "High Cholesterol", "Hypothyroidism", "PCOS", "Asthma", "Arthritis", "Depression"]

def main():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            city TEXT,
            dietary_preference TEXT,
            medical_conditions TEXT,
            physical_limitations TEXT
        )
    """)
    cur.execute("DELETE FROM users")
    
    for i in range(1, 101):
        # Use Faker-generated names
        first_name, last_name = random.choice(realistic_names)
        
        # Use Faker-generated cities
        city = random.choice(realistic_cities)
        
        # Ensure balanced dietary distribution (≈33 each)
        if i <= 33:
            diet = "vegetarian"
        elif i <= 66:
            diet = "non-vegetarian"
        else:
            diet = "vegan"
        
        # Generate medical conditions (0-3 conditions per user)
        num_conditions = random.choices([0, 1, 2, 3], weights=[0.3, 0.4, 0.2, 0.1])[0]
        conditions = random.sample(conditions_pool, k=num_conditions) if num_conditions > 0 else []
        
        # Ensure Type 2 Diabetes users get appropriate representation
        if "Type 2 Diabetes" in conditions and i % 7 == 0:  # Every 7th user with diabetes
            conditions.append("High Cholesterol")  # Common comorbidity
        
        # Physical limitations (mostly none, some realistic ones)
        limitations = ["none"] if random.random() > 0.1 else random.choice([
            ["mobility issues"], ["swallowing difficulties"], ["vision problems"], ["hearing impairment"]
        ])
        
        cur.execute("""
            INSERT INTO users(id, first_name, last_name, city, dietary_preference, medical_conditions, physical_limitations)
            VALUES(?,?,?,?,?,?,?)
        """, (i, first_name, last_name, city, diet, json.dumps(conditions), json.dumps(limitations)))

    con.commit()
    con.close()
    print(f"✅ Created DB at: {DB_PATH} with 100 users using Faker for realistic data generation.")
    print(f"📊 Generated {len(set(realistic_names))} unique names and {len(set(realistic_cities))} cities")

if __name__ == "__main__":
    main()
