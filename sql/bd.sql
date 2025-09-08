
WITH
-- CTE para despesas de Serviços
SERV AS (
    SELECT DISTINCT
        crt.IDRATEIO,
        crt.LCTREF,
        tmc.IDOPERACAO,
        crt.IDPARTIDA,
        tct.IDMOV,
        tmv.CODTMV,
        tmv.CODUSUARIO,
        tmv.DATAEMISSAO,
        cln.CREDITO,
        cln.DEBITO,
        IIF(cln.CREDITO LIKE '3.1.2%', cln.CREDITO, cln.DEBITO) AS COD_CONTA,
        crt.CODGERENCIAL,
        cln.COMPLEMENTO,
        cln.[DATA],
        crt.VLRCREDITO,
        crt.VLRDEBITO,
        (crt.VLRDEBITO - crt.VLRCREDITO) AS UNIFICAVALOR
    FROM HUBDADOS.CorporeRM.CRATEIOLC AS crt
    LEFT JOIN HUBDADOS.CorporeRM.CLANCA AS cln ON crt.LCTREF = cln.LCTREF
    LEFT JOIN HUBDADOS.CorporeRM.TMOVCONT AS tmc ON cln.IDPARTIDA = tmc.IDPARTIDA
    LEFT JOIN HUBDADOS.CorporeRM.TMOVCTB AS tct ON tmc.IDOPERACAO = tct.IDOPERACAO
    LEFT JOIN HUBDADOS.CorporeRM.TMOV AS tmv ON tct.IDMOV = tmv.IDMOV
    WHERE 
        YEAR(cln.[DATA]) = YEAR(GETDATE())
        AND (cln.DEBITO NOT LIKE '2.4.1.1.01%' OR cln.DEBITO IS NULL)
        AND (cln.CREDITO LIKE '3.1.2%' OR cln.DEBITO LIKE '3.1.2%')
        AND cln.COMPLEMENTO IS NOT NULL
),

-- CTE para despesas de Pessoal
PESSOAL AS (
    SELECT DISTINCT
        crt.IDRATEIO,
        crt.LCTREF,
        tmc.IDOPERACAO,
        crt.IDPARTIDA,
        tct.IDMOV,
        tmv.CODTMV,
        tmv.CODUSUARIO,
        tmv.DATAEMISSAO,
        cln.CREDITO,
        cln.DEBITO,
        IIF(cln.CREDITO LIKE '3.1.1%', cln.CREDITO, cln.DEBITO) AS COD_CONTA,
        crt.CODGERENCIAL,
        cln.COMPLEMENTO,
        cln.[DATA],
        crt.VLRCREDITO,
        crt.VLRDEBITO,
        (crt.VLRDEBITO - crt.VLRCREDITO) AS UNIFICAVALOR
    FROM HUBDADOS.CorporeRM.CRATEIOLC AS crt
    LEFT JOIN HUBDADOS.CorporeRM.CLANCA AS cln ON crt.LCTREF = cln.LCTREF
    LEFT JOIN HUBDADOS.CorporeRM.TMOVCONT AS tmc ON cln.IDPARTIDA = tmc.IDPARTIDA
    LEFT JOIN HUBDADOS.CorporeRM.TMOVCTB AS tct ON tmc.IDOPERACAO = tct.IDOPERACAO
    LEFT JOIN HUBDADOS.CorporeRM.TMOV AS tmv ON tct.IDMOV = tmv.IDMOV
    WHERE 
        YEAR(cln.[DATA]) = YEAR(GETDATE())
        AND (cln.DEBITO NOT LIKE '2.4.1.1.01%' OR cln.DEBITO IS NULL)
        AND (cln.DEBITO LIKE '3.1.1%' OR cln.CREDITO LIKE '3.1.1%')
        AND cln.COMPLEMENTO IS NOT NULL
        AND cln.COMPLEMENTO NOT LIKE 'Custo Serviço e financeiro referente ao ano de 2018'
),

