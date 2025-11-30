# Shell.ai Carbon Emission Optimization - Project Overview

## Problem Statement

This is a **Fleet Optimization Problem** for Shell.ai focused on minimizing carbon emissions from a commercial vehicle fleet over a 16-year period (2023-2038) while meeting transportation demand and managing costs.

### Objective
**Minimize total carbon emissions** while:
- Meeting all transportation demand across different vehicle sizes and distances
- Managing fleet acquisition, operation, and disposal costs
- Balancing trade-offs between vehicle types, fuel choices, and operational efficiency

---

## Data Files Explained

### 1. **carbon_emissions.csv**
**Purpose:** Target carbon emission reduction goals by year

| Column | Description |
|--------|-------------|
| year | Year (2023-2038) |
| carbon_emission | Target maximum emissions for that year |

**Key Insight:** Emissions targets decrease from ~11.7M (2023) to ~2.4M (2038), representing a ~79% reduction requirement.

---

### 2. **demand.csv**
**Purpose:** Transportation demand that MUST be met

| Column | Description |
|--------|-------------|
| year | Year (2023-2038) |
| size | Vehicle size (S1, S2, S3, S4) |
| distance | Distance category (D1, D2, D3, D4) |
| demand | Number of km that must be covered |

**Key Insights:**
- 4 vehicle sizes: S1 (small), S2 (medium), S3 (medium-large), S4 (large)
- 4 distance categories: D1 (short), D2 (medium), D3 (long), D4 (very long)
- Total demand increases over time (from ~18M km in 2023 to ~24M km in 2038)
- 16 combinations per year (4 sizes × 4 distances)

---

### 3. **vehicles.csv**
**Purpose:** Available vehicle types with specifications

| Column | Description |
|--------|-------------|
| id | Unique vehicle identifier (e.g., BEV_S1_2023) |
| vehicle | Vehicle type (BEV, Diesel, LNG) |
| size | Vehicle size (S1, S2, S3, S4) |
| year | Year vehicle becomes available |
| cost | Purchase cost in currency units |
| yearly_range | Maximum km per year the vehicle can travel |
| distance | Optimal distance category for this vehicle |

**Vehicle Types:**
- **BEV** (Battery Electric Vehicle): Zero emissions, high upfront cost, decreasing over time
- **Diesel**: Traditional, uses B20 or HVO fuels, moderate emissions
- **LNG** (Liquefied Natural Gas): Can use LNG or BioLNG, lower emissions than diesel

**Key Insights:**
- BEV costs decrease significantly (e.g., S1: $187k → $130k)
- Diesel/LNG costs increase over time (inflation)
- Each vehicle has a yearly range limit (73k-118k km/year)

---

### 4. **fuels.csv**
**Purpose:** Fuel characteristics by year

| Column | Description |
|--------|-------------|
| fuel | Fuel type (B20, BioLNG, Electricity, HVO, LNG) |
| year | Year (2023-2038) |
| emissions | kg CO2 per liter/kWh |
| cost | Cost per liter/kWh |
| cost_uncertainty | Uncertainty percentage |

**Fuel Types:**
- **Electricity**: 0 emissions, decreasing cost
- **BioLNG**: Very low emissions (0.378), decreasing cost
- **HVO** (Hydrotreated Vegetable Oil): Low emissions (0.488)
- **LNG**: Moderate emissions (2.486)
- **B20** (20% biodiesel blend): High emissions (3.049), increasing cost

**Key Insight:** Electricity and bio-fuels become increasingly cost-competitive over time.

---

### 5. **vehicles_fuels.csv**
**Purpose:** Fuel consumption rates for each vehicle-fuel combination

| Column | Description |
|--------|-------------|
| id | Vehicle identifier |
| fuel | Compatible fuel type |
| consumption | Liters or kWh per km |

**Key Insights:**
- Diesel vehicles can use B20 or HVO (same consumption rate)
- LNG vehicles can use LNG or BioLNG (slightly different consumption)
- BEV vehicles only use Electricity
- Consumption improves slightly in later years for some vehicles

---

### 6. **cost_profiles.csv**
**Purpose:** Vehicle depreciation and operating costs

| Column | Description |
|--------|-------------|
| end_of_year | Years since purchase (1-10) |
| resale_value_percent | % of original cost when sold |
| insurance_cost_percent | Annual insurance as % of original cost |
| maintenance_cost_percent | Annual maintenance as % of original cost |

**Key Insights:**
- Vehicles depreciate rapidly (90% → 30% over 10 years)
- Insurance and maintenance costs increase with age
- After year 8, resale value plateaus at 30%

