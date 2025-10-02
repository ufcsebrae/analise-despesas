-- Busca o orçamento anualizado de um período específico.
-- Parâmetro: :id_periodo
SELECT
    B.CODCCUSTO,
    SUM(A.VALORORCADO) AS VALOR_ORCADO
FROM
    CorporeRM.TMOVORCAMENTO AS A
INNER JOIN
    CorporeRM.TORCAMENTO AS B ON A.IDORCAMENTO = B.IDORCAMENTO
WHERE
    B.IDPERIODO = ?
GROUP BY
    B.CODCCUSTO;
