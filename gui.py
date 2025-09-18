"""
TODO
- Handle multijob crafting
"""

from typing import List, Optional, Dict, Union
import duckdb
import polars as pl
import streamlit as st
# from st_aggrid import AgGrid


import config
from utils import utils
logger = utils.setup_logger(__name__)
import main


def get_recipe_list() -> [dict]:
    with duckdb.connect(config.DB_NAME) as db:
        query = """SELECT *, CONCAT(result_name, ' (', result_id, ')') as result_text from  recipe_price"""
        df = db.sql(query).pl()
        logger.info(f"Recipe list initialised")
    return df

# def get_ingredients(recipe_list: pl.DataFrame, item: int) -> Optional[list]:
#     """Get item ingredient list from local db

#     Args:
#         item (int): ID of the item  to check
        
#     Returns:
#         Optional[dict]: Item crafting ingredient dict, or None if request failsprint(details)
#     """
    
#     # Convert DataFrame to structured dictionary
#     df = recipe_list
#     query = f"""--sql
#             SELECT result_id, result_name, ingredient0_id, ingredient0_name, ingredient1_id, ingredient1_name, ingredient2_id, ingredient2_name, ingredient3_id, ingredient3_name,
#                 ingredient4_id, ingredient4_name, ingredient5_id, ingredient5_name, ingredient6_id, ingredient6_name, ingredient7_id, ingredient7_name from df
#                 WHERE result_id = {item}"""
#     df = duckdb.sql(query).pl()
    
#     null_cols = [col for col in df.columns if df[col][0] in [None,0,-1,""]]
#     # st.write(null_cols)
#     df = df.drop(null_cols)
    
#     df_dict = df.to_dict(as_series=False)
#     # st.write(df_dict)
    
#     for k,v in df_dict.items():
#         st.write(f"{v}")
    
    # item_dict = {}
    # for col in df.columns:
    #     if col.startswith(("result", "ingredient")):
    #         prefix, *suffix = col.split("_")
    #         item_dict.setdefault(prefix, {})["_".join(suffix)] = df[col][0]
    
    # # Remove ingredients with zero amount
    # ingredients_to_remove = [
    # prefix for prefix in item_dict 
    # if prefix.startswith("ingredient") 
    # and item_dict[prefix].get("amount", 0) == 0
    # ]
    
    # for ingredient in ingredients_to_remove:
    #     item_dict.pop(ingredient)
    
#     return item_dict

def print_result(item_data: dict):
    st.markdown("##")
    st.markdown("## Craft Details")

    res_grid={}

    for x in range(2):
        y = st.columns(6)
        for y, col in enumerate(y):
            coord = (x,y)
            tile = col.container()
            res_grid[coord] = tile

    row = 0
    res_grid[(row,0)].markdown("**Item**")
    res_grid[(row,1)].markdown("**ID**")
    res_grid[(row,2)].markdown("**Number per craft**")
    res_grid[(row,3)].markdown("**Shop price**")
    res_grid[(row,4)].markdown("**NQ**")
    res_grid[(row,5)].markdown("**HQ**")
    
    v = item_data["result"]
    res_grid[(1,0)].write(v["name"])
    res_grid[(1,1)].write(f"{v["id"]}")
    with res_grid[(1,2)]:
        st.write("1")
        if v["amount"] > 1:
            st.write(f"{v["amount"]}")
    with res_grid[(1,3)]:
        if v["shop_price"]:
            st.write(f"{v["shop_price"]}")
            if v["amount"] > 1:
                st.write(f"Price per craftable amount: {v["shop_price"] * v["amount"]}")
        else:
            st.write(":red[No Shop]")
    with res_grid[(1,4)]:
        st.write(f"{v["nq"]["minPrice"]}")
        if v["amount"] > 1:
            st.write(f"Price per craftable amount: {v["nq"]["minPrice"] * v["amount"]}")
    with res_grid[(1,5)]:
        if v.get("hq"):
            st.write(f"{v["hq"]["minPrice"]}")
            if v["amount"] > 1:
                st.write(f"Price per craftable amount: {v["hq"]["minPrice"] * v["amount"]}")
        else:
            st.write(":red[No HQ item]")
    

    prices = {"Shop": v.get("shop_price"),
            "Marketboard (NQ)": v.get("nq", {}).get("minPrice"),
            "Marketboard (HQ)": v.get("hq", {}).get("minPrice")}    
    prices = {source: price for source, price in prices.items() if price is not None}
    
    res_min_source = min(prices, key=prices.get) 
    res_min_price = prices[res_min_source]
    # st.markdown("###")
    st.markdown(f"##### Cheapest buyable from is :blue[{res_min_source}]: :red[{res_min_price} gil]")
    if v["amount"] > 1:
        st.write(f"Price per craftable amount ({v["amount"]}: {v["amount"] * {res_min_price}}")
    
    return(res_min_source, res_min_price)




