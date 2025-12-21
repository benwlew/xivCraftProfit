"""
TODO
- Remove row gaps
- Force url change on DC selection
- Add Japanese language support
- Make sure large numbers fit in st.metrics
- Add item source, e.g. currency if vendor
- Add world functionality (cheapest selling on dc vs world)
- Add checkbox to consider p/l against NQ
- Add item number dependencies for number_input (never exceed total needed); not sure how to implement
- Clean up repeated variable assignment
"""

import duckdb
import requests
import polars as pl
import streamlit as st
import json


DB_NAME = "ffxiv_price.duckdb"


def icon_link(icon: int) -> str:
    folder = f"{icon:0>6}"
    folder = folder[:3] + "000"
    icon_link = f"https://v2.xivapi.com/api/asset?path=ui/icon/{folder}/{icon:0>6}.tex&format=png"

    return icon_link


@st.cache_data
def get_all_recipes() -> pl.DataFrame:
    with duckdb.connect(DB_NAME) as con:
        query = """SELECT *, CONCAT(result_name, ' (', result_id, ')') as result_text from  recipe_price"""
        df = con.sql(query).pl()

    df = df.rename({"pk":"recipe_id", "Icon":"result_icon"})
    df = df.with_columns(
        pl.when(pl.col("result_id").is_duplicated())
        .then(pl.concat_str(["result_text", pl.lit(" ("), "job", pl.lit(")")]))
        .otherwise("result_text")
        .alias("result_text")
    )
    return df


def get_worlds_dc() -> pl.DataFrame:
    with duckdb.connect(DB_NAME) as con:
        query = """SELECT * from  world_dc"""
        df = con.sql(query).pl()
    return df


@st.cache_data
def get_recipe_ingr(all_recipes_df: pl.DataFrame, recipe_id: int) -> pl.DataFrame:
    # Get recipe ingredient IDs to be passed to API request
    
    df = all_recipes_df.filter(pl.col("recipe_id") == recipe_id)

    # Unpivot wide table (1 row per recipe) into long table(e.g. ingredients0, ingredients1 -> 2 rows of ingredients )
    df = df.with_columns(
        pl.concat_list(pl.col("^ingredient\\d.*_id$")).alias("ingredient_id")
    ).drop(pl.col("^ingredient\\d.*_id$"))
    df = df.with_columns(
        pl.concat_list(pl.col("^ingredient\\d.*_name$")).alias("ingredient_name")
    ).drop(pl.col("^ingredient\\d.*_name$"))
    df = df.with_columns(
        pl.concat_list(pl.col("^ingredient\\d.*_shop_price$")).alias(
            "ingredient_shop_price"
        )
    ).drop(pl.col("^ingredient\\d.*_shop_price$"))
    df = df.with_columns(
        pl.concat_list(pl.col("^ingredient\\d.*_amount$")).alias("ingredient_amount")
    ).drop(pl.col("^ingredient\\d.*_amount$"))
    df = df.explode(
        pl.col(
            "ingredient_id",
            "ingredient_name",
            "ingredient_shop_price",
            "ingredient_amount",
        )
    )
    df = df.filter(pl.col("ingredient_id") > 0)
    df = df.drop("CanQuickSynth", "CanHq", "IsExpert")
    lookup_item_df = df.with_columns(pl.col("recipe_id","job"),pl.lit(None).alias("result_id"),pl.lit(None).alias("result_name"),
                                     pl.lit(None).alias("result_shop_price"),pl.lit(None).alias("result_amount"), 
                                     pl.lit(None).alias("result_icon"),pl.lit(None).alias("result_text"),
                                     pl.col("result_id").alias("ingredient_id"), pl.col("result_name").alias("ingredient_name"),
                                     pl.col("result_shop_price").alias("ingredient_shop_price"), pl.col("result_amount").alias("ingredient_amount")).unique()
    df = pl.concat([df, lookup_item_df])
    

    return df


