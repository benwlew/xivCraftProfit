with
	flat_recipe as (
select
			r."#" as recipe_id,
	--Number,
	classjob.abbreviation as job,
			classjob.v3 as job_ja,
	--RecipeLevelTable,
	--v4,
	r.Item_Result as result_id,
			r.Amount_Result as result_amount,
			r.Item_Ingredient_0 as ingredient0_id,
			r.Amount_Ingredient_0 as ingredient0_amount,
			r.Item_Ingredient_1 as ingredient1_id,
			r.Amount_Ingredient_1 as ingredient1_amount,
			r.Item_Ingredient_2 as ingredient2_id,
			r.Amount_Ingredient_2 as ingredient2_amount,
			r.Item_Ingredient_3 as ingredient3_id,
			r.Amount_Ingredient_3 as ingredient3_amount,
			r.Item_Ingredient_4 as ingredient4_id,
			r.Amount_Ingredient_4 as ingredient4_amount,
			r.Item_Ingredient_5 as ingredient5_id,
			r.Amount_Ingredient_5 as ingredient5_amount,
			r.Item_Ingredient_6 as ingredient6_id,
			r.Amount_Ingredient_6 as ingredient6_amount,
			r.Item_Ingredient_7 as ingredient7_id,
			r.Amount_Ingredient_7 as ingredient7_amount,
from
			imported.recipe as r
left join imported.classjob on
	r.crafttype = classjob.dohdoljobindex
where
			r.item_result > 0
	and classjob.classjobcategory = 33
	--DOH
	),
	unpivot_recipe as (
select
			recipe_id,
			job,
			job_ja,
			result_id as item_id,
			result_amount as item_amount,
			'result' as recipe_part
from
			flat_recipe
union all
select
			recipe_id,
			job,
			job_ja,
			ingredient0_id as item_id,
			ingredient0_amount as item_amount,
			'ingredient0' as type
from
			flat_recipe
union all
select
			recipe_id,
			job,
			job_ja,
			ingredient1_id as item_id,
			ingredient1_amount as item_amount,
			'ingredient1' as type
from
			flat_recipe
union all
select
			recipe_id,
			job,
			job_ja,
			ingredient2_id as item_id,
			ingredient2_amount as item_amount,
			'ingredient2' as type
from
			flat_recipe
union all
select
			recipe_id,
			job,
			job_ja,
			ingredient3_id as item_id,
			ingredient3_amount as item_amount,
			'ingredient3' as type
from
			flat_recipe
union all
select
			recipe_id,
			job,
			job_ja,
			ingredient4_id as item_id,
			ingredient4_amount as item_amount,
			'ingredient4' as type
from
			flat_recipe
union all
select
			recipe_id,
			job,
			job_ja,
			ingredient5_id as item_id,
			ingredient5_amount as item_amount,
			'ingredient5' as type
from
			flat_recipe
union all
select
			recipe_id,
			job,
			job_ja,
			ingredient6_id as item_id,
			ingredient6_amount as item_amount,
			'ingredient6' as type
from
			flat_recipe
union all
select
			recipe_id,
			job,
			job_ja,
			ingredient7_id as item_id,
			ingredient7_amount as item_amount,
			'ingredient7' as type
from
			flat_recipe
	),
	shop_items as (
select
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
	result_id,
	true as two_job_craft
from
	flat_recipe
group by
	result_id
having
	count(result_id) > 1
)
select
	ur.*,
	i."Name" as item_name,
	ij."Name" as item_name_ja,
	case
		when tjc.two_job_craft = TRUE 
		then concat(i."Name", ' (', ur.item_id, ') (', ur.job, ')')
		else concat(i."Name", ' (', ur.item_id, ')')
	end as selectbox_label,
	case
		when tjc.two_job_craft = TRUE 
		then concat(ij."Name", ' (', ur.item_id, ') (', ur.job_ja, ')')
		else concat(ij."Name", ' (', ur.item_id, ')')
	end as selectbox_label_ja,
	concat(ij."Name", ' (', ur.item_id, ')') as selectbox_label_ja,
	i.Icon as item_icon,
	s.price_mid as shop_price,
	tjc.two_job_craft
from
	unpivot_recipe as ur
left join imported.item as i on
	ur.item_id = i."#"
left join imported.item_ja as ij on
	ur.item_id = ij."#"
left join shop_items as s on
	ur.item_id = s.item_id
left join two_job_crafts as tjc on
	ur.recipe_id = tjc.recipe_id
where
	ur.item_id > 0
	and i.IsUntradable = false
	and i.ItemSearchCategory != 0
	-- Exclude market prohibited items
order by
	ur.recipe_id asc,
	ur.recipe_part asc