data = LOAD '/user/proyecto/input/datos_filtrados2.csv'
    USING PigStorage(',')
    AS (tipo:chararray, comuna:chararray, timestamp:chararray, descripcion:chararray, lat:chararray, lon:chararray);

data_clean = FILTER data BY tipo != 'tipo_incidente';

dates = FOREACH data_clean GENERATE SUBSTRING(timestamp, 0, 10) AS fecha;

grouped = GROUP dates BY fecha;

counts = FOREACH grouped GENERATE group AS fecha, COUNT(dates) AS total_incidentes;

STORE counts INTO '/user/proyecto/input/tendencias_temporales' USING PigStorage(',');