@st.cache_data
def price_lookup(lookup_items_df: pl.DataFrame, region: str) -> pl.DataFrame:
    
    lookup_item_ids  =  [
        str(id) for id in lookup_items_df["ingredient_id"]]
    url = f"https://universalis.app/api/v2/{region}/{','.join(lookup_item_ids)}"
    
    # GET from Universalis API twice per item - once each for NQ/HQ
    raw_market_data = {}
    for hq in [False, True]:
        parameters = {
            "hq": hq,
            "listings": 100,
            "fields": "items.nqSaleVelocity,items.hqSaleVelocity,items.listings.pricePerUnit,items.listings.onMannequin,listings.worldName",
        }
        response = requests.get(url, params=parameters)

        # Unpivot and unnest json, filter out Mannquin items (false listings), find minimum price for each group, then merge NQ/HQ data together
        data = response.json()["items"]
        data = pl.DataFrame(data).unpivot().rename({"variable": "id"}).unnest("value")
        data = data.explode("listings").unnest("listings")
        data = data.filter(
            (pl.col("onMannequin") == False) | pl.col("onMannequin").is_null()
        )
        data = data.group_by("id").min()
        if hq:
            hq_data = data.select(
                pl.col("id"),
                pl.col("pricePerUnit").alias("hq_price"),
                pl.col("hqSaleVelocity").alias("hq_velocity"),
            )
            raw_market_data["hq"] = response.json()
        elif not hq:
            nq_data = data.select(
                pl.col("id"),
                pl.col("pricePerUnit").alias("nq_price"),
                pl.col("nqSaleVelocity").alias("nq_velocity"),
            )
            raw_market_data["nq"] = response.json()

    market_data = nq_data.join(hq_data, on="id").sort("id").cast(pl.Int64).rename({"id":"ingredient_id"})

    return market_data


def join_dfs(lookup_items_df: pl.DataFrame, prices_df: pl.DataFrame) -> pl.DataFrame:
    combined_df = lookup_items_df.join(prices_df, on="ingredient_id", how="left").with_row_index()
    return combined_df


