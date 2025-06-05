data = LOAD '/user/proyecto/input/datos_filtrados2.csv'
    USING PigStorage(',')
    AS (tipo:chararray, comuna:chararray, timestamp:chararray, descripcion:chararray, lat:chararray, lon:chararray);

data_clean = FILTER data BY tipo != 'tipo_incidente';

grouped = GROUP data_clean BY comuna;

counts = FOREACH grouped GENERATE group AS comuna, COUNT(data_clean) AS total_incidentes;

STORE counts INTO '/user/proyecto/input/incidentes_por_comuna' USING PigStorage(',');
