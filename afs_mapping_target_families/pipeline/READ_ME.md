# Pipeline: Create Combined Dataset

The script create_combined_dataset.py is used to aggregate multiple raw data sources to create a single file that serves as the backend of the streamlit dashboard. The three datasets are:

1. [Quarterly outcomes at age 2](https://www.gov.uk/government/statistics/child-development-outcomes-at-2-to-2-and-a-half-years-quarterly-data-for-2021-to-2022): This is the main dataset used for the analysis
2. [Annual EYFSP scores from 2021/2022 - Headline measures by characteristics](https://explore-education-statistics.service.gov.uk/data-catalogue/early-years-foundation-stage-profile-results/2021-22): This is used to generate statistics on the % of children reaching a GLD from each county/unitary authority
3. [Census 2021 age by single year](https://www.ons.gov.uk/datasets/TS007/editions/2021/versions/1): This is used to estimate the response rate for each county/unitary authority

The pipeline performs several steps of data manipulation.

## Aggregating Quarterly Data

The raw ASQ data is broken down quarterly covering the date ranges: April - June 2021; July - September 2021; October - December 2021; January - March 2022. As part of the aggregation, we have added a field called 'date' to the dataset, which indicates which of the date ranges the data point covers.

We also add an additional row for each county and unitary authority with the date value 'Annual'. For each local authority, we calculate the total number of students who answered the question for that category and the total number of students who were above average for the category, and use those totals to calculate the annual percent of students who were above average for that category. If an LA submitted "Don't know" (represented by 'dk' or 'DK' in the raw data) for one of the categories then we put "Could not compute" as the value for the annual aggregation.

## Estimating Response Rates

Response rates are estimated using population estimates from the Census 2021 data. The response rate is calculated as:
${total number of students who answered all 5 categories over the year} \over {Total number of 1 year olds when the census was conducted in March 2021}}}$.

## Including Percent of Students Reaching Good Level of Development at Age 5

GLD percentage is estimated using the EYFSP Headline Measures data. The EYFSP data is filtered for "geographic_area" = "Local authority" and the fields "characteristic", "characteristic_type", and "gender" are all = "Total". This gives us the aggregate gld_percentage for the county/unitary authority, which is then used to connect to the ASQ data. This aggregation can be found in getters/raw/eyfsp.py.
