import pandas as pd
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import coo_matrix
import sys

def load_data():
    print("Loading data...")
    data = {}
    data['carbon_emissions'] = pd.read_csv('carbon_emissions.csv')
    data['demand'] = pd.read_csv('demand.csv')
    data['vehicles'] = pd.read_csv('vehicles.csv')
    data['fuels'] = pd.read_csv('fuels.csv')
    data['vehicles_fuels'] = pd.read_csv('vehicles_fuels.csv')
    data['cost_profiles'] = pd.read_csv('cost_profiles.csv')
    print("Data loaded.")
    return data

class OptimizationModel:
    def __init__(self):
        self.var_names = []
        self.var_types = [] # 0 for continuous, 1 for integer
        self.lbs = []
        self.ubs = []
        self.obj_coeffs = []
        self.var_map = {}
        
        self.constraints_rows = []
        self.constraints_cols = []
        self.constraints_vals = []
        self.constraints_lbs = []
        self.constraints_ubs = []
        self.constraint_count = 0

    def add_variable(self, name, var_type='continuous', lb=0, ub=np.inf, obj=0):
        idx = len(self.var_names)
        self.var_names.append(name)
        self.var_types.append(1 if var_type == 'integer' else 0)
        self.lbs.append(lb)
        self.ubs.append(ub)
        self.obj_coeffs.append(obj)
        self.var_map[name] = idx
        return idx

    def add_constraint(self, terms, sense, rhs):
        # terms: list of (coeff, var_idx)
        # sense: '==', '<=', '>='
        # rhs: value
        
        row_idx = self.constraint_count
        self.constraint_count += 1
        
        for coeff, var_idx in terms:
            self.constraints_rows.append(row_idx)
            self.constraints_cols.append(var_idx)
            self.constraints_vals.append(coeff)
            
        if sense == '==':
            self.constraints_lbs.append(rhs)
            self.constraints_ubs.append(rhs)
        elif sense == '<=':
            self.constraints_lbs.append(-np.inf)
            self.constraints_ubs.append(rhs)
        elif sense == '>=':
            self.constraints_lbs.append(rhs)
            self.constraints_ubs.append(np.inf)

    def solve(self):
        print(f"Solving with {len(self.var_names)} variables and {self.constraint_count} constraints...")
        
        c = np.array(self.obj_coeffs)
        integrality = np.array(self.var_types)
        bounds = Bounds(self.lbs, self.ubs)
        
        A = coo_matrix((self.constraints_vals, (self.constraints_rows, self.constraints_cols)), 
                       shape=(self.constraint_count, len(self.var_names)))
        
        constraints = LinearConstraint(A, self.constraints_lbs, self.constraints_ubs)
        
        res = milp(c=c, constraints=constraints, integrality=integrality, bounds=bounds, 
                   options={'disp': True, 'time_limit': 300, 'mip_rel_gap': 0.05})
        
        return res

