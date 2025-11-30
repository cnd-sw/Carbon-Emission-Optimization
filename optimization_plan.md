# Optimization Plan

## Problem Formulation

We will model this as a Mixed Integer Linear Programming (MILP) problem.

### Sets
- **Years ($T$)**: 2023 to 2038 (16 years)
- **Sizes ($S$)**: S1, S2, S3, S4
- **Distances ($D$)**: D1, D2, D3, D4
- **Vehicle Types ($V$)**: BEV, Diesel, LNG
- **Fuels ($F$)**: Electricity, BioLNG, HVO, LNG, B20
- **Vehicle Age ($A$)**: 0 to 10 (Vehicles are sold or scrapped after 10 years)

### Parameters
- **Demand($t, s, d$)**: Required km for year $t$, size $s$, distance $d$.
- **EmissionTarget($t$)**: Max allowable CO2 emissions in year $t$.
- **VehicleCost($v, s, t$)**: Purchase cost of vehicle $v$, size $s$ in year $t$.
- **VehicleRange($v, s$)**: Max km/year for vehicle $v$, size $s$.
- **FuelEmission($f$)**: CO2 emissions per unit of fuel $f$.
- **FuelCost($f, t$)**: Cost per unit of fuel $f$ in year $t$.
- **Consumption($v, f$)**: Fuel consumption (units/km) for vehicle $v$ using fuel $f$.
- **MaintCost($age$)**: Maintenance cost % of purchase price.
- **InsCost($age$)**: Insurance cost % of purchase price.
- **ResaleValue($age$)**: Resale value % of purchase price.

### Decision Variables
- **Buy($t, v, s$)**: Integer. Number of new vehicles of type $v$, size $s$ purchased in year $t$.
- **Sell($t, v, s, age$)**: Integer. Number of vehicles of type $v$, size $s$ and specific $age$ sold in year $t$.
- **Use($t, v, s, d, f, age$)**: Continuous/Integer. Number of vehicles of type $v$, size $s$, age $age$ used for distance bucket $d$ with fuel $f$ in year $t$.
    - *Note*: To simplify, we might aggregate usage across ages if efficiency doesn't change with age. However, we need to track age for maintenance/insurance costs.
    - *Simplification*: We can define $Fleet(t, v, s, age)$ as the number of vehicles available.
    - $Use(t, v, s, d, f)$ is the number of vehicles assigned to a task. We just need to ensure $\sum_{d,f} Use(...) \le \sum_{age} Fleet(...)$.
    - However, since we need to calculate costs which depend on age, we need to know the fleet composition.

### Constraints

1.  **Demand Satisfaction**:
    For each year $t$, size $s$, distance $d$:
    $$ \sum_{v, f} (AllocatedVehicles_{t,v,s,d,f} \times AverageDistance) \ge Demand_{t,s,d} $$
    *Refinement*: We can assume vehicles assigned to a distance bucket travel the minimum of (Demand / NumVehicles) and (VehicleRange).
    To keep it linear:
    $$ \sum_{v, f} (Use_{t,v,s,d,f} \times VehicleRange_{v,s}) \ge Demand_{t,s,d} $$
    This assumes full utilization of range. If demand is low, this might overestimate capacity, but since we minimize cost, the solver will try to match capacity to demand.
    *Correction*: We need to ensure we don't count more distance than the demand requires for the objective (fuel cost).
    Fuel Cost = $\sum TotalKm \times Consumption \times FuelCost$.
    TotalKm for a bucket = $Demand_{t,s,d}$.
    We just need to ensure we have *enough* vehicles to cover the demand.
    $$ \sum_{v, f} (Use_{t,v,s,d,f} \times VehicleRange_{v,s}) \ge Demand_{t,s,d} $$
    And Fuel Cost is calculated based on $Demand_{t,s,d}$ distributed among the selected vehicles.
    Let $Fraction_{t,v,s,d,f}$ be the fraction of demand $Demand_{t,s,d}$ met by vehicle $v$ with fuel $f$.
    This makes it non-linear or complex.
    
    *Alternative Approach*:
    Variables: $KmCovered_{t,v,s,d,f}$ (Continuous).
    Constraint: $\sum_{v,f} KmCovered_{t,v,s,d,f} = Demand_{t,s,d}$.
    Constraint: $KmCovered_{t,v,s,d,f} \le Use_{t,v,s,d,f} \times VehicleRange_{v,s}$.
    This links usage (integer vehicles) to km covered (continuous).

2.  **Fleet Balance**:
    $$ Fleet_{t,v,s,0} = Buy_{t,v,s} $$
    $$ Fleet_{t,v,s,age} = Fleet_{t-1,v,s,age-1} - Sell_{t,v,s,age} $$
    $$ \sum_{d, f} Use_{t,v,s,d,f} \le \sum_{age} Fleet_{t,v,s,age} $$
    
    *Note*: We assume we can use vehicles bought in the same year.
    We also need to ensure we don't sell more than we have.
    $$ Sell_{t,v,s,age} \le Fleet_{t-1,v,s,age-1} $$

3.  **Emission Targets**:
    $$ \sum_{s,d,v,f} (KmCovered_{t,v,s,d,f} \times Consumption_{v,f} \times FuelEmission_{f}) \le EmissionTarget_{t} $$

4.  **Fuel Compatibility**:
    $KmCovered_{t,v,s,d,f} = 0$ if vehicle $v$ not compatible with fuel $f$.

### Objective Function
Minimize Total Cost:
$$ \sum_{t} (Cost_{Purchase} + Cost_{Fuel} + Cost_{Maint} + Cost_{Ins} - Cost_{Resale}) $$

Where:
- $Cost_{Purchase} = \sum_{v,s} Buy_{t,v,s} \times VehicleCost_{v,s,t}$
- $Cost_{Fuel} = \sum_{v,s,d,f} KmCovered_{t,v,s,d,f} \times Consumption_{v,f} \times FuelCost_{f,t}$
- $Cost_{Maint} = \sum_{v,s,age} Fleet_{t,v,s,age} \times PurchasePrice_{v,s,year\_bought} \times MaintRate_{age}$
- $Cost_{Ins} = \sum_{v,s,age} Fleet_{t,v,s,age} \times PurchasePrice_{v,s,year\_bought} \times InsRate_{age}$
- $Cost_{Resale} = \sum_{v,s,age} Sell_{t,v,s,age} \times PurchasePrice_{v,s,year\_bought} \times ResaleRate_{age}$

*Note*: Tracking `PurchasePrice` based on `year_bought` implies we need to track cohorts of vehicles.
$Fleet_{t,v,s,age}$ implicitly tracks the cohort bought in year $t-age$.
So $PurchasePrice$ is $VehicleCost_{v,s,t-age}$.

## Implementation Strategy
1.  Use `pulp` for MILP.
2.  Pre-process data into dictionaries.
3.  Define variables.
4.  Add constraints.
5.  Set objective.
6.  Solve.
7.  Extract solution to CSV.

