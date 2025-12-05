import pandas as pd
import numpy as np

def validate_submission():
    print("Validating submission.csv...")
    
    # Load Data
    try:
        submission = pd.read_csv('submission.csv')
        demand = pd.read_csv('demand.csv')
        emissions_targets = pd.read_csv('carbon_emissions.csv')
        vehicles_fuels = pd.read_csv('vehicles_fuels.csv')
        fuels = pd.read_csv('fuels.csv')
        vehicles = pd.read_csv('vehicles.csv')
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        return

    # Pre-process Data
    # 1. Demand
    demand_dict = demand.set_index(['year', 'size', 'distance'])['demand'].to_dict()
    
    # 2. Emissions
    emissions_target_dict = emissions_targets.set_index('year')['carbon_emission'].to_dict()
    
    # 3. Consumption & Emissions Factors
    vf_df = vehicles_fuels.copy()
    vf_df['vehicle_type'] = vf_df['id'].apply(lambda x: x.split('_')[0])
    vf_df['size'] = vf_df['id'].apply(lambda x: x.split('_')[1])
    vf_df['year'] = vf_df['id'].apply(lambda x: int(x.split('_')[2]))
    consumption = vf_df.set_index(['vehicle_type', 'size', 'year', 'fuel'])['consumption'].to_dict()
    
    fuels_df = fuels.set_index(['fuel', 'year'])
    fuel_emissions = fuels_df['emissions'].to_dict()

    # 4. Vehicle Range
    vehicles_df = vehicles.set_index(['vehicle', 'size', 'year'])
    vehicle_range = vehicles_df['yearly_range'].to_dict()

    # Validation Flags
    all_passed = True
    
    # ---------------------------------------------------------
    # Check 1: Demand Satisfaction
    # ---------------------------------------------------------
    print("\nChecking Demand Satisfaction...")
    use_df = submission[submission['type'] == 'Use'].copy()
    
    # Helper to parse ID
    use_df['vehicle_type'] = use_df['id'].apply(lambda x: x.split('_')[0])
    use_df['size'] = use_df['id'].apply(lambda x: x.split('_')[1])
    # Note: ID year is purchase year, not current year.
    
    # Group by Year, Size, Distance
    # We need to sum (num_vehicles * distance_per_vehicle)
    use_df['total_distance'] = use_df['num_vehicles'] * use_df['distance_per_vehicle']
    
    covered_demand = use_df.groupby(['year', 'size', 'distance_bucket'])['total_distance'].sum().to_dict()
    
    demand_passed = True
    for (year, size, dist), target in demand_dict.items():
        covered = covered_demand.get((year, size, dist), 0)
        if covered < target - 1.0: # Tolerance for float errors
            print(f"FAIL: Demand not met for {year}, {size}, {dist}. Target: {target}, Covered: {covered}, Diff: {covered - target}")
            demand_passed = False
            all_passed = False
            
    if demand_passed:
        print("PASS: All demand satisfied.")

    # ---------------------------------------------------------
    # Check 2: Emission Targets
    # ---------------------------------------------------------
    print("\nChecking Emission Targets...")
    
    # Calculate emissions for each row
    def calc_row_emission(row):
        if row['type'] != 'Use':
            return 0
        
        v_type = row['id'].split('_')[0]
        size = row['id'].split('_')[1]
        v_year = int(row['id'].split('_')[2])
        
        # Consumption
        cons = consumption.get((v_type, size, v_year, row['fuel']), 0)
        
        # Emission Factor
        emis_factor = fuel_emissions.get((row['fuel'], row['year']), 0)
        
        # Total Emission = Distance * Consumption * Factor
        total_dist = row['num_vehicles'] * row['distance_per_vehicle']
        return total_dist * cons * emis_factor

    use_df['emissions'] = use_df.apply(calc_row_emission, axis=1)
    yearly_emissions = use_df.groupby('year')['emissions'].sum().to_dict()
    
    emissions_passed = True
    for year, target in emissions_target_dict.items():
        actual = yearly_emissions.get(year, 0)
        if actual > target + 1.0: # Tolerance
            print(f"FAIL: Emissions exceeded for {year}. Target: {target}, Actual: {actual}, Diff: {actual - target}")
            emissions_passed = False
            all_passed = False
            
    if emissions_passed:
        print("PASS: All emission targets met.")

    # ---------------------------------------------------------
    # Check 3: Fleet Balance
    # ---------------------------------------------------------
    print("\nChecking Fleet Balance...")
    
    # Reconstruct fleet state
    # Key: (id) -> count
    fleet_state = {} 
    
    years = sorted(submission['year'].unique())
    fleet_passed = True
    
    for year in years:
        year_data = submission[submission['year'] == year]
        
        # Process Buys
        buys = year_data[year_data['type'] == 'Buy']
        for _, row in buys.iterrows():
            vid = row['id']
            count = row['num_vehicles']
            fleet_state[vid] = fleet_state.get(vid, 0) + count
            
        # Process Sells
        sells = year_data[year_data['type'] == 'Sell']
        for _, row in sells.iterrows():
            vid = row['id']
            count = row['num_vehicles']
            if fleet_state.get(vid, 0) < count:
                print(f"FAIL: Sold more vehicles than owned in {year} for {vid}. Owned: {fleet_state.get(vid, 0)}, Sold: {count}")
                fleet_passed = False
                all_passed = False
            fleet_state[vid] = fleet_state.get(vid, 0) - count
            
        # Process Use
        uses = year_data[year_data['type'] == 'Use']
        # Sum usage by ID
        usage_counts = uses.groupby('id')['num_vehicles'].sum().to_dict()
        
        for vid, count in usage_counts.items():
            if fleet_state.get(vid, 0) < count:
                print(f"FAIL: Used more vehicles than owned in {year} for {vid}. Owned: {fleet_state.get(vid, 0)}, Used: {count}")
                fleet_passed = False
                all_passed = False
                
        # Check Range Limits
        # Distance per vehicle <= Yearly Range
        for _, row in uses.iterrows():
            vid = row['id']
            v_type = vid.split('_')[0]
            size = vid.split('_')[1]
            v_year = int(vid.split('_')[2])
            
            max_range = vehicle_range.get((v_type, size, v_year), 0)
            if row['distance_per_vehicle'] > max_range + 0.1:
                 print(f"FAIL: Vehicle {vid} exceeded range in {year}. Max: {max_range}, Used: {row['distance_per_vehicle']}")
                 fleet_passed = False
                 all_passed = False

    if fleet_passed:
        print("PASS: Fleet balance and usage limits respected.")
        
    if all_passed:
        print("\nSUCCESS: Submission is valid!")
    else:
        print("\nFAILURE: Submission contains errors.")

if __name__ == "__main__":
    validate_submission()