def print_result(df: pl.DataFrame) -> int:
    ### Create grid for item

    result_grid = {}
    for x in range(2):
        y = st.columns(6, border=True, gap=None)
        for y, col in enumerate(y):
            coord = (x, y)
            tile = col.container()
            result_grid[coord] = tile

    name = df.item(0, "ingredient_name")
    id = df.item(0, "ingredient_id")
    amount = df.item(0, "ingredient_amount")
    shop_price = df.item(0, "ingredient_shop_price")
    nq_price = df.item(0, "nq_price")
    nq_velocity = df.item(0, "nq_velocity")
    hq_price = df.item(0, "hq_price")
    hq_velocity = df.item(0, "hq_velocity")

    row = 0
    result_grid[(row, 0)].markdown("**Item**")
    result_grid[(row, 1)].markdown("**ID**")
    result_grid[(row, 2)].markdown("**Number per craft**")
    result_grid[(row, 3)].markdown("**Shop price**")
    result_grid[(row, 4)].markdown("**NQ Price**")
    result_grid[(row, 5)].markdown("**HQ Price**")


    # with result_grid[(row, 1)]:
    #     if int(id) in all_recipes_df["result_id"]:
    #         st.markdown(f"[{id}](/?id={id})")
    #     else:
    #         st.markdown(id)

    # result_grid[(row, 2)].markdown(str(amount))

    # with result_grid[(row, 3)]:
    #     if shop_price is None:
    #         st.write(":red[N/A  \n(Not sold in shop)]")
    #     else:
    #         shop_qty = st.number_input(
    #             "num_shop",
    #             min_value=0,
    #             max_value=amount,
    #             key=f"{id}_shop_qty",
    #             label_visibility="hidden",
    #         )
    #         shop_total = shop_price * shop_qty
    #         st.write(f"{shop_total:,} gil ({shop_price:,} gil each)")
            
    # with result_grid[(row, 4)]:
    #     if nq_price is None:
    #         st.write(":red[N/A  \n(No NQ available)]")
    #     else:
    #         nq_qty = st.number_input(
    #             "num_nq",
    #             min_value=0,
    #             max_value=amount,
    #             value=amount,
    #             key=f"{id}_nq_qty",
    #             label_visibility="hidden",
    #         )
    #         nq_total = nq_price * nq_qty
    #         st.write(f"{nq_total:,} gil ({nq_price:,} gil each)")
    #         st.write(f"Velocity: {nq_velocity:,}/day")
            
    # with result_grid[(row, 5)]:
    #     if hq_price is None:
    #         st.write(":red[N/A  \n(No HQ available)]")
    #     else:
    #         hq_qty = st.number_input(
    #             "num_hq",
    #             min_value=0,
    #             max_value=amount,
    #             key=f"{id}_hq_qty",
    #             label_visibility="hidden",
    #         )
    #         hq_total = hq_price * hq_qty
    #         st.write(f"{hq_total:,} gil ({hq_price:,} gil each)")
    #         st.write(f"Velocity: {nq_velocity:,}/day")
            


    # df
    # df_dict = df.to_dicts()
    # # df_dict

    result_grid[(row, 0)].write(name)
    result_grid[(row, 1)].write(str(id))
    result_grid[(row, 2)].write(f"{amount}")
    with result_grid[(row, 3)]:
        if shop_price is None:
            st.write(":red[N/A  \n(Not sold in shop)]")
        else:
            st.write(f"{shop_price:,}")
    with result_grid[(row, 4)]:
        if nq_price is None:
            st.write(":red[N/A  \n(No NQ available)]")
        else:
            st.write(f"{nq_price:,}")
            st.write(f"Velocity: {nq_velocity:,}/day")
    with result_grid[(row, 5)]:
        if hq_price is None:
            st.write(":red[N/A  \n(No HQ available)]")
        else:
            st.write(f"{hq_price:,}")
            st.write(f"Velocity: {hq_velocity:,}/day")

    try:
        hq_velocity = hq_velocity
    except:
        hq_velocity = 0
    try:
        nq_velocity = nq_velocity
    except:
        nq_velocity = 0
    try:
        total_velocity = hq_velocity + nq_velocity
        return total_velocity
    except:
        return None


