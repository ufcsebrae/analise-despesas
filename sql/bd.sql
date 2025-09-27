-- sql/bd.sql
-- VERSÃO FINAL: Tradução do script T-SQL para um único SELECT com CTEs

-- CTE 1: Substitui a tabela de variável @CONTAS
WITH CONTAS_DE_INTERESSE AS (
    SELECT CONTA FROM (VALUES
        ('3.1.1.1.01.001'), ('3.1.1.1.01.002'), ('3.1.1.1.01.004'), ('3.1.1.1.01.005'), ('3.1.1.1.01.008'),
        ('3.1.1.1.02.001'), ('3.1.1.1.03.001'), ('3.1.1.1.04.001'), ('3.1.1.1.04.999'), ('3.1.1.2.01.004'),
        ('3.1.1.2.01.005'), ('3.1.1.2.01.006'), ('3.1.1.3.01.001'), ('3.1.1.3.01.002'), ('3.1.1.3.01.003'),
        ('3.1.1.3.01.004'), ('3.1.1.3.01.005'), ('3.1.1.3.01.008'), ('3.1.1.3.01.999'), ('3.1.2.1.01.001'),
        ('3.1.2.1.01.002'), ('3.1.2.1.02.001'), ('3.1.2.1.02.002'), ('3.1.2.1.02.003'), ('3.1.2.1.02.004'),
        ('3.1.2.1.02.005'), ('3.1.2.1.02.006'), ('3.1.2.1.02.007'), ('3.1.2.1.02.008'), ('3.1.2.1.02.009'),
        ('3.1.2.1.02.010'), ('3.1.2.1.02.013'), ('3.1.2.1.02.014'), ('3.1.2.1.02.019'), ('3.1.2.1.02.022'),
        ('3.1.2.1.02.999'), ('3.1.2.1.03.001'), ('3.1.2.2.01.001'), ('3.1.2.2.01.002'), ('3.1.2.2.01.003'),
        ('3.1.2.2.01.004'), ('3.1.2.2.01.005'), ('3.1.2.2.01.006'), ('3.1.2.2.01.008'), ('3.1.2.2.01.999'),
        ('3.1.2.2.02.001'), ('3.1.2.2.02.002'), ('3.1.2.2.02.004'), ('3.1.2.2.02.007'), ('3.1.2.2.02.999'),
        ('3.1.2.3.01.001'), ('3.1.3.1.01.001'), ('3.1.3.1.01.002'), ('3.1.3.1.01.003'), ('3.1.3.1.01.004'),
        ('3.1.3.1.01.005'), ('3.1.3.1.01.006'), ('3.1.3.1.01.999'), ('3.1.3.1.02.001'), ('3.1.3.1.02.002'),
        ('3.1.3.1.02.003'), ('3.1.3.1.02.004'), ('3.1.3.1.02.005'), ('3.1.3.1.02.006'), ('3.1.3.1.02.009'),
        ('3.1.3.1.02.010'), ('3.1.3.1.02.999'), ('3.1.3.2.01.001'), ('3.1.3.2.01.002'), ('3.1.3.2.01.003'),
        ('3.1.3.2.01.004'), ('3.1.3.2.01.999'), ('3.1.3.2.02.004'), ('3.1.3.3.01.001'), ('3.1.3.3.01.002'),
        ('3.1.3.3.01.003'), ('3.1.3.3.01.005'), ('3.1.3.3.01.007'), ('3.1.3.3.01.008'), ('3.1.3.3.01.999'),
        ('3.1.3.4.01.002'), ('3.1.3.4.01.003'), ('3.1.3.4.01.005'), ('3.1.3.4.01.999'), ('3.1.3.5.01.001'),
        ('3.1.3.5.01.002'), ('3.1.3.5.01.003'), ('3.1.3.5.01.004'), ('3.1.3.5.01.005'), ('3.1.3.6.01.001'),
        ('3.1.3.6.01.002'), ('3.1.3.6.01.003'), ('3.1.3.6.01.004'), ('3.1.3.6.01.005'), ('3.1.3.6.01.006'),
        ('3.1.3.6.01.999'), ('3.1.3.7.01.001'), ('3.1.3.7.01.004'), ('3.1.3.7.01.005'), ('3.1.3.7.01.006'),
        ('3.1.3.7.01.007'), ('3.1.3.7.01.008'), ('3.1.3.7.01.009'), ('3.1.3.7.01.010'), ('3.1.3.7.01.011'),
        ('3.1.3.7.01.015'), ('3.1.3.7.01.021'), ('3.1.3.7.01.023'), ('3.1.3.7.01.999'), ('3.1.3.8.01.001'),
        ('3.1.4.1.01.002'), ('3.1.4.1.01.003'), ('3.1.4.1.02.001'), ('3.1.4.2.01.001'), ('3.1.4.2.01.002'),
        ('3.1.4.2.01.004'), ('3.1.4.2.01.005'), ('3.1.4.2.01.006'), ('3.1.4.2.01.007'), ('3.1.4.2.01.999'),
        ('5.1.1.2.01.001'), ('5.2.2.2.01.001'), ('5.2.2.2.01.003'), ('5.2.2.2.01.004'), ('5.2.2.2.01.006'),
        ('5.2.4.1.01.001'), ('5.2.5.2.01.001')
    ) AS Contas(CONTA)
),
-- CTE 2: Substitui a tabela temporária #CCUSTO
CENTROS_DE_CUSTO AS (
    SELECT
        NivelAcao.CODCCUSTO COLLATE Latin1_General_CI_AS AS CC,
        NivelUnidade.CAMPOLIVRE AS UNIDADE,
        NivelProjeto.CAMPOLIVRE AS PROJETO,
        NivelAcao.CAMPOLIVRE AS ACAO
    FROM CorporeRM.GCCUSTO AS NivelAcao
    LEFT JOIN CorporeRM.GCCUSTO AS NivelProjeto ON LEFT(NivelAcao.CODCCUSTO, 5) = NivelProjeto.CODCCUSTO
    LEFT JOIN CorporeRM.GCCUSTO AS NivelUnidade ON LEFT(NivelAcao.CODCCUSTO, 12) = NivelUnidade.CODCCUSTO
    WHERE 
        LEN(NivelAcao.CODCCUSTO) = 16 AND NivelAcao.ATIVO = 'T' AND NivelAcao.PERMITELANC = 'T'
),
-- CTE 3: Substitui a tabela temporária #ORCAMENTO, unificando os lançamentos
ORCAMENTO_UNIFICADO AS (
    SELECT
        RIGHT(crt.CODGERENCIAL, 16) COLLATE Latin1_General_CI_AS AS CC, 
        cln.DEBITO COLLATE Latin1_General_CI_AS AS CONTA,
        CASE WHEN pc.Natureza = 1 THEN cln.VALOR ELSE -1 * cln.VALOR END AS VALOR,
        crt.IDRATEIO, crt.LCTREF, crt.IDPARTIDA, tmv.IDMOV, tmv.CODTMV, tmv.CAMPOLIVRE1 as CONTRATO,
        tmv.CODUSUARIO, tmv.DATAEMISSAO, cln.COMPLEMENTO, cln.[DATA], tmv.CODCFO
    FROM HUBDADOS.CorporeRM.CRATEIOLC crt
    INNER JOIN HUBDADOS.CorporeRM.CLANCA cln ON crt.LCTREF = cln.LCTREF
    INNER JOIN HUBDADOS.CorporeRM.TMOV tmv ON cln.INTEGRACHAVE = CAST(tmv.IDMOV AS VARCHAR(255))
    INNER JOIN CorporeRM.CCONTA pc ON pc.CODCONTA = cln.DEBITO
    WHERE cln.[DATA] >= :data_inicio AND cln.[DATA] < DATEADD(day, 1, CAST(:data_fim AS DATE))

    UNION ALL

    SELECT
        RIGHT(crt.CODGERENCIAL, 16) COLLATE Latin1_General_CI_AS AS CC, 
        cln.CREDITO COLLATE Latin1_General_CI_AS AS CONTA,
        CASE WHEN pc.Natureza = 0 THEN cln.VALOR ELSE -1 * cln.VALOR END AS VALOR,
        crt.IDRATEIO, crt.LCTREF, crt.IDPARTIDA, tmv.IDMOV, tmv.CODTMV, tmv.CAMPOLIVRE1 as CONTRATO,
        tmv.CODUSUARIO, tmv.DATAEMISSAO, cln.COMPLEMENTO, cln.[DATA], tmv.CODCFO
    FROM HUBDADOS.CorporeRM.CRATEIOLC crt
    INNER JOIN HUBDADOS.CorporeRM.CLANCA cln ON crt.LCTREF = cln.LCTREF
    INNER JOIN HUBDADOS.CorporeRM.TMOV tmv ON cln.INTEGRACHAVE = CAST(tmv.IDMOV AS VARCHAR(255))
    INNER JOIN CorporeRM.CCONTA pc ON pc.CODCONTA = cln.CREDITO
    WHERE cln.[DATA] >= :data_inicio AND cln.[DATA] < DATEADD(day, 1, CAST(:data_fim AS DATE))
)
-- CONSULTA FINAL: Junta as CTEs para gerar o resultado
SELECT
    orc.VALOR AS UNIFICAVALOR,
    orc.COMPLEMENTO,
    orc.[DATA],
    orc.CONTA AS COD_CONTA,
    REPLACE(fcf.NOME, CHAR(22), '') AS FORNECEDOR,
    cc.UNIDADE AS CLASSIFICA,
    cc.PROJETO,
    cc.ACAO
FROM ORCAMENTO_UNIFICADO AS orc
INNER JOIN CONTAS_DE_INTERESSE AS f ON orc.CONTA = f.CONTA
LEFT JOIN CENTROS_DE_CUSTO AS cc ON orc.CC = cc.CC
LEFT JOIN HUBDADOS.CorporeRM.FCFO AS fcf ON orc.CODCFO = fcf.CODCFO
WHERE 
    cc.UNIDADE = :unidade_gestora;

