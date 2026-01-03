with shop_items as (select
	distinct
			item as item_id,
			price_mid
from
			imported.gilshopitem
inner join imported.item on
	item."#" = gilshopitem.item
	),
	two_job_crafts as (
select
	any_value(recipe_id) as recipe_id,
	item_id,
	true as two_job_craft
from
	recipe_unpivoted as ru
where recipe_part = 'result'
group by
	item_id
having
	count(item_id) > 1
)
select
	ru.*,
	i."Name" as item_name,
	ij."Name" as item_name_ja,
	case
		when tjc.two_job_craft = TRUE 
		then concat(i."Name", ' (', ru.item_id, ') (', ru.job, ')')
		else concat(i."Name", ' (', ru.item_id, ')')
	end as selectbox_label,
	case
		when tjc.two_job_craft = TRUE 
		then concat(ij."Name", ' (', ru.item_id, ') (', ru.job_ja, ')')
		else concat(ij."Name", ' (', ru.item_id, ')')
	end as selectbox_label_ja,
	i.Icon as item_icon,
	s.price_mid as shop_price,
	tjc.two_job_craft
from
	recipe_unpivoted as ru
left join imported.item as i on
	ru.item_id = i."#"
left join imported.item_ja as ij on
	ru.item_id = ij."#"
left join shop_items as s on
	ru.item_id = s.item_id
left join two_job_crafts as tjc on
	ru.recipe_id = tjc.recipe_id
where
	ru.item_id > 0
	and i.IsUntradable = false
	and i.ItemSearchCategory != 0
	-- Exclude market prohibited items
order by
	ru.recipe_id asc,
	ru.recipe_part asc