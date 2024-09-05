-- Intermediate query views for the "STAPH AUREUS COAG +" organism query, organism id: 80023
-- This queries result in a materialized view that contains the data of the patients with the organism id
-- The view contains additional data that should be removed before its use (e.g. ids and used drugs)

-- Drops any existing intermediate and materialized views to ensure a clean slate for the query.
drop materialized view if exists inter_query_7;
drop view if exists last_drug_date_view;
drop view if exists inter_query_6;
drop view if exists last_drug_date_view;
drop view if exists inter_query_5;
drop view if exists curr_unit_view;
drop materialized view if exists inter_query_4;
drop view if exists presc_view;
drop view if exists inter_query_3;
drop view if exists inter_query_2;
drop view if exists inter_query_1;

-- Create a view to extract data from microbiologyevents, filtering by organism id (80023)
-- Filters out null and pending cultures ('P')
create view inter_query_1 as 
	select row_id as event_id, subject_id, hadm_id, coalesce(charttime, chartdate) as date, ab_name, spec_type_desc, interpretation 
	from microbiologyevents m
	where interpretation is not null and interpretation <> 'P' and org_itemid = 80023;

-- Add patient demographic data, such as gender and age, by joining with the patients table
create view inter_query_2 as
	select iq.*, p.gender, extract(year from age(iq.date, p.dob)) as age
	from (select * from inter_query_1) as iq
	join (select * from patients) as p on iq.subject_id = p.subject_id;

-- Incorporate admission details from the admissions table
-- Includes admission type, location, time since admission, and discharge/death information
create view inter_query_3 as 
	select iq.*, a.admission_type, a.admission_location, extract(day from iq.date - a.ADMITTIME) as admission_days,
		(a.deathtime is not null) as exitus, a.discharge_location
	from
		(select * from inter_query_2) as iq
	join
		(select * from admissions) as a on iq.hadm_id = a.hadm_id;

-- Create a view to gather prescription data for patients, including only drugs prescribed in the last 180 days
-- Filters out drugs with NDC code '0'
create view presc_view as 
	select iq.event_id, string_agg(pr.ndc, ', ') as drugs
	from
		(select * from inter_query_3) as iq 
	join
		(select subject_id, hadm_id, ndc, enddate, startdate from prescriptions) as pr
		on iq.subject_id = pr.subject_id AND iq.hadm_id = pr.hadm_id
	where iq.date > enddate AND iq.date - INTERVAL '180 days' < pr.startdate and ndc <> '0'
	group by iq.event_id;

-- Intermediate materialized view that adds prescription data to the previous results (denormalized)
create materialized view inter_query_4 as 
	select iq.*, pr.drugs 
	from
		(select * from inter_query_3) as iq
	left outer join
		(select * from presc_view) as pr on iq.event_id = pr.event_id;

-- View to determine the current care unit of a patient when the culture was taken
-- Joins transfer data to associate patients with their ICU status based on culture event time
create view curr_unit_view as
select iq.event_id, curr_careunit as icu_when_culture 
from 
    (select * from inter_query_4) iq
left outer join
    (select subject_id, hadm_id, CURR_CAREUNIT, INTIME, OUTTIME from transfers) t
on iq.subject_id = t.subject_id and iq.hadm_id = t.hadm_id
where iq.date > t.intime and iq.date < t.outtime;

-- View to add ICU status to the dataset from the culture data
create view inter_query_5 as
select iq.*, v.icu_when_culture 
from 
    (select * from inter_query_4) iq
left outer join
    (select * from curr_unit_view) v
on iq.event_id = v.event_id;

-- Exclude patients who were in more than one ICU during the culture collection period
create view inter_query_6 as
SELECT *
FROM inter_query_5 iq 
WHERE event_id NOT IN (
    SELECT event_id
    FROM inter_query_5 iq2
    GROUP BY event_id
    HAVING COUNT(*) > 1
);

-- View to obtain the most recent treatment data within the last 180 days for each patient
-- Includes the last treatment date, the number of treatments, and the total days with treatment
create view last_drug_date_view as 
select iq.event_id, 
    max(pr.enddate) as last_treatment_date, 
    count(pr.enddate) as number_of_treatments_last_180_days,
    sum(days_with_treatment_last_180_days) as days_with_treatment_last_180_days
from
    (select * from inter_query_6) iq
left outer join
    (select subject_id, hadm_id, enddate, drug, extract(day from enddate - startdate) as days_with_treatment_last_180_days 
     from prescriptions) pr
on iq.subject_id = pr.subject_id and iq.hadm_id = pr.hadm_id 
   and to_tsvector('english', upper(pr.drug)) @@ to_tsquery('english', replace(split_part(iq.ab_name, '/', 1), ' ', ' & '))
where pr.enddate < iq.date and pr.enddate > iq.date - interval '180' day
group by iq.event_id;

-- Final materialized view that calculates the time since the last treatment
-- It also aggregates the number of treatments and treatment duration within the last 180 days
create materialized view inter_query_7 as
select iq.*, 
    coalesce(extract(day from iq.date - v.last_treatment_date), 360) as days_since_last_treatment,
    coalesce(v.number_of_treatments_last_180_days, 0) as number_of_treatments_last_180_days,
    coalesce(v.days_with_treatment_last_180_days, 0) as days_with_treatment_last_180_days
from
    (select * from inter_query_6 iq) iq
left outer join
    (select * from last_drug_date_view) v
on iq.event_id = v.event_id;