def solve_optimization():
    data = load_data()
    model = OptimizationModel()
    
    # Sets
    years = sorted(data['carbon_emissions']['year'].unique())
    sizes = sorted(data['demand']['size'].unique())
    distances = sorted(data['demand']['distance'].unique())
    vehicle_types = sorted(data['vehicles']['vehicle'].unique())
    fuels = sorted(data['fuels']['fuel'].unique())
    
    # Parameters
    demand_dict = data['demand'].set_index(['year', 'size', 'distance'])['demand'].to_dict()
    emission_targets = data['carbon_emissions'].set_index('year')['carbon_emission'].to_dict()
    
    vehicles_df = data['vehicles'].set_index(['vehicle', 'size', 'year'])
    vehicle_cost = vehicles_df['cost'].to_dict()
    vehicle_range = vehicles_df['yearly_range'].to_dict()
    
    fuels_df = data['fuels'].set_index(['fuel', 'year'])
    fuel_cost = fuels_df['cost'].to_dict()
    fuel_emissions = fuels_df['emissions'].to_dict()
    
    vf_df = data['vehicles_fuels'].copy()
    vf_df['vehicle_type'] = vf_df['id'].apply(lambda x: x.split('_')[0])
    vf_df['size'] = vf_df['id'].apply(lambda x: x.split('_')[1])
    vf_df['year'] = vf_df['id'].apply(lambda x: int(x.split('_')[2]))
    consumption = vf_df.set_index(['vehicle_type', 'size', 'year', 'fuel'])['consumption'].to_dict()
    
    cp_df = data['cost_profiles'].set_index('end_of_year')
    resale_profile = cp_df['resale_value_percent'].to_dict()
    insurance_profile = cp_df['insurance_cost_percent'].to_dict()
    maintenance_profile = cp_df['maintenance_cost_percent'].to_dict()
    
    # Variables
    print("Creating variables...")
    
    buy_vars = {}
    sell_vars = {}
    use_vars = {}
    km_vars = {}
    fleet_vars = {}
    
    for t in years:
        for v in vehicle_types:
            for s in sizes:
                # Buy
                cost = vehicle_cost.get((v, s, t), 0)
                buy_vars[(t, v, s)] = model.add_variable(f"Buy_{t}_{v}_{s}", 'continuous', obj=cost)
                
                # Fleet (Age 0 to 10)
                for age in range(11):
                    if t - age >= 2023:
                        # Maintenance + Insurance Cost for holding fleet
                        year_bought = t - age
                        price = vehicle_cost.get((v, s, year_bought), 0)
                        maint_rate = maintenance_profile.get(age, 0) / 100.0
                        ins_rate = insurance_profile.get(age, 0) / 100.0
                        holding_cost = price * (maint_rate + ins_rate)
                        
                        fleet_vars[(t, v, s, age)] = model.add_variable(f"Fleet_{t}_{v}_{s}_{age}", 'continuous', obj=holding_cost)
                
                # Sell (Age 1 to 10)
                for age in range(1, 11):
                    if t - age >= 2023:
                        # Resale Value (Negative Cost)
                        year_bought = t - age
                        price = vehicle_cost.get((v, s, year_bought), 0)
                        resale_rate = resale_profile.get(age, 0) / 100.0
                        resale_value = -1 * price * resale_rate
                        
                        sell_vars[(t, v, s, age)] = model.add_variable(f"Sell_{t}_{v}_{s}_{age}", 'continuous', obj=resale_value)

                # Use & Km
                for d in distances:
                    for f in fuels:
                        if (v, s, t, f) in consumption:
                            # Use (Integer vehicles)
                            use_vars[(t, v, s, d, f)] = model.add_variable(f"Use_{t}_{v}_{s}_{d}_{f}", 'continuous', obj=0)
                            
                            # Km (Continuous)
                            # Fuel Cost associated with Km
                            cons = consumption[(v, s, t, f)]
                            f_cost = fuel_cost.get((f, t), 0)
                            cost_per_km = cons * f_cost
                            
                            km_vars[(t, v, s, d, f)] = model.add_variable(f"Km_{t}_{v}_{s}_{d}_{f}", 'continuous', obj=cost_per_km)

    print("Adding constraints...")
    
    # 1. Fleet Dynamics
    for t in years:
        for v in vehicle_types:
            for s in sizes:
                # Age 0
                # Fleet(t, 0) - Buy(t) == 0
                model.add_constraint([
                    (1, fleet_vars[(t, v, s, 0)]),
                    (-1, buy_vars[(t, v, s)])
                ], '==', 0)
                
                # Age 1 to 10
                for age in range(1, 11):
                    if t - age >= 2023:
                        # Fleet(t, age) - Fleet(t-1, age-1) + Sell(t, age) == 0
                        # Note: Sell is removed from fleet.
                        # Fleet(t) = Fleet(t-1) - Sell(t)
                        # So Fleet(t) + Sell(t) - Fleet(t-1) == 0
                        
                        terms = [
                            (1, fleet_vars[(t, v, s, age)]),
                            (1, sell_vars[(t, v, s, age)])
                        ]
                        
                        if t > 2023:
                            terms.append((-1, fleet_vars[(t-1, v, s, age-1)]))
                        else:
                            # t=2023, age>=1 means bought before 2023.
                            # We assume starting fleet is 0.
                            # So Fleet(2023, age>0) should be 0.
                            # And Sell(2023, age>0) should be 0.
                            # The constraint naturally enforces this if Fleet(t-1) is treated as 0.
                            pass
                            
                        model.add_constraint(terms, '==', 0)
                        
                        # Can't sell more than available
                        # Sell(t, age) <= Fleet(t-1, age-1)
                        if t > 2023:
                            model.add_constraint([
                                (1, sell_vars[(t, v, s, age)]),
                                (-1, fleet_vars[(t-1, v, s, age-1)])
                            ], '<=', 0)

    # 2. Demand Satisfaction
    for t in years:
        for s in sizes:
            for d in distances:
                # Sum(Km) == Demand
                terms = []
                for v in vehicle_types:
                    for f in fuels:
                        if (t, v, s, d, f) in km_vars:
                            terms.append((1, km_vars[(t, v, s, d, f)]))
                
                model.add_constraint(terms, '==', demand_dict[(t, s, d)])
                
                # Link Km to Use
                # Km <= Use * Range
                for v in vehicle_types:
                    for f in fuels:
                        if (t, v, s, d, f) in km_vars:
                            rng = vehicle_range.get((v, s, t), 0)
                            model.add_constraint([
                                (1, km_vars[(t, v, s, d, f)]),
                                (-rng, use_vars[(t, v, s, d, f)])
                            ], '<=', 0)

    # 3. Usage Limit
    # Sum(Use) <= Sum(Fleet)
    for t in years:
        for v in vehicle_types:
            for s in sizes:
                use_terms = []
                for d in distances:
                    for f in fuels:
                        if (t, v, s, d, f) in use_vars:
                            use_terms.append((1, use_vars[(t, v, s, d, f)]))
                
                fleet_terms = []
                for age in range(11):
                    if (t, v, s, age) in fleet_vars:
                        fleet_terms.append((-1, fleet_vars[(t, v, s, age)]))
                
                # Sum(Use) - Sum(Fleet) <= 0
                model.add_constraint(use_terms + fleet_terms, '<=', 0)

    # 4. Emission Targets
    for t in years:
        terms = []
        for v in vehicle_types:
            for s in sizes:
                for d in distances:
                    for f in fuels:
                        if (t, v, s, d, f) in km_vars:
                            cons = consumption[(v, s, t, f)]
                            emis = fuel_emissions.get((f, t), 0)
                            coeff = cons * emis
                            terms.append((coeff, km_vars[(t, v, s, d, f)]))
                            
        model.add_constraint(terms, '<=', emission_targets[t])

    # Solve
    res = model.solve()
    print(f"Solver Status: {res.success}, Message: {res.message}")
    
    if not res.success:
        print("Optimization failed!")
        return

    # Extract Solution
    x = res.x
    submission_rows = []
    
    # Helper to get value
    def get_val(idx):
        return x[idx]
    
    # Reconstruct logic similar to before
    # ... (Logic to create submission rows)
    # Since we need to distribute usage among fleet ages, we do the same post-processing.
    
    # First, extract Buy/Sell
    for t in years:
        for v in vehicle_types:
            for s in sizes:
                # Buy
                idx = buy_vars[(t, v, s)]
                val = int(round(get_val(idx)))
                if val > 0:
                    vid = f"{v}_{s}_{t}"
                    submission_rows.append({
                        'year': t, 'id': vid, 'num_vehicles': val, 'type': 'Buy',
                        'fuel': '', 'distance_bucket': '', 'distance_per_vehicle': ''
                    })
                
                # Sell
                for age in range(1, 11):
                    if (t, v, s, age) in sell_vars:
                        idx = sell_vars[(t, v, s, age)]
                        val = int(round(get_val(idx)))
                        if val > 0:
                            year_bought = t - age
                            vid = f"{v}_{s}_{year_bought}"
                            submission_rows.append({
                                'year': t, 'id': vid, 'num_vehicles': val, 'type': 'Sell',
                                'fuel': '', 'distance_bucket': '', 'distance_per_vehicle': ''
                            })
    
    # Post-process Use
    final_submission = list(submission_rows)
    
    for t in years:
        # Build Fleet Pool
        fleet_pool = {}
        for v in vehicle_types:
            for s in sizes:
                pool = []
                # Check Fleet vars
                # Note: Fleet vars are end of year.
                # But we need available for use.
                # Available = Fleet[t] + Sell[t] (since Sell removed it from Fleet[t])
                # Or Fleet[t-1] + Buy[t].
                # Let's use Fleet[t-1] + Buy[t].
                
                # From prev year
                if t > 2023:
                    for age in range(11):
                        if (t-1, v, s, age) in fleet_vars:
                            idx = fleet_vars[(t-1, v, s, age)]
                            count = int(round(get_val(idx)))
                            if count > 0:
                                year_bought = (t-1) - age
                                vid = f"{v}_{s}_{year_bought}"
                                pool.append({'id': vid, 'count': count})
                
                # Buy
                idx = buy_vars[(t, v, s)]
                bought = int(round(get_val(idx)))
                if bought > 0:
                    vid = f"{v}_{s}_{t}"
                    pool.append({'id': vid, 'count': bought})
                
                fleet_pool[(v, s)] = pool

        # Assign Tasks
        for v in vehicle_types:
            for s in sizes:
                for d in distances:
                    for f in fuels:
                        if (t, v, s, d, f) in use_vars:
                            idx_use = use_vars[(t, v, s, d, f)]
                            idx_km = km_vars[(t, v, s, d, f)]
                            
                            needed = int(round(get_val(idx_use)))
                            total_km = get_val(idx_km)
                            
                            if needed > 0:
                                avg_km = total_km / needed
                                remaining_needed = needed
                                pool = fleet_pool.get((v, s), [])
                                
                                for item in pool:
                                    if item['count'] > 0 and remaining_needed > 0:
                                        take = min(item['count'], remaining_needed)
                                        final_submission.append({
                                            'year': t, 'id': item['id'], 'num_vehicles': take,
                                            'type': 'Use', 'fuel': f, 'distance_bucket': d,
                                            'distance_per_vehicle': avg_km
                                        })
                                        item['count'] -= take
                                        remaining_needed -= take
    
    df_sub = pd.DataFrame(final_submission)
    df_sub = df_sub[['year', 'id', 'num_vehicles', 'type', 'fuel', 'distance_bucket', 'distance_per_vehicle']]
    df_sub.to_csv('submission.csv', index=False)
    print("Submission saved to submission.csv")

if __name__ == "__main__":
    solve_optimization()