-- CTE para despesas de Crédito
CRED AS (
    SELECT DISTINCT
        crt.IDRATEIO,
        crt.LCTREF,
        tmc.IDOPERACAO,
        crt.IDPARTIDA,
        tct.IDMOV,
        tmv.CODTMV,
        tmv.CODUSUARIO,
        tmv.DATAEMISSAO,
        cln.CREDITO,
        cln.DEBITO,
        IIF(cln.DEBITO LIKE '5.1.1.2%', cln.DEBITO, cln.CREDITO) AS COD_CONTA,
        crt.CODGERENCIAL,
        cln.COMPLEMENTO,
        cln.[DATA],
        crt.VLRCREDITO,
        crt.VLRDEBITO,
        (crt.VLRDEBITO - crt.VLRCREDITO) AS UNIFICAVALOR
    FROM HUBDADOS.CorporeRM.CRATEIOLC AS crt
    LEFT JOIN HUBDADOS.CorporeRM.CLANCA AS cln ON crt.LCTREF = cln.LCTREF
    LEFT JOIN HUBDADOS.CorporeRM.TMOVCONT AS tmc ON cln.IDPARTIDA = tmc.IDPARTIDA
    LEFT JOIN HUBDADOS.CorporeRM.TMOVCTB AS tct ON tmc.IDOPERACAO = tct.IDOPERACAO
    LEFT JOIN HUBDADOS.CorporeRM.TMOV AS tmv ON tct.IDMOV = tmv.IDMOV
    WHERE 
        YEAR(cln.[DATA]) = YEAR(GETDATE())
        AND (cln.DEBITO NOT LIKE '2.4.1.1.01%' OR cln.DEBITO IS NULL)
        AND cln.COMPLEMENTO IS NOT NULL
        AND cln.DEBITO LIKE '5.2.5.3%'
),

-- CTE para Liberação de Convênios
LIBERCONV AS (
    SELECT DISTINCT
        crt.IDRATEIO,
        crt.LCTREF,
        tmc.IDOPERACAO,
        crt.IDPARTIDA,
        tct.IDMOV,
        tmv.CODTMV,
        tmv.CODUSUARIO,
        tmv.DATAEMISSAO,
        cln.CREDITO,
        cln.DEBITO,
        IIF(cln.DEBITO LIKE '5.1.1.2%' OR cln.DEBITO LIKE '1.9.5.7.01.001', cln.DEBITO, cln.CREDITO) AS COD_CONTA,
        crt.CODGERENCIAL,
        cln.COMPLEMENTO,
        cln.[DATA],
        crt.VLRCREDITO,
        crt.VLRDEBITO,
        (crt.VLRDEBITO - crt.VLRCREDITO) AS UNIFICAVALOR
    FROM HUBDADOS.CorporeRM.CRATEIOLC AS crt
    LEFT JOIN HUBDADOS.CorporeRM.CLANCA AS cln ON crt.LCTREF = cln.LCTREF
    LEFT JOIN HUBDADOS.CorporeRM.TMOVCONT AS tmc ON cln.IDPARTIDA = tmc.IDPARTIDA
    LEFT JOIN HUBDADOS.CorporeRM.TMOVCTB AS tct ON tmc.IDOPERACAO = tct.IDOPERACAO
    LEFT JOIN HUBDADOS.CorporeRM.TMOV AS tmv ON tct.IDMOV = tmv.IDMOV
    WHERE 
        YEAR(cln.[DATA]) = YEAR(GETDATE())
        AND (cln.DEBITO NOT LIKE '2.4.1.1.01%' OR cln.DEBITO IS NULL)
        AND cln.COMPLEMENTO IS NOT NULL
        AND (
            crt.CODGERENCIAL NOT LIKE '9.99999.999999.999'
            AND (cln.DEBITO LIKE '5.1.1.2%' OR cln.CREDITO LIKE '5.1.1.2%')
        )
),