def print_metrics(result_df: pl.DataFrame, craft_cost_total: int) -> float:
    st.markdown("## Craft Details")
    # st.image(icon_link(icon))

    min_price_df = result_df.select(pl.col("ingredient_shop_price", "nq_price","hq_price")).unpivot(variable_name="source", value_name="price")
    min_price_df = min_price_df.filter(pl.col("price") == pl.col("price").min()).unique()
    
    result_min_source = min_price_df.select(pl.col("source")).item()
    result_min_price = min_price_df.select(pl.col("price")).item()
    

    name = result_df.item(0, "ingredient_name")
    id = result_df.item(0, "ingredient_id")
    shop_price = result_df.item(0, "ingredient_shop_price")
    nq_price = result_df.item(0, "nq_price")
    nq_velocity = result_df.item(0, "nq_velocity")
    hq_velocity = result_df.item(0, "hq_velocity")
    
    metric_col1, metric_col2, metric_col3, metric_col4, metric_col5, metric_col6 = (
        st.columns(6, border=True, gap=None)
    )

    amount = result_df.item(0, "ingredient_amount")
    craft_cost_each = int(craft_cost_total / amount)
    try:
        hq_price_each = result_df.item(0, "hq_price")
        hq_price_total = hq_price_each * amount
        pl_each = hq_price_each - craft_cost_each
        pl_total = pl_each * amount
        pl_perc = pl_each / hq_price_each

        with metric_col1:
            with st.container():
                if amount == 1:
                    st.metric(f"Craft Cost", f"{craft_cost_each:,} gil")
                elif amount > 1:
                    st.metric(
                        f"Craft Cost", f"{craft_cost_total:,} ({craft_cost_each:,} gil)"
                    )
        with metric_col2:
            with st.container():
                if amount == 1:
                    st.metric(
                        f"Profit/Loss",
                        f"{pl_each:,} gil",
                        f"{pl_perc:.2%}",
                        help="Calculated agains HQ buy price - assuming that crafters will always aim for HQ",
                    )
                if amount > 1:
                    st.metric(
                        f"Profit/Loss",
                        f"{pl_total:,} gil ({pl_each:,} gil each)",
                        f"{pl_perc:.2%}",
                        help="Calculated agains HQ buy price - assuming that crafters will always aim for HQ",
                    )
        with metric_col4:
            with st.container():
                if amount == 1:
                    st.metric(
                        f"Cheapest price: :blue[{result_min_source.split('_')[0]}]",
                        f"{result_min_price:,} gil",
                    )
                elif amount > 1:
                    st.metric(
                        f"Cheapest price: :blue[{result_min_source.split('_')[0]}]",
                        f"{result_min_price * amount:,} gil ({result_min_price:,} gil each)",
                        help="Number in parentheses is single item cost",
                    )
        with metric_col5:
            with st.container():
                if hq_price is not None:
                    if amount == 1:
                        st.metric(f"HQ Price", f"{hq_price_each:,} gil")
                    if amount > 1:
                        st.metric(
                            f"HQ Price",
                            f"{hq_price_total:,} gil ({hq_price_each:,} gil each)",
                            help="Number in parentheses is single item cost",
                        )
    except:
        nq_price_each = result_df.item(0, "nq_price")
        nq_price_total = nq_price_each * amount
        pl_each = nq_price_each - craft_cost_each
        pl_total = pl_each * amount
        pl_perc = pl_each / nq_price_each
    return pl_perc



def print_pl_warning(pl_perc: float) -> None:
    if pl_perc is None:
        return
    elif pl_perc < 0:
        st.error(
            f"Buying ingredients and crafting this item will result in a loss: {pl_perc:,.2%}",
            icon="🔥",
        )
    elif pl_perc < 0.25:
        st.warning(f"Low profit margin (below 25%): {pl_perc:,.2%}", icon="🚨")
    else:
        st.success(f"Profit above 25%: {pl_perc:,.2%}", icon="🥳")


def print_velocity_warning(velocity: int) -> None:
    if velocity is None:
        return
    elif velocity < 15:
        st.error(f"Item won't sell: {velocity:,}/day", icon="🔥")
    elif velocity < 99:
        st.warning(f"Item will sell really slowly: {velocity:,}/day", icon="🚨")
    else:
        st.success(f"Item will sell: {velocity:,}/day", icon="🥳")