---

### 7. **sample_submission.csv**
**Purpose:** Template showing the required solution format

| Column | Description |
|--------|-------------|
| year | Year of operation |
| id | Vehicle identifier |
| num_vehicles | Number of vehicles |
| type | Action: Buy, Use, or Sell |
| fuel | Fuel used (for "Use" actions) |
| distance_bucket | Distance category (for "Use" actions) |
| distance_per_vehicle | km traveled per vehicle |

**Actions:**
- **Buy**: Acquire new vehicles (fuel, distance_bucket, distance_per_vehicle = 0 or empty)
- **Use**: Operate vehicles with specific fuel on specific routes
- **Sell**: Dispose of vehicles (fuel, distance_bucket, distance_per_vehicle = 0 or empty)

---

## How to Approach This Problem

### 1. **Decision Variables**
For each year, vehicle type, and fuel combination, decide:
- How many vehicles to **buy**
- How many vehicles to **use** (and on which routes with which fuel)
- How many vehicles to **sell**

### 2. **Constraints**
- **Demand satisfaction**: Total km covered must meet or exceed demand for each size-distance combination
- **Fleet balance**: Can't use more vehicles than you own
- **Vehicle capacity**: Each vehicle has a yearly range limit
- **Fuel compatibility**: Vehicles can only use compatible fuels
- **Carbon targets**: Total emissions should meet yearly targets

### 3. **Optimization Objectives**
**Primary:** Minimize total carbon emissions
**Secondary:** Minimize total cost (vehicle purchase, fuel, maintenance, insurance) while maximizing resale value

### 4. **Key Trade-offs**
- **BEV vs. Diesel/LNG**: BEVs have zero emissions but higher upfront costs and limited range
- **Fuel choice**: Bio-fuels cost more but emit less
- **Vehicle lifetime**: Keep vehicles longer (higher maintenance) vs. sell early (lose resale value)
- **Fleet composition**: Diverse fleet (flexible) vs. specialized fleet (efficient)

### 5. **Calculation Examples**

#### Total Emissions Calculation:
```
Emissions = Σ (num_vehicles × distance_per_vehicle × fuel_consumption × fuel_emissions)
```

#### Total Cost Calculation:
```
Total Cost = Purchase_Cost + Fuel_Cost + Maintenance_Cost + Insurance_Cost - Resale_Value

Where:
- Fuel_Cost = distance × consumption × fuel_cost
- Maintenance_Cost = vehicle_cost × maintenance_percent
- Insurance_Cost = vehicle_cost × insurance_percent
- Resale_Value = vehicle_cost × resale_percent (when sold)
```

---

## Solution Strategy Recommendations

### Phase 1: Early Years (2023-2027)
- Use existing diesel/LNG vehicles for high-demand routes
- Gradually introduce BEVs for short-distance routes (D1, D2)
- Experiment with bio-fuels (BioLNG, HVO) to reduce emissions

### Phase 2: Transition (2028-2033)
- Increase BEV adoption as costs decrease
- Phase out high-emission diesel vehicles
- Optimize fuel mix (electricity + bio-fuels)

### Phase 3: Final Push (2034-2038)
- Maximize BEV fleet for all feasible routes
- Use bio-fuels only where BEVs are impractical (long-distance, large vehicles)
- Achieve aggressive emission targets

---

## Next Steps

1. **Build a mathematical model** (Linear Programming or Mixed Integer Programming)
2. **Implement in Python** using libraries like:
   - `pulp` or `scipy.optimize` for optimization
   - `pandas` for data manipulation
   - `numpy` for calculations

3. **Validate solution**:
   - Check all demand is met
   - Verify carbon targets are achieved
   - Ensure fleet balance (can't use vehicles you don't own)

4. **Generate submission file** in the format of `sample_submission.csv`

---

## Key Success Factors

✅ **Meet all demand** - This is non-negotiable  
✅ **Minimize emissions** - Primary objective  
✅ **Balance costs** - Don't overspend on unnecessary vehicles  
✅ **Plan long-term** - Decisions in 2023 affect 2038  
✅ **Leverage technology trends** - BEV costs decrease, bio-fuels become competitive

---

## Questions to Consider

1. When should you start buying BEVs aggressively?
2. Which vehicle sizes benefit most from electrification?
3. Should you keep diesel vehicles for long-distance routes?
4. What's the optimal vehicle replacement cycle?
5. How much should you invest in bio-fuels vs. waiting for cheaper electricity?

Good luck with your optimization!
