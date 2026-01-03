with dc as (
    select
        "#" as dc_id,
        Name,
        #5 as region
    from
        imported.worlddcgrouptype
)
select
    world."#" as world_id,
    world.Name as world,
    dc.Name as datacentre,
    dc.region
    from imported.world
    left join dc on world.Region = dc.dc_id
where
    world.ispublic = true
    and world."#" < 999
order by world_id asc
