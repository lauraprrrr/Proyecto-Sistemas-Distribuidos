data = LOAD '/user/proyecto/input/datos_filtrados2.csv'
    USING PigStorage(',')
    AS (tipo:chararray, comuna:chararray, timestamp:chararray, descripcion:chararray, lat:chararray, lon:chararray);

data_clean = FILTER data BY tipo != 'tipo_incidente';

grouped = GROUP data_clean BY tipo;

counts = FOREACH grouped GENERATE group AS tipo_incidente, COUNT(data_clean) AS frecuencia;

STORE counts INTO '/user/proyecto/input/frecuencia_tipos' USING PigStorage(',');