@st.fragment
def print_ingredients(item_data: dict):

    st.markdown("#")
    st.markdown("# Ingredients")
    

    ing_grid={}

    for x in range(len(item_data)):
        y = st.columns(7)
        for y, col in enumerate(y):
            coord = (x,y)
            tile = col.container()
            # tile.write(f"{x}_{y}")
            ing_grid[coord] = tile
    
    
    ### TODO: Not sure determining max bounds of grid is needed
    ing_coords = list(ing_grid.keys())
    x,y = [r for r, c in ing_coords],[c for r, c in ing_coords]
    ing_rows, ing_cols = max(x)+1, max(y)+1 
    # print(ing_rows)
    # print(ing_cols)

    row = 0
    ing_grid[(row,0)].markdown("**Ingredient**")
    ing_grid[(row,1)].markdown("**ID**")
    ing_grid[(row,2)].markdown("**Number Needed**")
    ing_grid[(row,3)].markdown("**Shop price**")
    ing_grid[(row,4)].button("NQ", help="Click to set all to NQ", type="tertiary")
    ing_grid[(row,5)].button("NQ", help="Click to set all to HQ", type="tertiary")
    ing_grid[(row,6)].markdown("**Cost**")



    craft_cost = 0
    for row, (k,v) in enumerate(item_data.items()):
        if k.startswith("ingredient"):
            cost = 0
            ing_grid[(row,0)].write(v["name"])
            ing_grid[(row,1)].write(f"{v["id"]}")
            ing_grid[(row,2)].write(f"{v["amount"]}")
            with ing_grid[(row,3)]:
                if v["shop_price"]:
                    shop_qty = st.number_input("no_shop", min_value = 0, max_value = v["amount"], key=f"{ing_grid[(row,3)]}_shop_qty", label_visibility="hidden")
                    st.write(f"Price each: {v["shop_price"]}")
                    shop_total = v["shop_price"] * shop_qty 
                    st.write(f"{shop_total}")
                    cost += shop_total
                else:
                    st.write(":red[No Shop]")
            with ing_grid[(row,4)]:
                nq_qty = st.number_input("no_nq", min_value = 0, max_value = v["amount"], value=v["amount"],  key=f"{ing_grid[(row,3)]}_nq_qty", label_visibility="hidden")
                st.write(f"Price each: {v["nq"]["minPrice"]}")
                nq_total = v["nq"]["minPrice"] * nq_qty
                st.write(f"{nq_total}")
                cost += nq_total
            with ing_grid[(row,5)]:
                if v.get("hq"):
                    hq_qty = st.number_input("no_hq", min_value = 0, max_value = v["amount"], key=f"{ing_grid[(row,3)]}_hq_qty", label_visibility="hidden")
                    st.write(f"Price each: {v["hq"]["minPrice"]}")
                    hq_total = v["hq"]["minPrice"] * hq_qty
                    st.write(f"{hq_total}")
                    cost += hq_total
                else:
                    st.write(":red[No HQ item]")
            ing_grid[(row,6)].write(f"{cost}")
            craft_cost += cost
    
    st.markdown(f"#### Cheapest buyable from is :red[{craft_cost} gil]")
    # if v["amount"] > 1:
    #     st.write(f"Price per craftable amount ({v["amount"]}: {v["amount"] * {craft_cost}}")




    # for k,v in item_data.items():
    #     if k.startswith("ingredient"):
    #         cols = st.columns(4)
    #         row.append(cols)
    #         # ingredients_col, nq_col, hq_col, total_col = st.columns(4)
    #         # ingredients_container = st.container(border=True)
    #         for col in row:# with ingredients_col:
    #             st.write(f'### {v["name"]} ({v["id"]})')
    #             st.write(f'Number required: {v["amount"]}')
    #             st.write(f'Shop price: {v["shop_price"]}') ## Conditional format red if None
    #             # with nq_col:
    #             st.write(f'NQ price: {v["nq"]["minPrice"]}')
    #             st.write(f'NQ velocity: ({v["nq"]["velocity"]:.0f}/day)')
    #             # with hq_col:
    #             try:
    #                 st.write(f'HQ price: {v["hq"]["minPrice"]}')
    #                 st.write(f'HQ velocity: ({v["hq"]["velocity"]:.0f}/day)')
    #             except:
    #                 pass




    """
    TOTAL = 100

    def update(last):
        change = ss.A + ss.B + ss.C - TOTAL
        sliders = ['A','B','C']    
        last = sliders.index(last)
        # Modify to 'other two'
        # Add logic here to deal with rounding and to protect against edge cases (if one of the 'others'
        # doesn't have enough room to accomodate the change)
        ss[sliders[(last+1)%3]] -= change/2
        ss[sliders[(last+2)%3]] -= change/2


    st.number_input('A', key='A', min_value=0, max_value=100, value = 50, on_change=update, args=('A',))
    st.number_input('B', key='B', min_value=0, max_value=100, value = 25, on_change=update, args=('B',))
    st.number_input('C', key='C', min_value=0, max_value=100, value = 25, on_change=update, args=('C',))
    """