@st.fragment
def print_ingredients(df: pl.DataFrame) -> int:
    result_df = df.filter(pl.col("result_id").is_null())
    ingr_df = df.filter(pl.col("result_id").is_not_null())
    
    st.markdown("")
    st.markdown("# Ingredients")
    st.text(
        "All items are set to NQ by default, but can be adjusted. The cost will update dynamically as item amounts are changed.  \nEach column is set to max out at the number needed, but it is possible to increase numbers over this limit when using multiple columns; to avoid this, users should lower NQ after increasing HQ and vice versa."
    )
    st.markdown("")
    ### Create grid for items
    ingr_grid = {}
    for x in range(len(ingr_df) + 1):
        y = st.columns(7, border=True, gap=None)
        for y, col in enumerate(y):
            coord = (x, y)
            tile = col.container()
            ingr_grid[coord] = tile

    # Create grid header row
    row = 0
    ingr_grid[(row, 0)].markdown("**Ingredient**")
    ingr_grid[(row, 1)].markdown(
        "**ID**",
        help="Click link to lookup item profit/loss of subcraft (opens in new tab)",
    )
    ingr_grid[(row, 2)].markdown("**Required**")
    ingr_grid[(row, 3)].markdown("**Shop price**")
    ### TODO Buttons to set all don't work yet
    ingr_grid[(row, 4)].button(
        "**NQ**",
        help="Click to set all to NQ",
        type="tertiary",
    )
    ingr_grid[(row, 5)].button(
        "**HQ**",
        help="Click to set all to HQ",
        type="tertiary",
    )
    ingr_grid[(row, 6)].markdown("**Cost**")


    # Fill row/columnm in grid
    craft_cost_total = 0

    for row in range(1, len(ingr_df) + 1):
        row_cost = 0
        index = row - 1
        name = ingr_df.item(index, "ingredient_name")
        id = ingr_df.item(index, "ingredient_id")
        amount = ingr_df.item(index, "ingredient_amount")
        shop_price = ingr_df.item(index, "ingredient_shop_price")
        nq_price = ingr_df.item(index, "nq_price")
        nq_velocity = ingr_df.item(index, "nq_velocity")
        hq_price = ingr_df.item(index, "hq_price")
        hq_velocity = ingr_df.item(index, "hq_velocity")

        # ingr_grid[(row, 0)].image(image_rul)
        ingr_grid[(row, 0)].markdown(name)

        with ingr_grid[(row, 1)]:
            if int(id) in all_recipes_df["result_id"]:
                st.markdown(f"[{id}](/?id={id})")
            else:
                st.markdown(id)

        ingr_grid[(row, 2)].markdown(str(amount))

        with ingr_grid[(row, 3)]:
            if shop_price is None:
                st.write(":red[N/A  \n(Not sold in shop)]")
            else:
                shop_qty = st.number_input(
                    "num_shop",
                    min_value=0,
                    max_value=amount,
                    key=f"{id}_shop_qty",
                    label_visibility="hidden",
                )
                shop_total = shop_price * shop_qty
                st.write(f"{shop_total:,} gil ({shop_price:,} gil each)")
                row_cost += shop_total
        with ingr_grid[(row, 4)]:
            if nq_price is None:
                st.write(":red[N/A  \n(No NQ available)]")
            else:
                nq_qty = st.number_input(
                    "num_nq",
                    min_value=0,
                    max_value=amount,
                    value=amount,
                    key=f"{id}_nq_qty",
                    label_visibility="hidden",
                )
                nq_total = nq_price * nq_qty
                st.write(f"{nq_total:,} gil ({nq_price:,} gil each)")
                st.write(f"Velocity: {nq_velocity:,}/day")
                row_cost += nq_total
        with ingr_grid[(row, 5)]:
            if hq_price is None:
                st.write(":red[N/A  \n(No HQ available)]")
            else:
                hq_qty = st.number_input(
                    "num_hq",
                    min_value=0,
                    max_value=amount,
                    key=f"{id}_hq_qty",
                    label_visibility="hidden",
                )
                hq_total = hq_price * hq_qty
                st.write(f"{hq_total:,} gil ({hq_price:,} gil each)")
                st.write(f"Velocity: {nq_velocity:,}/day")
                row_cost += hq_total
        ingr_grid[(row, 6)].write(f"{row_cost:,}")
        craft_cost_total += row_cost

        # ingr_grid[(row, 6)].markdown(df.item(row,"cost"))
    
    name = result_df.item(0, "ingredient_name")
    id = result_df.item(0, "ingredient_id")
    amount = result_df.item(0, "ingredient_amount")
    shop_price = result_df.item(0, "ingredient_shop_price")
    nq_price = result_df.item(0, "nq_price")
    nq_velocity = result_df.item(0, "nq_velocity")
    hq_price = result_df.item(0, "hq_price")
    hq_velocity = result_df.item(0, "hq_velocity")

    craft_cost_each = int(craft_cost_total / amount)

    if amount > 1:
        st.write(
            f"#### Total ingredient cost per craftable amount ({amount}): :red[{craft_cost_total:,}]"
        )
    st.write(f"#### Total ingredient cost: :red[{craft_cost_each:,} gil each]")

    with cont_analysis:
        pl_perc = print_metrics(combined_df, craft_cost_total)

    with cont_pl_warning:
        print_pl_warning(pl_perc)

    return result_df, craft_cost_total



