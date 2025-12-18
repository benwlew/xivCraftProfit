with dc as (
    select
        "#" as pk,
        Name,
        #5 as region
    from
        imported.worlddcgrouptype
)
select
    world."#" as pk,
    world.Name as world,
    dc.Name as datacentre,
    dc.region
    from imported.world
    left join dc on world.Region = dc.pk
where
    world.ispublic = true
    and world."#" < 999
order by pk
