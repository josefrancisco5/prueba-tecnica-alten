MERGE INTO `project-5b0d8e1f-190f-427b-88c.SANDBOX_prueba_tecnica_alten.integration_prueba_tecnica` AS target
USING (
  SELECT
    name_common,
    TRIM(REGEXP_REPLACE(REGEXP_REPLACE(capital, r"[\[\]']", ''), r'\s*,\s*', ', ')) AS capital,
    region,
    population,
    area,
    CURRENT_DATE() AS transformation_date
  FROM `project-5b0d8e1f-190f-427b-88c.SANDBOX_prueba_tecnica_alten.countries`
) AS source
  ON  target.name_common = source.name_common
  AND target.transformation_date = source.transformation_date

WHEN MATCHED THEN
  UPDATE SET
    target.capital = source.capital,
    target.region = source.region,
    target.population = source.population,
    target.area = source.area

WHEN NOT MATCHED THEN
  INSERT (name_common, capital, region, population, area, transformation_date)
  VALUES (source.name_common, source.capital, source.region,
          source.population, source.area, source.transformation_date);