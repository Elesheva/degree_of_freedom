import numpy as np
import pandas as pd

df = pd.read_excel('C:/Users/vikto/Downloads/British Airways Summer Schedule Dataset - Forage Data Science Task 1.xlsx')
df = df.drop(['FLIGHT_DATE', 'FLIGHT_TIME', 'AIRLINE_CD', 'FLIGHT_NO', 'DEPARTURE_STATION_CD', 'ARRIVAL_STATION_CD', 'ARRIVAL_COUNTRY', 'AIRCRAFT_TYPE'], axis=1)
group_df = df.groupby(by=["TIME_OF_DAY", "HAUL", "ARRIVAL_REGION"]).sum().reset_index()
group_df ['TIER_1'] = round(((group_df['TIER1_ELIGIBLE_PAX'])*100)/(group_df[['FIRST_CLASS_SEATS', 'BUSINESS_CLASS_SEATS', 'ECONOMY_SEATS']].sum(axis=1)),2)
group_df ['TIER_2'] = round(((group_df['TIER2_ELIGIBLE_PAX'])*100)/(group_df[['FIRST_CLASS_SEATS', 'BUSINESS_CLASS_SEATS', 'ECONOMY_SEATS']].sum(axis=1)),2)
group_df ['TIER_3'] = round(((group_df['TIER3_ELIGIBLE_PAX'])*100)/(group_df[['FIRST_CLASS_SEATS', 'BUSINESS_CLASS_SEATS', 'ECONOMY_SEATS']].sum(axis=1)),2)
new_df = group_df.drop(['TIER1_ELIGIBLE_PAX', 'TIER2_ELIGIBLE_PAX', 'TIER3_ELIGIBLE_PAX', 'FIRST_CLASS_SEATS', 'BUSINESS_CLASS_SEATS', 'ECONOMY_SEATS'], axis=1)

Q1_FIRST_CLASS_SEATS = group_df['FIRST_CLASS_SEATS'].quantile(0.25)
Q3_FIRST_CLASS_SEATS = group_df['FIRST_CLASS_SEATS'].quantile(0.75)
mean_FIRST_CLASS_SEATS = np.mean(group_df['FIRST_CLASS_SEATS'])
median_FIRST_CLASS_SEATS = np.median(group_df['FIRST_CLASS_SEATS'])

Q1_BUSINESS_CLASS_SEATS = group_df['BUSINESS_CLASS_SEATS'].quantile(0.25)
Q3_BUSINESS_CLASS_SEATS = group_df['BUSINESS_CLASS_SEATS'].quantile(0.75)
mean_BUSINESS_CLASS_SEATS = np.mean(group_df['BUSINESS_CLASS_SEATS'])
median_BUSINESS_CLASS_SEATS = np.median(group_df['BUSINESS_CLASS_SEATS'])

Q1_ECONOMY_SEATS = group_df['ECONOMY_SEATS'].quantile(0.25)
Q3_ECONOMY_SEATS = group_df['ECONOMY_SEATS'].quantile(0.75)
mean_ECONOMY_SEATS = np.mean(group_df['ECONOMY_SEATS'])
median_ECONOMY_SEATS = np.median(group_df['ECONOMY_SEATS'])

def assign_notes(row):
    if 0 == row['FIRST_CLASS_SEATS']:
        if Q3_BUSINESS_CLASS_SEATS < row['BUSINESS_CLASS_SEATS'] > mean_BUSINESS_CLASS_SEATS : 
            return "Короткие рейсы, мало пассажиров First Class. В TIER_1 пассажиры преимущественно BA Gold Guest List и держатели BA Premier Card. Пассажиров Business class выше среднего. "
        elif Q3_BUSINESS_CLASS_SEATS > row['BUSINESS_CLASS_SEATS']:
            return "Короткие рейсы, мало пассажиров First Class. В TIER_1 пассажиры преимущественно BA Gold Guest List и держатели BA Premier Card. Пассажиров Business class много. "
        elif row['BUSINESS_CLASS_SEATS'] < mean_BUSINESS_CLASS_SEATS : 
            return "Короткие рейсы, мало пассажиров First Class. В TIER_1 пассажиры преимущественно BA Gold Guest List и держатели BA Premier Card. Пассажиров Business class ниже среднего."
        elif row['BUSINESS_CLASS_SEATS'] < Q1_BUSINESS_CLASS_SEATS: 
            return "Короткие рейсы, мало пассажиров First Class. В TIER_1 пассажиры преимущественно BA Gold Guest List и держатели BA Premier Card. Пассажиров Business class мало."
        
    elif 0 < row['FIRST_CLASS_SEATS'] < mean_FIRST_CLASS_SEATS and row['HAUL'] == "SHORT":
        return "Короткие рейсы, мало пассажиров First Class"
    elif row['FIRST_CLASS_SEATS'] > mean_FIRST_CLASS_SEATS:
        return "Длинные рейсы, пассажиров First Class выше среднего"
    else:
        return "Длинные рейсы, пассажиров First Class равно среднему"
      


group_df['Notes'] = group_df.apply(assign_notes, axis=1)