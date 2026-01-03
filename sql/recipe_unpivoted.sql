with recipe_unpivoted as ( UNPIVOT imported.recipe
        ON
(Item_Result,
Amount_Result) as result,
        (Item_Ingredient_0,
Amount_Ingredient_0) as ingredient0,
           (Item_Ingredient_1,
Amount_Ingredient_1) as ingredient1,
           (Item_Ingredient_2,
Amount_Ingredient_2) as ingredient2,
           (Item_Ingredient_3,
Amount_Ingredient_3) as ingredient3,
           (Item_Ingredient_4,
Amount_Ingredient_4) as ingredient4,
           (Item_Ingredient_5,
Amount_Ingredient_5) as ingredient5,
           (Item_Ingredient_6,
Amount_Ingredient_6) as ingredient6,
           (Item_Ingredient_7,
Amount_Ingredient_7)  as ingredient7
INTO
	NAME recipe_part VALUE (item_id,
	item_amount)
)
select
	ru."#" as recipe_id,
	classjob.abbreviation as job,
	classjob.v3 as job_ja,
ru.item_id,
	ru.item_amount,
	ru.recipe_part
from
	recipe_unpivoted as ru
left join imported.classjob on
	ru.crafttype = classjob.dohdoljobindex
where
			ru.item_id > 0
	and
	classjob.classjobcategory = 33	--DOH