if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="FFXIV Crafting Profit/Loss Checker")

    worlds_dc_df = get_worlds_dc()
    dc_list = worlds_dc_df.select("datacentre").unique().to_series().to_list()
    dc_list.sort()

    if "dc" not in st.session_state:
        # Pass dc parameter from url if available - doesn't seem to be working on streamlit cloud
        try:
            st.session_state.dc = [item.lower() for item in dc_list].index(
                st.query_params["dc"].lower()
            )
        except:
            st.session_state.dc = 0

    world_list = worlds_dc_df.select("world").to_series().to_list()
    world_list.sort()

    def filter_world(world_list, dc):
        world_list = (
            worlds_dc_df.filter(pl.col("datacentre") == dc)
            .select("world")
            .to_series()
            .to_list()
        )
        return world_list
    
    all_recipes_df = get_all_recipes()  # List of recipes for all craftable items in game
    selectbox_recipe_list = all_recipes_df.select(["result_text", "result_id", "recipe_id"])

    col1, col2 = st.columns(2)
    with col1:
        st.title("FFXIV Crafting Profit/Loss Checker")
    st.markdown("")

    with col2:
        with st.container(horizontal_alignment="right"):
            dc_selectbox = st.selectbox(
                "Select datacentre", dc_list, index=st.session_state.dc, width=200
            )

            if dc_selectbox:
                world_list = filter_world(world_list, dc_selectbox)
                # reload page to use param url?
            world_selectbox = st.selectbox(
                "Select world (optional)", world_list, index=None, width=200
            )

    st.text(
        "Select recipe to check if better value to craft from ingredients or buy from marketboard.  \nNumber in parentheses is item id."
    )

    if "default_item_index" not in st.session_state:
        # Pass id parameter from url if available - doesn't seem to be working on streamlit cloud
        try:
            st.session_state.default_item_index = selectbox_recipe_list.select(
                pl.col("result_id").index_of(st.query_params["id"])
            )[0, 0]
        except:
            st.session_state.default_item_index = None

    item_selectbox = st.selectbox(
        "label",
        options=selectbox_recipe_list["result_text"],
        index=st.session_state.default_item_index,
        label_visibility="hidden",
    )

    if item_selectbox:
        lookup_item_id = selectbox_recipe_list.filter(
            pl.col("result_text") == item_selectbox
        ).select("result_id").item()
        recipe_id = selectbox_recipe_list.filter(
            pl.col("result_text") == item_selectbox
        ).select("recipe_id").item()
        
        st.set_page_config(layout="wide", page_title=item_selectbox)

        cont_pl_warning = st.empty()
        cont_velocity_warning = st.empty()
        cont_analysis = st.empty()
        cont_result = st.empty()
        cont_ingr = st.empty()
        cont_ingr_table = st.container()

        lookup_items_df = get_recipe_ingr(all_recipes_df, recipe_id)
        # lookup_items_df
        prices_df = price_lookup(lookup_items_df, dc_selectbox)
        # prices_df
        combined_df = join_dfs(lookup_items_df, prices_df)
        # combined_df
    
        with cont_ingr:
            result_df, craft_cost_total = print_ingredients(combined_df)
        with cont_result:
            total_velocity = print_result(result_df)
        if total_velocity is None:
            with cont_analysis:
                st.error(
                    "Error fetching price data from Universalis - item may be too new or Universalis may be down."
                )
        else:
            with cont_analysis:
                pl_perc = print_metrics(result_df, craft_cost_total)
            with cont_pl_warning:
                print_pl_warning(pl_perc)
            with cont_velocity_warning:
                print_velocity_warning(total_velocity)
