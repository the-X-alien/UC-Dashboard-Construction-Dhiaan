uc question sprint formulas

this doc has the formula for each of the 10 sprint questions. every question has a sql version and a pandas version. both give the same answer. the data files are in the Data folder.

q1: avg number of uc campuses an applicant applied to in fall 2025
answer: 5.74

sql:
select
  sum(case when campus != 'Universitywide' then applicants end) * 1.0
  / sum(case when campus = 'Universitywide' then applicants end)
from schools
where fall_term = 2025;

pandas:
y = raw[raw['fall_term'] == 2025]
num = y[y['campus'] != 'Universitywide']['applicants'].sum()
den = y[y['campus'] == 'Universitywide']['applicants'].sum()
num / den

explanation:
one applicant can apply to many campuses. the campus rows count each person once per campus they picked, so adding those up over counts people. the universitywide row counts each person one time. we divide the big summed number by the universitywide number to get how many campuses the average person applied to. the data says 5.74.

q2: ucla fall 2025 admit rate for applicants from california public high schools
answer: 8.29

sql:
select
  sum(admits) * 100.0 / sum(applicants)
from dash
where fall_term = 2025
  and campus = 'Los Angeles'
  and school_type = 'High Schools (Public)';

pandas:
s = dash[(dash['fall_term'] == 2025) & (dash['campus'] == 'Los Angeles') & (dash['school_type'] == 'High Schools (Public)')]
s['admits'].sum() * 100 / s['applicants'].sum()

explanation:
the question asks for ucla and for ca public high school applicants only. we filter to the ucla row and the public school type, then divide admits by applicants. this is 8.29. note this is not the same as ucla overall rate because overall includes private and out of state applicants.

q3: which campus does applying to computer science cost the most admit rate versus its own overall rate in fall 2025
answer: Davis

sql:
select c.campus
from disc c
join disc o
  on c.campus = o.campus
  and o.broad_discipline = 'All disciplines'
where c.fall_term = 2025
  and c.broad_discipline = 'Computer Science'
order by (c.admit_rate - o.admit_rate) asc
limit 1;

pandas:
d25 = disc[disc['fall_term'] == 2025]
ov = d25[d25['broad_discipline'] == 'All disciplines'].set_index('campus')['admit_rate']
cs = d25[d25['broad_discipline'] == 'Computer Science'].set_index('campus')['admit_rate']
pen = (cs - ov).dropna()
pen.idxmin()

explanation:
for each campus we take the cs admit rate and subtract the campus overall rate. the most negative number means cs hurt the most. davis has the biggest drop so davis is the answer.

q4: interquartile range of admit gpa for berkeley computer science in fall 2025
answer: 0.02

sql:
select admit_gpa_p75 - admit_gpa_p25
from trmaj
where campus = 'Berkeley'
  and broad_discipline = 'Computer Science'
  and major = 'ComputerScience';

pandas:
b = trmaj[(trmaj['campus'] == 'Berkeley') & (trmaj['broad_discipline'] == 'Computer Science') & (trmaj['major'] == 'ComputerScience')]
b['admit_gpa_p75'].iloc[0] - b['admit_gpa_p25'].iloc[0]

explanation:
iqr is the 75th percentile minus the 25th percentile. the file has those two numbers for berkeley cs. we subtract them. the answer is 0.02. uc gpa is capped so the top students are all near 4.0 which makes the range small.

q5: in fall 2025 at how many of the 9 campuses was the white freshman admit rate higher than the hispanic/latino(a) rate
answer: 9

sql:
select count(*) from (
  select campus,
    sum(case when ethnicity = 'White' and count_type = 'Adm' then n end) * 1.0
      / sum(case when ethnicity = 'White' and count_type = 'App' then n end) as wr,
    sum(case when ethnicity = 'Hispanic/Latino(a)' and count_type = 'Adm' then n end) * 1.0
      / sum(case when ethnicity = 'Hispanic/Latino(a)' and count_type = 'App' then n end) as hr
  from eth
  where fall_term = 2025 and campus != 'Systemwide'
  group by campus
  having wr > hr
);

pandas:
e25 = eth[(eth['fall_term'] == 2025) & (eth['campus'] != 'Systemwide')]
ap = e25[e25['count_type'] == 'App'].pivot_table(index='campus', columns='ethnicity', values='n', aggfunc='sum')
ad = e25[e25['count_type'] == 'Adm'].pivot_table(index='campus', columns='ethnicity', values='n', aggfunc='sum')
white_rate = ad['White'] / ap['White']
hispanic_rate = ad['Hispanic/Latino(a)'] / ap['Hispanic/Latino(a)']
(white_rate > hispanic_rate).sum()

explanation:
for each campus we compute white admit rate and hispanic admit rate using the ethnicity file. then we count how many campuses have white higher. all 9 campuses have white higher.

q6: systemwide in fall 2025 which group had the higher freshman admit rate white or hispanic/latino(a)
answer: Hispanic/Latino(a)

