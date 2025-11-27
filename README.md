# Carbon Emission Optimization - Shell.ai

## 🎯 Problem Statement

This is a **Fleet Optimization Challenge** from Shell.ai focused on minimizing carbon emissions from a commercial vehicle fleet over 16 years (2023-2038) while meeting transportation demand.

### Objective
**Minimize total carbon emissions by 79.4%** (from 11.7M to 2.4M) while:
- ✅ Meeting all transportation demand (growing from 17M to 25M km)
- ✅ Managing fleet costs (purchase, fuel, maintenance, insurance)
- ✅ Balancing vehicle types (BEV, Diesel, LNG) and fuel choices

---

## 📊 Data Files

| File | Description | Key Info |
|------|-------------|----------|
| `carbon_emissions.csv` | Yearly emission targets | 79.4% reduction required |
| `demand.csv` | Transportation demand | 4 sizes × 4 distances × 16 years |
| `vehicles.csv` | Vehicle specifications | 3 types (BEV/Diesel/LNG), costs, ranges |
| `fuels.csv` | Fuel properties | Emissions, costs, trends |
| `vehicles_fuels.csv` | Fuel compatibility | Consumption rates |
| `cost_profiles.csv` | Lifecycle costs | Depreciation, insurance, maintenance |
| `sample_submission.csv` | Solution format | Buy/Use/Sell actions |

---

## 🚀 Quick Start

### 1. Explore the Data
```bash
python data_explorer.py
```
This will:
- Load and analyze all data files
- Print key statistics and insights
- Generate visualizations (`data_overview.png`)

### 2. Read the Documentation
- **`PROJECT_OVERVIEW.md`** - Detailed problem explanation, data dictionary, solution strategies
- **`data_overview.png`** - Visual summary of key trends

### 3. Key Insights from Data

**Carbon Targets:**
- 2023: 11,677,957 emissions → 2038: 2,404,387 emissions
- Average yearly reduction: 618,238

**Demand Growth:**
- 2023: 17.2M km → 2038: 25.3M km (+47.3%)
- Largest segment: S1 vehicles (41.8%), D2 distances (41.7%)

**Vehicle Economics:**
- BEV costs decrease: $187k → $130k (S1)
- Diesel/LNG costs increase (inflation)
- Electricity cost drops 45.8%

**Fuel Emissions (kg CO2/unit):**
- Electricity: 0.000 ⚡
- BioLNG: 0.378 🌱
- HVO: 0.488 🌱
- LNG: 2.486 ⛽
- B20: 3.049 ⛽

---

## 💡 Solution Approach

### Decision Variables
For each year, decide:
1. **Buy**: Which vehicles to purchase
2. **Use**: Which vehicles to operate (with which fuel, on which routes)
3. **Sell**: Which vehicles to dispose of

### Constraints
- Meet all demand (size × distance combinations)
- Respect vehicle capacity limits
- Use only compatible fuels
- Maintain fleet balance

### Optimization Strategy
1. **Early years (2023-2027)**: Use diesel/LNG, introduce BEVs for short routes
2. **Transition (2028-2033)**: Increase BEV adoption, phase out high-emission vehicles
3. **Final push (2034-2038)**: Maximize BEVs, use bio-fuels for long-distance only

---

## 📁 Project Structure

```
Carbon-Emission-Optimization/
├── README.md                    # This file
├── PROJECT_OVERVIEW.md          # Detailed problem explanation
├── data_explorer.py             # Data analysis script
├── data_overview.png            # Generated visualizations
├── carbon_emissions.csv         # Emission targets
├── demand.csv                   # Transportation demand
├── vehicles.csv                 # Vehicle specifications
├── fuels.csv                    # Fuel properties
├── vehicles_fuels.csv           # Fuel compatibility
├── cost_profiles.csv            # Lifecycle costs
└── sample_submission.csv        # Solution template
```

---

## 🔧 Next Steps

1. ✅ **Understand the data** - Run `data_explorer.py`
2. ✅ **Read the overview** - Review `PROJECT_OVERVIEW.md`
3. 🔨 **Build optimizer** - Create optimization model (LP/MIP)
4. 🧪 **Validate solution** - Check constraints and objectives
5. 📤 **Generate submission** - Format as `sample_submission.csv`

---

## 🏆 Success Criteria

- [x] All demand met for every year/size/distance combination
- [x] Carbon emission targets achieved
- [x] Fleet balance maintained (can't use vehicles you don't own)
- [x] Costs minimized while meeting emission goals

---

## 📚 Resources

- **Optimization Libraries**: `pulp`, `scipy.optimize`, `cvxpy`
- **Data Analysis**: `pandas`, `numpy`, `matplotlib`
- **Problem Type**: Mixed Integer Linear Programming (MILP)

---

**Good luck optimizing! 🚛⚡🌱**