-- CTE para despesas de Imobilizado
IMOB AS (
    SELECT DISTINCT
        crt.IDRATEIO,
        crt.LCTREF,
        tmc.IDOPERACAO,
        crt.IDPARTIDA,
        tct.IDMOV,
        tmv.CODTMV,
        tmv.CODUSUARIO,
        tmv.DATAEMISSAO,
        cln.CREDITO,
        cln.DEBITO,
        IIF((cln.DEBITO LIKE '5.2.2.2%' OR cln.DEBITO LIKE '5.2.3.1%' OR cln.DEBITO LIKE '1.9.5.2.03%' OR cln.DEBITO LIKE '1.9.5.2.04%' OR cln.DEBITO LIKE '1.9.5.2.03.004'), cln.DEBITO, cln.CREDITO) AS COD_CONTA,
        crt.CODGERENCIAL,
        cln.COMPLEMENTO,
        cln.[DATA],
        crt.VLRCREDITO,
        crt.VLRDEBITO,
        (crt.VLRDEBITO - crt.VLRCREDITO) AS UNIFICAVALOR
    FROM HUBDADOS.CorporeRM.CRATEIOLC AS crt
    LEFT JOIN HUBDADOS.CorporeRM.CLANCA AS cln ON crt.LCTREF = cln.LCTREF
    LEFT JOIN HUBDADOS.CorporeRM.TMOVCONT AS tmc ON cln.IDPARTIDA = tmc.IDPARTIDA
    LEFT JOIN HUBDADOS.CorporeRM.TMOVCTB AS tct ON tmc.IDOPERACAO = tct.IDOPERACAO
    LEFT JOIN HUBDADOS.CorporeRM.TMOV AS tmv ON tct.IDMOV = tmv.IDMOV
    WHERE 
        YEAR(cln.[DATA]) = YEAR(GETDATE())
        AND ((cln.DEBITO NOT LIKE '7.2.3.1.01%' AND cln.DEBITO NOT LIKE '7.2.2.2.01%') OR cln.DEBITO IS NULL)
        AND cln.COMPLEMENTO IS NOT NULL
        AND (cln.DEBITO LIKE '5.2.2.2%' OR cln.CREDITO LIKE '5.2.2.2%' OR cln.DEBITO LIKE '5.2.3.1%' OR cln.CREDITO LIKE '5.2.3.1%')
),

-- CTE para despesas de Investimentos
INVEST AS (
    SELECT DISTINCT
        crt.IDRATEIO,
        crt.LCTREF,
        tmc.IDOPERACAO,
        crt.IDPARTIDA,
        tct.IDMOV,
        tmv.CODTMV,
        tmv.CODUSUARIO,
        tmv.DATAEMISSAO,
        cln.CREDITO,
        cln.DEBITO,
        IIF(cln.DEBITO LIKE '5.2.2.1%' OR cln.DEBITO LIKE '1.9.5.2.02%', cln.DEBITO, cln.CREDITO) AS COD_CONTA,
        crt.CODGERENCIAL,
        cln.COMPLEMENTO,
        cln.[DATA],
        crt.VLRCREDITO,
        crt.VLRDEBITO,
        (crt.VLRDEBITO - crt.VLRCREDITO) AS UNIFICAVALOR
    FROM HUBDADOS.CorporeRM.CRATEIOLC AS crt
    LEFT JOIN HUBDADOS.CorporeRM.CLANCA AS cln ON crt.LCTREF = cln.LCTREF
    LEFT JOIN HUBDADOS.CorporeRM.TMOVCONT AS tmc ON cln.IDPARTIDA = tmc.IDPARTIDA
    LEFT JOIN HUBDADOS.CorporeRM.TMOVCTB AS tct ON tmc.IDOPERACAO = tct.IDOPERACAO
    LEFT JOIN HUBDADOS.CorporeRM.TMOV AS tmv ON tct.IDMOV = tmv.IDMOV
    WHERE 
        YEAR(cln.[DATA]) = YEAR(GETDATE())
        AND (cln.DEBITO NOT LIKE '2.4.1.1.01%' OR cln.DEBITO IS NULL)
        AND cln.COMPLEMENTO IS NOT NULL
        AND (cln.DEBITO LIKE '5.2.2.1%' OR cln.CREDITO LIKE '5.2.2.1%')
        AND crt.IDRATEIO NOT LIKE '1929077'
),