sql:
select case
  when (sum(case when ethnicity = 'Hispanic/Latino(a)' and count_type = 'Adm' then n end) * 1.0
        / sum(case when ethnicity = 'Hispanic/Latino(a)' and count_type = 'App' then n end))
     > (sum(case when ethnicity = 'White' and count_type = 'Adm' then n end) * 1.0
        / sum(case when ethnicity = 'White' and count_type = 'App' then n end))
  then 'Hispanic/Latino(a)' else 'White' end
from eth
where fall_term = 2025 and campus = 'Systemwide';

pandas:
sysw = eth[(eth['fall_term'] == 2025) & (eth['campus'] == 'Systemwide')]
wr = sysw[(sysw['ethnicity'] == 'White') & (sysw['count_type'] == 'Adm')]['n'].iloc[0] / sysw[(sysw['ethnicity'] == 'White') & (sysw['count_type'] == 'App')]['n'].iloc[0]
hr = sysw[(sysw['ethnicity'] == 'Hispanic/Latino(a)') & (sysw['count_type'] == 'Adm')]['n'].iloc[0] / sysw[(sysw['ethnicity'] == 'Hispanic/Latino(a)') & (sysw['count_type'] == 'App')]['n'].iloc[0]
if hr > wr:
    'Hispanic/Latino(a)'
else:
    'White'

explanation:
at the systemwide level we compare the two groups only. hispanic rate is higher than white rate so the answer is hispanic/latino(a). this is the opposite of q5 because systemwide mixes all campuses together.

q7: of bay area high school graduates in class of 2023 what share enrolled at a california community college within 12 months
answer: 34.04

sql:
select sum(enrolled_ccc) * 100.0 / sum(graduates)
from schools
where fall_term = 2023
  and campus = 'Universitywide'
  and county in ('Alameda','Contra Costa','Marin','Napa','San Francisco','San Mateo','Santa Clara','Solano','Sonoma');

pandas:
bay = ['Alameda','Contra Costa','Marin','Napa','San Francisco','San Mateo','Santa Clara','Solano','Sonoma']
sub = raw[(raw['fall_term'] == 2023) & (raw['campus'] == 'Universitywide') & (raw['county'].isin(bay))]
sub['enrolled_ccc'].sum() * 100 / sub['graduates'].sum()

explanation:
bay area means those nine counties. we use the universitywide rows for 2023 and add up community college enrollees, then divide by total graduates. the share is 34.04 percent.

q8: at mission san jose high school in fall 2023 what share of the school a-g completers applied to at least one uc
answer: 99.06

sql:
select sum(applicants) * 100.0 / sum(ag_completers)
from schools
where high_school = 'MISSION SAN JOSE HIGH SCHOOL'
  and fall_term = 2023
  and campus = 'Universitywide';

pandas:
m = raw[(raw['high_school'] == 'MISSION SAN JOSE HIGH SCHOOL') & (raw['fall_term'] == 2023) & (raw['campus'] == 'Universitywide')]
m['applicants'].iloc[0] * 100 / m['ag_completers'].iloc[0]

explanation:
the question tells us the formula: universitywide applicants divided by ag completers. we grab that one school row and do the division. almost every a-g completer applied so it is 99.06 percent.

q9: how many distinct california public high schools sent at least one freshman applicant to uc in fall 2025
answer: 193

sql:
select count(distinct high_school)
from schools
where fall_term = 2025
  and campus = 'Universitywide'
  and applicants > 0
  and school_type = 'High Schools (Public)';

pandas:
raw[(raw['fall_term'] == 2025) & (raw['campus'] == 'Universitywide') & (raw['applicants'] > 0) & (raw['school_type'] == 'High Schools (Public)')]['high_school'].nunique()

explanation:
we count unique school names that sent any applicant. filter to 2025, universitywide, public schools, and at least one applicant. the count is 193.

q10: of the five schools listed using uc berkeley 2022 to 2025 which one most outperforms its expected admit rate after controlling for a-g completion poverty applicant gpa and school size
answer: MISSION SENIOR HIGH SCHOOL

sql:
select high_school
from dash
where campus = 'Berkeley'
  and fall_term between 2022 and 2025
  and high_school in ('HERCULES HIGH SCHOOL','MISSION SENIOR HIGH SCHOOL','MONTEREY TRAIL HIGH SCHOOL','PHILLIP & SALA BURTON ACAD HS','RANCHO SAN JUAN HIGH SCHOOL')
group by high_school
order by avg(admit_rate_residual) desc
limit 1;

pandas:
five = ['HERCULES HIGH SCHOOL','MISSION SENIOR HIGH SCHOOL','MONTEREY TRAIL HIGH SCHOOL','PHILLIP & SALA BURTON ACAD HS','RANCHO SAN JUAN HIGH SCHOOL']
b = dash[(dash['campus'] == 'Berkeley') & (dash['fall_term'].between(2022, 2025)) & (dash['high_school'].isin(five))]
b.groupby('high_school')['admit_rate_residual'].mean().idxmax()

explanation:
the data already has a column called admit_rate_residual which is the actual rate minus the expected rate after those controls. a higher number means the school did better than expected. we average it per school for berkeley 2022 to 2025 and take the top one. mission senior high school is the highest.
