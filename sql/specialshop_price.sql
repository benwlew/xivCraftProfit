with specialshop as (select "#", "Name", columns('_0_') from imported.SpecialShop
union all
select "#", "Name", columns('_1_') from imported.SpecialShop
union all
select "#", "Name", columns('_2_') from imported.SpecialShop
union all
select "#", "Name", columns('_3_') from imported.SpecialShop
union all
select "#", "Name", columns('_4_') from imported.SpecialShop
union all
select "#", "Name", columns('_5_') from imported.SpecialShop
union all
select "#", "Name", columns('_6_') from imported.SpecialShop
union all
select "#", "Name", columns('_7_') from imported.SpecialShop
union all
select "#", "Name", columns('_8_') from imported.SpecialShop
union all
select "#", "Name", columns('_9_') from imported.SpecialShop
union all
select "#", "Name", columns('_10_') from imported.SpecialShop
union all
select "#", "Name", columns('_11_') from imported.SpecialShop
union all
select "#", "Name", columns('_12_') from imported.SpecialShop
union all
select "#", "Name", columns('_13_') from imported.SpecialShop
union all
select "#", "Name", columns('_14_') from imported.SpecialShop
union all
select "#", "Name", columns('_15_') from imported.SpecialShop
union all
select "#", "Name", columns('_16_') from imported.SpecialShop
union all
select "#", "Name", columns('_17_') from imported.SpecialShop
union all
select "#", "Name", columns('_18_') from imported.SpecialShop
union all
select "#", "Name", columns('_19_') from imported.SpecialShop
union all
select "#", "Name", columns('_20_') from imported.SpecialShop
union all
select "#", "Name", columns('_21_') from imported.SpecialShop
union all
select "#", "Name", columns('_22_') from imported.SpecialShop
union all
select "#", "Name", columns('_23_') from imported.SpecialShop
union all
select "#", "Name", columns('_24_') from imported.SpecialShop
union all
select "#", "Name", columns('_25_') from imported.SpecialShop
union all
select "#", "Name", columns('_26_') from imported.SpecialShop
union all
select "#", "Name", columns('_27_') from imported.SpecialShop
union all
select "#", "Name", columns('_28_') from imported.SpecialShop
union all
select "#", "Name", columns('_29_') from imported.SpecialShop
union all
select "#", "Name", columns('_30_') from imported.SpecialShop
union all
select "#", "Name", columns('_31_') from imported.SpecialShop
union all
select "#", "Name", columns('_32_') from imported.SpecialShop
union all
select "#", "Name", columns('_33_') from imported.SpecialShop
union all
select "#", "Name", columns('_34_') from imported.SpecialShop
union all
select "#", "Name", columns('_35_') from imported.SpecialShop
union all
select "#", "Name", columns('_36_') from imported.SpecialShop
union all
select "#", "Name", columns('_37_') from imported.SpecialShop
union all
select "#", "Name", columns('_38_') from imported.SpecialShop
union all
select "#", "Name", columns('_39_') from imported.SpecialShop
union all
select "#", "Name", columns('_40_') from imported.SpecialShop
union all
select "#", "Name", columns('_41_') from imported.SpecialShop
union all
select "#", "Name", columns('_42_') from imported.SpecialShop
union all
select "#", "Name", columns('_43_') from imported.SpecialShop
union all
select "#", "Name", columns('_44_') from imported.SpecialShop
union all
select "#", "Name", columns('_45_') from imported.SpecialShop
union all
select "#", "Name", columns('_46_') from imported.SpecialShop
union all
select "#", "Name", columns('_47_') from imported.SpecialShop
union all
select "#", "Name", columns('_48_') from imported.SpecialShop
union all
select "#", "Name", columns('_49_') from imported.SpecialShop
union all
select "#", "Name", columns('_50_') from imported.SpecialShop
union all
select "#", "Name", columns('_51_') from imported.SpecialShop
union all
select "#", "Name", columns('_52_') from imported.SpecialShop
union all
select "#", "Name", columns('_53_') from imported.SpecialShop
union all
select "#", "Name", columns('_54_') from imported.SpecialShop
union all
select "#", "Name", columns('_55_') from imported.SpecialShop
union all
select "#", "Name", columns('_56_') from imported.SpecialShop
union all
select "#", "Name", columns('_57_') from imported.SpecialShop
union all
select "#", "Name", columns('_58_') from imported.SpecialShop
union all
select "#", "Name", columns('_59_') from imported.SpecialShop)
select 
item_receive_0_0 as receive_item_id,
"#" as cost_item_id,
"Name" as cost_item_name,
count_cost_0_0 as cost_item_amount
from specialshop
where cost_item_name like ('%Tomestone%')
and cost_item_amount > 0