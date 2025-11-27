"""
Shell.ai Carbon Emission Optimization - Data Explorer
This script loads and explores all the data files to help understand the problem.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set display options
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
sns.set_style('whitegrid')

def load_all_data():
    """Load all CSV files into dataframes"""
    print("Loading data files...")
    
    data = {
        'carbon_emissions': pd.read_csv('carbon_emissions.csv'),
        'demand': pd.read_csv('demand.csv'),
        'vehicles': pd.read_csv('vehicles.csv'),
        'fuels': pd.read_csv('fuels.csv'),
        'vehicles_fuels': pd.read_csv('vehicles_fuels.csv'),
        'cost_profiles': pd.read_csv('cost_profiles.csv'),
        'sample_submission': pd.read_csv('sample_submission.csv')
    }
    
    print("✓ All data loaded successfully!\n")
    return data

def explore_carbon_targets(df):
    """Analyze carbon emission targets"""
    print("=" * 60)
    print("CARBON EMISSION TARGETS")
    print("=" * 60)
    print(f"\nTotal years: {len(df)}")
    print(f"Starting emissions (2023): {df.iloc[0]['carbon_emission']:,.0f}")
    print(f"Target emissions (2038): {df.iloc[-1]['carbon_emission']:,.0f}")
    reduction = (1 - df.iloc[-1]['carbon_emission'] / df.iloc[0]['carbon_emission']) * 100
    print(f"Required reduction: {reduction:.1f}%")
    print(f"\nAverage yearly reduction: {df['carbon_emission'].diff().mean():,.0f}")
    print("\n")

def explore_demand(df):
    """Analyze transportation demand"""
    print("=" * 60)
    print("TRANSPORTATION DEMAND")
    print("=" * 60)
    
    # Total demand by year
    yearly_demand = df.groupby('year')['demand'].sum()
    print(f"\nTotal demand 2023: {yearly_demand.iloc[0]:,.0f} km")
    print(f"Total demand 2038: {yearly_demand.iloc[-1]:,.0f} km")
    growth = (yearly_demand.iloc[-1] / yearly_demand.iloc[0] - 1) * 100
    print(f"Demand growth: {growth:.1f}%")
    
    # Demand by size
    print("\nDemand by vehicle size (2023):")
    size_demand = df[df['year'] == 2023].groupby('size')['demand'].sum()
    for size, demand in size_demand.items():
        print(f"  {size}: {demand:>12,} km ({demand/size_demand.sum()*100:>5.1f}%)")
    
    # Demand by distance
    print("\nDemand by distance category (2023):")
    dist_demand = df[df['year'] == 2023].groupby('distance')['demand'].sum()
    for dist, demand in dist_demand.items():
        print(f"  {dist}: {demand:>12,} km ({demand/dist_demand.sum()*100:>5.1f}%)")
    print("\n")

def explore_vehicles(df):
    """Analyze vehicle options"""
    print("=" * 60)
    print("VEHICLE OPTIONS")
    print("=" * 60)
    
    # Count by type
    print("\nVehicle types available:")
    type_counts = df.groupby('vehicle').size()
    for vtype, count in type_counts.items():
        print(f"  {vtype}: {count} variants")
    
    # Cost analysis for 2023
    print("\nVehicle costs in 2023:")
    df_2023 = df[df['year'] == 2023]
    for size in ['S1', 'S2', 'S3', 'S4']:
        size_vehicles = df_2023[df_2023['size'] == size]
        print(f"\n  Size {size}:")
        for _, row in size_vehicles.iterrows():
            print(f"    {row['vehicle']:>6}: ${row['cost']:>8,.0f} (range: {row['yearly_range']:,} km/year)")
    
    # BEV cost trends
    print("\nBEV cost reduction over time (Size S1):")
    bev_s1 = df[(df['vehicle'] == 'BEV') & (df['size'] == 'S1')]
    print(f"  2023: ${bev_s1[bev_s1['year'] == 2023]['cost'].values[0]:,.0f}")
    print(f"  2030: ${bev_s1[bev_s1['year'] == 2030]['cost'].values[0]:,.0f}")
    print(f"  2038: ${bev_s1[bev_s1['year'] == 2038]['cost'].values[0]:,.0f}")
    print("\n")

def explore_fuels(df):
    """Analyze fuel options"""
    print("=" * 60)
    print("FUEL OPTIONS")
    print("=" * 60)
    
    # 2023 fuel comparison
    df_2023 = df[df['year'] == 2023]
    print("\nFuel comparison (2023):")
    print(f"{'Fuel':<12} {'Emissions':<12} {'Cost':<12}")
    print("-" * 40)
    for _, row in df_2023.iterrows():
        print(f"{row['fuel']:<12} {row['emissions']:<12.3f} ${row['cost']:<12.3f}")
    
    # Cost trends
    print("\nElectricity cost trend:")
    elec = df[df['fuel'] == 'Electricity']
    print(f"  2023: ${elec[elec['year'] == 2023]['cost'].values[0]:.3f}/kWh")
    print(f"  2038: ${elec[elec['year'] == 2038]['cost'].values[0]:.3f}/kWh")
    reduction = (1 - elec[elec['year'] == 2038]['cost'].values[0] / 
                 elec[elec['year'] == 2023]['cost'].values[0]) * 100
    print(f"  Reduction: {reduction:.1f}%")
    print("\n")

def explore_vehicle_fuels(df):
    """Analyze vehicle-fuel compatibility"""
    print("=" * 60)
    print("VEHICLE-FUEL COMPATIBILITY")
    print("=" * 60)
    
    # Extract vehicle type from id
    df['vehicle_type'] = df['id'].str.split('_').str[0]
    
    print("\nFuel options by vehicle type:")
    for vtype in ['BEV', 'Diesel', 'LNG']:
        fuels = df[df['vehicle_type'] == vtype]['fuel'].unique()
        print(f"  {vtype}: {', '.join(fuels)}")
    
    print("\nAverage consumption rates (2023):")
    df_2023 = df[df['id'].str.contains('2023')]
    for vtype in ['BEV', 'Diesel', 'LNG']:
        vtype_data = df_2023[df_2023['vehicle_type'] == vtype]
        avg_consumption = vtype_data['consumption'].mean()
        print(f"  {vtype}: {avg_consumption:.3f} units/km")
    print("\n")

def explore_cost_profiles(df):
    """Analyze vehicle lifecycle costs"""
    print("=" * 60)
    print("VEHICLE LIFECYCLE COSTS")
    print("=" * 60)
    
    print("\nDepreciation schedule:")
    print(f"{'Year':<6} {'Resale %':<10} {'Insurance %':<12} {'Maintenance %':<15}")
    print("-" * 50)
    for _, row in df.iterrows():
        print(f"{row['end_of_year']:<6} {row['resale_value_percent']:<10} "
              f"{row['insurance_cost_percent']:<12} {row['maintenance_cost_percent']:<15}")
    
    print("\nKey insights:")
    print(f"  - Year 1 resale value: {df.iloc[0]['resale_value_percent']}%")
    print(f"  - Year 10 resale value: {df.iloc[-1]['resale_value_percent']}%")
    print(f"  - Total depreciation: {df.iloc[0]['resale_value_percent'] - df.iloc[-1]['resale_value_percent']}%")
    print("\n")

def create_visualizations(data):
    """Create helpful visualizations"""
    print("=" * 60)
    print("CREATING VISUALIZATIONS")
    print("=" * 60)
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('Shell.ai Carbon Emission Optimization - Data Overview', fontsize=16)
    
    # 1. Carbon emission targets
    ax = axes[0, 0]
    data['carbon_emissions'].plot(x='year', y='carbon_emission', ax=ax, marker='o')
    ax.set_title('Carbon Emission Targets')
    ax.set_ylabel('Emissions')
    ax.grid(True)
    
    # 2. Total demand by year
    ax = axes[0, 1]
    yearly_demand = data['demand'].groupby('year')['demand'].sum()
    yearly_demand.plot(ax=ax, marker='o', color='green')
    ax.set_title('Total Transportation Demand')
    ax.set_ylabel('Total km')
    ax.grid(True)
    
    # 3. Fuel emissions comparison
    ax = axes[0, 2]
    fuel_2023 = data['fuels'][data['fuels']['year'] == 2023]
    fuel_2023.plot(x='fuel', y='emissions', kind='bar', ax=ax, legend=False)
    ax.set_title('Fuel Emissions (2023)')
    ax.set_ylabel('kg CO2 per unit')
    ax.set_xlabel('Fuel Type')
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    # 4. BEV cost trends
    ax = axes[1, 0]
    for size in ['S1', 'S2', 'S3', 'S4']:
        bev_data = data['vehicles'][(data['vehicles']['vehicle'] == 'BEV') & 
                                     (data['vehicles']['size'] == size)]
        ax.plot(bev_data['year'], bev_data['cost'], marker='o', label=f'Size {size}')
    ax.set_title('BEV Cost Trends')
    ax.set_ylabel('Cost ($)')
    ax.set_xlabel('Year')
    ax.legend()
    ax.grid(True)
    
    # 5. Demand by size (2023)
    ax = axes[1, 1]
    demand_2023 = data['demand'][data['demand']['year'] == 2023]
    size_demand = demand_2023.groupby('size')['demand'].sum()
    size_demand.plot(kind='bar', ax=ax, color='orange')
    ax.set_title('Demand by Vehicle Size (2023)')
    ax.set_ylabel('Total km')
    ax.set_xlabel('Vehicle Size')
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=0)
    
    # 6. Electricity cost trend
    ax = axes[1, 2]
    elec_data = data['fuels'][data['fuels']['fuel'] == 'Electricity']
    ax.plot(elec_data['year'], elec_data['cost'], marker='o', color='blue')
    ax.set_title('Electricity Cost Trend')
    ax.set_ylabel('Cost ($/kWh)')
    ax.set_xlabel('Year')
    ax.grid(True)
    
    plt.tight_layout()
    plt.savefig('data_overview.png', dpi=300, bbox_inches='tight')
    print("✓ Saved visualization to 'data_overview.png'\n")
    plt.show()

def main():
    """Main execution function"""
    print("\n" + "=" * 60)
    print("SHELL.AI CARBON EMISSION OPTIMIZATION - DATA EXPLORER")
    print("=" * 60 + "\n")
    
    # Load data
    data = load_all_data()
    
    # Explore each dataset
    explore_carbon_targets(data['carbon_emissions'])
    explore_demand(data['demand'])
    explore_vehicles(data['vehicles'])
    explore_fuels(data['fuels'])
    explore_vehicle_fuels(data['vehicles_fuels'])
    explore_cost_profiles(data['cost_profiles'])
    
    # Create visualizations
    create_visualizations(data)
    
    print("=" * 60)
    print("EXPLORATION COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review the visualizations in 'data_overview.png'")
    print("2. Read 'PROJECT_OVERVIEW.md' for detailed problem explanation")
    print("3. Start building your optimization model")
    print("\n")

if __name__ == "__main__":
    main()
