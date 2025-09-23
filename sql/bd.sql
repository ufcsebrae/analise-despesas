-- sql/bd.sql
WITH 
-- 1. CTE unificada para buscar todos os lançamentos relevantes de uma só vez.
BaseLancamentos AS (
    SELECT
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
        cln.COMPLEMENTO,
        cln.[DATA],
        crt.VLRCREDITO,
        crt.VLRDEBITO,
        (crt.VLRDEBITO - crt.VLRCREDITO) AS UNIFICAVALOR,
        crt.CODGERENCIAL,
        tmv.CODCFO,
        
        -- 2. Classifica a despesa e determina a conta contábil usando CASE.
        --    Isso substitui a necessidade de múltiplas CTEs e IIF.
        CASE
            WHEN (cln.DEBITO LIKE '3.1.1%' OR cln.CREDITO LIKE '3.1.1%')                               THEN 'Pessoal'
            WHEN (cln.CREDITO LIKE '3.1.2%' OR cln.DEBITO LIKE '3.1.2%')                               THEN 'Serviços'
            WHEN (cln.DEBITO LIKE '3.1.3%' OR cln.CREDITO LIKE '3.1.3%')                               THEN 'Custo'
            WHEN (cln.DEBITO LIKE '3.1.4.1%' OR cln.CREDITO LIKE '3.1.4.1%' OR 
                  cln.DEBITO LIKE '3.1.4.2%' OR cln.CREDITO LIKE '3.1.4.2%')                           THEN 'Encargos'
            WHEN (cln.DEBITO LIKE '5.1.1.2%' OR cln.CREDITO LIKE '5.1.1.2%')                           THEN 'Liberação de Convênios'
            WHEN (cln.DEBITO LIKE '5.2.2.1%' OR cln.CREDITO LIKE '5.2.2.1%')                           THEN 'Investimentos'
            WHEN (cln.DEBITO LIKE '5.2.2.2%' OR cln.CREDITO LIKE '5.2.2.2%' OR
                  cln.DEBITO LIKE '5.2.3.1%' OR cln.CREDITO LIKE '5.2.3.1%')                           THEN 'Imobilizado'
            WHEN (cln.DEBITO LIKE '5.2.4.1.01%' OR cln.CREDITO LIKE '5.2.4.1.01%')                     THEN 'Depósito'
            WHEN (cln.DEBITO LIKE '5.2.5.2.01.001' OR cln.CREDITO LIKE '5.2.5.2.01.001')               THEN 'Fundo'
            WHEN (cln.DEBITO LIKE '5.2.5.3%')                                                         THEN 'Crédito'
            WHEN (cln.DEBITO LIKE '1.9.5.%') -- Captura outras contas de débito específicas
                 THEN CASE 
                        WHEN cln.DEBITO LIKE '1.9.5.1.01.001' THEN 'Depósito'
                        WHEN cln.DEBITO LIKE '1.9.5.1.01.003' THEN 'Fundo'
                        WHEN cln.DEBITO LIKE '1.9.5.2.02%' THEN 'Investimentos'
                        WHEN cln.DEBITO LIKE '1.9.5.2.03%' OR cln.DEBITO LIKE '1.9.5.2.04%' THEN 'Imobilizado'
                        WHEN cln.DEBITO LIKE '1.9.5.7.01.001' THEN 'Liberação de Convênios'
                      END
            ELSE NULL
        END AS TIPO_DESPESA,

        COALESCE(cln.DEBITO, cln.CREDITO) AS COD_CONTA -- Simplificação; a lógica IIF era redundante
        
    FROM HUBDADOS.CorporeRM.CRATEIOLC AS crt
    LEFT JOIN HUBDADOS.CorporeRM.CLANCA AS cln ON crt.LCTREF = cln.LCTREF
    LEFT JOIN HUBDADOS.CorporeRM.TMOVCONT AS tmc ON cln.IDPARTIDA = tmc.IDPARTIDA
    LEFT JOIN HUBDADOS.CorporeRM.TMOVCTB AS tct ON tmc.IDOPERACAO = tct.IDOPERACAO
    LEFT JOIN HUBDADOS.CorporeRM.TMOV AS tmv ON tct.IDMOV = tmv.IDMOV
    
    -- 3. Filtros genéricos aplicados a todos os lançamentos
    WHERE 
        YEAR(cln.[DATA]) = :ano -- Usando parâmetro para o ano
        AND cln.COMPLEMENTO IS NOT NULL
        AND (cln.DEBITO NOT LIKE '2.4.1.1.01%' OR cln.DEBITO IS NULL)
),