-- CTE para despesas de Fundo
FUNDO AS (
    SELECT DISTINCT
        crt.IDRATEIO,
        crt.LCTREF,
        tmc.IDOPERACAO,
        crt.IDPARTIDA,
        tct.IDMOV,
        tmv.CODTMV,
        tmv.CODUSUARIO,
        tmv.DATAEMISSAO,
        cln.CREDITO,
        cln.DEBITO,
        IIF(cln.DEBITO LIKE '5.2.5.2.01.001' OR cln.DEBITO LIKE '1.9.5.1.01.003', cln.DEBITO, cln.CREDITO) AS COD_CONTA,
        crt.CODGERENCIAL,
        cln.COMPLEMENTO,
        cln.[DATA],
        crt.VLRCREDITO,
        crt.VLRDEBITO,
        (crt.VLRDEBITO - crt.VLRCREDITO) AS UNIFICAVALOR
    FROM HUBDADOS.CorporeRM.CRATEIOLC AS crt
    LEFT JOIN HUBDADOS.CorporeRM.CLANCA AS cln ON crt.LCTREF = cln.LCTREF
    LEFT JOIN HUBDADOS.CorporeRM.TMOVCONT AS tmc ON cln.IDPARTIDA = tmc.IDPARTIDA
    LEFT JOIN HUBDADOS.CorporeRM.TMOVCTB AS tct ON tmc.IDOPERACAO = tct.IDOPERACAO
    LEFT JOIN HUBDADOS.CorporeRM.TMOV AS tmv ON tct.IDMOV = tmv.IDMOV
    WHERE 
        cln.COMPLEMENTO IS NOT NULL
        AND (cln.DEBITO NOT LIKE '2.4.1.1.01%' OR cln.DEBITO IS NULL)
        AND (
            (YEAR(cln.[DATA]) = YEAR(GETDATE()) AND cln.DEBITO LIKE '5.2.5.2.01.001')
            OR 
            (YEAR(cln.[DATA]) = YEAR(GETDATE()) AND cln.CREDITO IN ('5.2.5.2.01.001'))
        )
),

-- CTE para despesas de Encargos
ENCARGO AS (
    SELECT DISTINCT
        crt.IDRATEIO,
        crt.LCTREF,
        tmc.IDOPERACAO,
        crt.IDPARTIDA,
        tct.IDMOV,
        tmv.CODTMV,
        tmv.CODUSUARIO,
        tmv.DATAEMISSAO,
        cln.CREDITO,
        cln.DEBITO,
        IIF(cln.CREDITO LIKE '3.1.4%', cln.CREDITO, cln.DEBITO) AS COD_CONTA,
        crt.CODGERENCIAL,
        cln.COMPLEMENTO,
        cln.[DATA],
        crt.VLRCREDITO,
        crt.VLRDEBITO,
        (crt.VLRDEBITO - crt.VLRCREDITO) AS UNIFICAVALOR
    FROM HUBDADOS.CorporeRM.CRATEIOLC AS crt
    LEFT JOIN HUBDADOS.CorporeRM.CLANCA AS cln ON crt.LCTREF = cln.LCTREF
    LEFT JOIN HUBDADOS.CorporeRM.TMOVCONT AS tmc ON cln.IDPARTIDA = tmc.IDPARTIDA
    LEFT JOIN HUBDADOS.CorporeRM.TMOVCTB AS tct ON tmc.IDOPERACAO = tct.IDOPERACAO
    LEFT JOIN HUBDADOS.CorporeRM.TMOV AS tmv ON tct.IDMOV = tmv.IDMOV
    WHERE 
        YEAR(cln.[DATA]) = YEAR(GETDATE())
        AND (cln.DEBITO NOT LIKE '2.4.1.1.01%' OR cln.DEBITO IS NULL)
        AND (cln.DEBITO LIKE '3.1.4.1%' OR cln.CREDITO LIKE '3.1.4.1%' OR cln.DEBITO LIKE '3.1.4.2%' OR cln.CREDITO LIKE '3.1.4.2%')
        AND cln.COMPLEMENTO IS NOT NULL
        AND crt.IDRATEIO NOT IN ('1537384', '1911286')
),

