-- Busca todos os dados de despesas realizadas (brutos, linha a linha) para um ano.
-- Parâmetro: :ano
SELECT *
FROM vw_AnaliseDespesas
WHERE YEAR(DATA) = ?;
