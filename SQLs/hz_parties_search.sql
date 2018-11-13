select * from 
(
select 
	party_id,
	(select distinct person_number from per_all_people_f x where x.person_id = a.orig_system_reference) person_number,
	party_name, 
	party_unique_name,
	last_updated_by,
	last_update_date,
	creation_date,
	created_by
from hz_parties a
order by creation_date desc
)
where person_number = nvl(:p_person_number, person_number)
and party_name like nvl(:p_party_name, party_name)