-- CTE para despesas de Depósito
DEPOSITO AS (
    SELECT DISTINCT
        crt.IDRATEIO,
        crt.LCTREF,
        tmc.IDOPERACAO,
        crt.IDPARTIDA,
        tct.IDMOV,
        tmv.CODTMV,
        tmv.CODUSUARIO,
        tmv.DATAEMISSAO,
        cln.CREDITO,
        cln.DEBITO,
        IIF(cln.DEBITO LIKE '5.2.4.1.01%' OR cln.DEBITO LIKE '1.9.5.1.01.001', cln.DEBITO, cln.CREDITO) AS COD_CONTA,
        crt.CODGERENCIAL,
        cln.COMPLEMENTO,
        cln.[DATA],
        crt.VLRCREDITO,
        crt.VLRDEBITO,
        (crt.VLRDEBITO - crt.VLRCREDITO) AS UNIFICAVALOR
    FROM HUBDADOS.CorporeRM.CRATEIOLC AS crt
    LEFT JOIN HUBDADOS.CorporeRM.CLANCA AS cln ON crt.LCTREF = cln.LCTREF
    LEFT JOIN HUBDADOS.CorporeRM.TMOVCONT AS tmc ON cln.IDPARTIDA = tmc.IDPARTIDA
    LEFT JOIN HUBDADOS.CorporeRM.TMOVCTB AS tct ON tmc.IDOPERACAO = tct.IDOPERACAO
    LEFT JOIN HUBDADOS.CorporeRM.TMOV AS tmv ON tct.IDMOV = tmv.IDMOV
    WHERE 
        YEAR(cln.[DATA]) = YEAR(GETDATE())
        AND (cln.DEBITO NOT LIKE '2.4.1.1.01%' OR cln.DEBITO IS NULL)
        AND (cln.DEBITO LIKE '5.2.4.1.01%' OR cln.CREDITO LIKE '5.2.4.1.01%')
),

-- CTE para despesas de Custo
CUSTO AS (
    SELECT DISTINCT
        crt.IDRATEIO,
        crt.LCTREF,
        tmc.IDOPERACAO,
        crt.IDPARTIDA,
        tct.IDMOV,
        tmv.CODTMV,
        tmv.CODUSUARIO,
        tmv.DATAEMISSAO,
        cln.CREDITO,
        cln.DEBITO,
        IIF(cln.CREDITO LIKE '3.1.3%', cln.CREDITO, cln.DEBITO) AS COD_CONTA,
        crt.CODGERENCIAL,
        cln.COMPLEMENTO,
        cln.[DATA],
        crt.VLRCREDITO,
        crt.VLRDEBITO,
        (crt.VLRDEBITO - crt.VLRCREDITO) AS UNIFICAVALOR
    FROM HUBDADOS.CorporeRM.CRATEIOLC AS crt
    LEFT JOIN HUBDADOS.CorporeRM.CLANCA AS cln ON crt.LCTREF = cln.LCTREF
    LEFT JOIN HUBDADOS.CorporeRM.TMOVCONT AS tmc ON cln.IDPARTIDA = tmc.IDPARTIDA
    LEFT JOIN HUBDADOS.CorporeRM.TMOVCTB AS tct ON tmc.IDOPERACAO = tct.IDOPERACAO
    LEFT JOIN HUBDADOS.CorporeRM.TMOV AS tmv ON tct.IDMOV = tmv.IDMOV
    WHERE 
        YEAR(cln.[DATA]) = YEAR(GETDATE())
        AND (cln.DEBITO NOT LIKE '2.4.1.1.01%' OR cln.DEBITO IS NULL)
        AND (cln.DEBITO LIKE '3.1.3%' OR cln.CREDITO LIKE '3.1.3%')
        AND cln.COMPLEMENTO IS NOT NULL
        AND crt.IDRATEIO NOT LIKE '1537388'
),

