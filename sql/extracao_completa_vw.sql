-- sql/extracao_completa_vw.sql
SELECT * 
FROM vw_AnaliseDespesas 
WHERE YEAR([DATA]) = :ano