def print_analysis(item_data: dict):
    nq_craft_cost = 0
    hq_craft_cost = 0
    buy_hq_total = 0
    analysis_container = st.container(border=True)
    for k, v in item_data.items():
        name = v.get("name")
        id = v.get("id")
        amount = v.get("amount")
        shop_unit = v.get("shop_price") if v.get("shop_price") else None
        nq_unit = v.get("nq",{}).get(f"minPrice",None)
        hq_unit = v.get("hq",{}).get(f"minPrice",None)
        shop_total = shop_unit * amount if shop_unit else None
        nq_total = nq_unit * amount if nq_unit else None
        hq_total = hq_unit * amount if hq_unit else None
        nq_velocity = v.get("nq",{}).get(f"velocity",None)
        hq_velocity = v.get("hq",{}).get(f"velocity",None)

        if k.startswith('result'):
            ###TODO: Add source/quality of each item
            buy_hq_total = hq_total
    
    for k, v in item_data.items():
        name = v.get("name")
        id = v.get("id")
        amount = v.get("amount")
        shop_unit = v.get("shop_price") if v.get("shop_price") else None
        nq_unit = v.get("nq",{}).get(f"minPrice",None)
        hq_unit = v.get("hq",{}).get(f"minPrice",None)
        shop_total = shop_unit * amount if shop_unit else None
        nq_total = nq_unit * amount if nq_unit else None
        hq_total = hq_unit * amount if hq_unit else None
        nq_velocity = v.get("nq",{}).get(f"velocity",None)
        hq_velocity = v.get("hq",{}).get(f"velocity",None)

        if k.startswith('ingredient'):
            ###TODO: Add source/quality of each item
            nq_craft_cost += min(x for x in [shop_total, nq_total, hq_total] if x is not None)
            if hq_total is not None:
                hq_craft_cost += min(x for x in [shop_total, hq_total] if x is not None and hq_total)
            else:
                hq_craft_cost += min(x for x in [shop_total, nq_total, hq_total] if x is not None)
            # st.write(f"Cumulative Crafting Cost buying NQ mats: {nq_craft_cost:,.0f}")
            # st.write(f"Cumulative Crafting Cost buying HQ mats: {hq_craft_cost:,.0f}")

    nq_craft_pl = buy_hq_total - nq_craft_cost
    hq_craft_pl = buy_hq_total - hq_craft_cost
    nq_craft_pl_perc =  nq_craft_pl / buy_hq_total
    hq_craft_pl_perc =  hq_craft_pl / buy_hq_total

    analysis_container.write(f"### Profit Analysis")
    # analysis_container.write(f"Buy completed NQ cost: {buy_nq_total:,.0f}") if buy_nq_total else None
    analysis_container.write(f"Buy completed HQ cost: {buy_hq_total:,.0f}") if buy_hq_total else None
    analysis_container.write(f"Craft HQ from buying NQ items cost: {nq_craft_cost:,.0f}") if nq_craft_cost else None
    analysis_container.write(f"Craft HQ from buying HQ items cost: {hq_craft_cost:,.0f}") if hq_craft_cost else None
    analysis_container.write("")
    analysis_container.write(f"Craft HQ from buying NQ items P/L: {buy_hq_total:,.0f} - {nq_craft_cost:,.0f} = {nq_craft_pl:,.0f} ({nq_craft_pl_perc:,.2%})")
    if nq_craft_pl_perc <= 0:
        analysis_container.error("Warning: Crafting this item will result in a loss!")
    elif nq_craft_pl_perc < 0.2:
        analysis_container.error("Note: Low profit margin (below 20%)!")
            
    analysis_container.write(f"\nCraft HQ from buying HQ items P/L: {buy_hq_total:,.0f} - {hq_craft_cost:,.0f} = {hq_craft_pl:,.0f} ({hq_craft_pl_perc:,.2%})")
    if hq_craft_pl_perc <= 0:
        analysis_container.error("Warning: Crafting this item will result in a loss!")
    elif hq_craft_pl_perc < 0.2:
        analysis_container.error("Note: Low profit margin (below 20%)!")


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    recipe_list = get_recipe_list()
    selectbox_recipe_list = duckdb.sql("SELECT result_text, result_id from recipe_list").pl()
    # st.write(selectbox_recipe_list)
    
    st.title("FFXIV Craft or Buy Checker")
    st.markdown("")
    st.text("""Select recipe to check if better value to craft from ingredients or buy from marketboard.\nNumber in parentheses is item id.""")
    item_selectbox = st.selectbox("label", options=selectbox_recipe_list ,index=0,label_visibility="hidden") ###TODO Change index back to None
    
    st.data_editor(recipe_list, editable=True)
    st.markdown("""
                |1|2|3|
                |---|---|---|
                |4|5|5|
                """)

    fetch_button = st.button("Fetch Marketboard data from Universalis")
    if fetch_button:
        if not item_selectbox:
            st.error("Select an item first!")
        else:
            ### TODO Hide buttone while fetching
            with st.spinner(text="In progress..."):
                item_id = duckdb.sql(f"SELECT result_id from selectbox_recipe_list where result_text = '{item_selectbox}'").pl()
                item_id = item_id[0,0]
                test = main.fetch_universalis(item_id)

                print_result(test)
                # print_analysis(test)
                print_ingredients(test)
            
            # write_formatted_price(test)
    
    ### TODO FIX: Some recipes don't work properly like Amateur's stuff
    
    
    # with st.form("form"):
    #     st.write("stuff inside form")
    #     slider_val = st.slider("form slider")
    #     checkbox_val = st.checkbox("form checkbox")

    #     submitted = st.form_submit_button("submit")
    #     if submitted:
    #         st.write("slider", slider_val, "checkbox", checkbox_val)


    # tab1, tab2, tab3 = st.tabs(["1","2","3"])

    # with tab1:
    #     st.header("1")
    #     st.markdown("""wow!!!!!!!!""")

    # st.container()
    # st.toggle("yes","no")
    # st.download_button("yes","no")