-- CTE para buscar a estrutura hierárquica do Centro de Custo
CC AS (
    SELECT
        NivelAcao.CODCCUSTO,
        NivelUnidade.NOME AS UNIDADE,
        NivelProjeto.NOME AS PROJETO,
        NivelAcao.NOME AS ACAO
    FROM HUBDADOS.CorporeRM.GCCUSTO AS NivelAcao
    -- O JOIN para UNIDADE parece estar buscando o próprio nome, talvez a intenção fosse outra. Mantido conforme original.
    INNER JOIN HUBDADOS.CorporeRM.GCCUSTO AS NivelUnidade ON NivelAcao.CODCCUSTO = NivelUnidade.CODCCUSTO
    INNER JOIN HUBDADOS.CorporeRM.GCCUSTO AS NivelProjeto ON LEFT(NivelAcao.CODCCUSTO, 5) = NivelProjeto.CODCCUSTO
    INNER JOIN HUBDADOS.CorporeRM.GCCUSTO AS NivelAcaoDetalhe ON LEFT(NivelAcao.CODCCUSTO, 12) = NivelAcaoDetalhe.CODCCUSTO
    WHERE 
        LEN(NivelAcao.CODCCUSTO) > 15
),

-- Unifica todas as CTEs de despesas
DESPESAS AS (
    SELECT * FROM SERV
    UNION ALL
    SELECT * FROM PESSOAL
    UNION ALL
    SELECT * FROM CRED
    UNION ALL
    SELECT * FROM LIBERCONV
    UNION ALL
    SELECT * FROM IMOB
    UNION ALL
    SELECT * FROM INVEST
    UNION ALL
    SELECT * FROM FUNDO
    UNION ALL
    SELECT * FROM ENCARGO
    UNION ALL
    SELECT * FROM DEPOSITO
    UNION ALL
    SELECT * FROM CUSTO
)

-- Consulta final que combina os dados de despesas com informações de fornecedor e centro de custo
SELECT
    bd.UNIFICAVALOR,
    REPLACE(cc.UNIDADE, CHAR(22), '') AS CLASSIFICA,
    RIGHT(bd.CODGERENCIAL, 16) AS CODGERENCIAL,
    REPLACE(bd.COMPLEMENTO, CHAR(22), '') AS COMPLEMENTO,
    REPLACE(FCFO.NOME, CHAR(22), '') AS FORNECEDOR,
    REPLACE(cc.PROJETO, CHAR(22), '') AS PROJETO,
    REPLACE(cc.ACAO, CHAR(22), '') AS ACAO,
    NULL AS CONTA_FECHAMENTO,
    bd.[DATA],
    REPLACE(CCTA.DESCRICAO, CHAR(22), '') AS DESCNVL6,
    bd.COD_CONTA COLLATE Latin1_General_CI_AS AS COD_CONTA,
    FCFO.CODCFO
FROM DESPESAS AS bd
LEFT JOIN HUBDADOS.CorporeRM.TMOV AS tmv ON bd.IDMOV = tmv.IDMOV
LEFT JOIN CC AS cc ON cc.CODCCUSTO = RIGHT(bd.CODGERENCIAL, 16)
LEFT JOIN HUBDADOS.CorporeRM.CCONTA AS CCTA ON CCTA.CODCONTA COLLATE Latin1_General_CI_AS = bd.COD_CONTA
LEFT JOIN HUBDADOS.CorporeRM.FCFO AS FCFO ON FCFO.CODCFO = tmv.CODCFO
LEFT JOIN HUBDADOS.CorporeRM.TTMV AS TTMV ON TTMV.CODTMV = tmv.CODTMV;