-- CTE para Centro de Custo permanece a mesma, mas com um JOIN mais limpo.
CC AS (
   SELECT
        NivelAcao.CODCCUSTO,
        NivelUnidade.CAMPOLIVRE AS ACAO,
        NivelProjeto.CAMPOLIVRE AS PROJETO,
        NivelAcao.CAMPOLIVRE AS UNIDADE
    FROM HUBDADOS.CorporeRM.GCCUSTO AS NivelAcao
    -- Corrigindo a lógica para buscar os níveis hierárquicos corretos
    LEFT JOIN HUBDADOS.CorporeRM.GCCUSTO AS NivelProjeto ON LEFT(NivelAcao.CODCCUSTO, 5) = NivelProjeto.CODCCUSTO
    LEFT JOIN HUBDADOS.CorporeRM.GCCUSTO AS NivelUnidade ON LEFT(NivelAcao.CODCCUSTO, 12) = NivelUnidade.CODCCUSTO
    WHERE 
        LEN(NivelAcao.CODCCUSTO) > 15 -- Filtra para o nível mais detalhado
)

-- 4. Consulta Final
SELECT
    bl.UNIFICAVALOR,
    bl.TIPO_DESPESA,
    REPLACE(cc.UNIDADE, CHAR(22), '') AS CLASSIFICA,
    RIGHT(bl.CODGERENCIAL, 16) AS CODGERENCIAL,
    REPLACE(bl.COMPLEMENTO, CHAR(22), '') AS COMPLEMENTO,
    REPLACE(cc.PROJETO, CHAR(22), '') AS PROJETO,
    REPLACE(cc.ACAO, CHAR(22), '') AS ACAO,
    bl.[DATA],
    REPLACE(CCTA.DESCRICAO, CHAR(22), '') AS DESCNVL6,
    bl.COD_CONTA COLLATE Latin1_General_CI_AS AS COD_CONTA,
    bl.CODCFO,
    REPLACE(FCFO.NOME, CHAR(22), '') AS FORNECEDOR
FROM BaseLancamentos AS bl
LEFT JOIN CC ON CC.CODCCUSTO = RIGHT(bl.CODGERENCIAL, 16)
LEFT JOIN HUBDADOS.CorporeRM.CCONTA AS CCTA ON CCTA.CODCONTA COLLATE Latin1_General_CI_AS = bl.COD_CONTA
LEFT JOIN HUBDADOS.CorporeRM.FCFO AS FCFO ON FCFO.CODCFO = bl.CODCFO
LEFT JOIN HUBDADOS.CorporeRM.TTMV AS TTMV ON TTMV.CODTMV = bl.CODTMV

-- 5. Aplica as exclusões específicas de cada tipo de despesa no final
WHERE 
    bl.TIPO_DESPESA IS NOT NULL
    AND NOT (bl.TIPO_DESPESA = 'Pessoal' AND bl.COMPLEMENTO LIKE 'Custo Serviço e financeiro referente ao ano de 2018')
    AND NOT (bl.TIPO_DESPESA = 'Liberação de Convênios' AND bl.CODGERENCIAL LIKE '9.99999.999999.999')
    AND NOT ((bl.TIPO_DESPESA = 'Imobilizado') AND (bl.DEBITO LIKE '7.2.3.1.01%' OR bl.DEBITO LIKE '7.2.2.2.01%'))
    AND NOT (bl.TIPO_DESPESA = 'Investimentos' AND bl.IDRATEIO = '1929077')
    AND NOT (bl.TIPO_DESPESA = 'Encargos' AND bl.IDRATEIO IN ('1537384', '1911286'))
    AND NOT (bl.TIPO_DESPESA = 'Custo' AND bl.IDRATEIO = '1537388')
    AND cc.UNIDADE = :unidade_gestora;
