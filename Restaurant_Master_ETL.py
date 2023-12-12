import subprocess
import sys

def run_script(script_path, city, state):
    command = [sys.executable, script_path, "--city", city, "--state", state]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing {script_path}: {e}")
    
def main():
    if len(sys.argv) != 3:
        print("Usage: python main_script.py <city> <state>")
        sys.exit(1)

    city = sys.argv[1]
    state = sys.argv[2]

    print(f"Pulling data for {city}, {state}...")
    run_script('yelp_data_scrape.py', city, state)
    sys.exit(1)
    
    print(f"Loading data into database...")
    run_script('load_restaurant_data.py', city, state)
    sys.exit(1)

    print("ETL Process Finished.")

if __name__ == "__main__":
    main()
