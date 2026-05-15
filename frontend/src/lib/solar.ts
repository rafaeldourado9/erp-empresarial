/**
 * Funções puras de dimensionamento solar.
 * Fórmulas conforme manual interno Nacional Energy.
 */

export interface DimensionamentoInput {
  consumo_kwh_mes: number
  potencia_placa_w: number
  fator_regional?: number // default 126 (média Brasil)
}

export interface DimensionamentoResult {
  geracao_por_placa_kwh: number
  qtd_placas: number
  kwp_sistema: number
  consumo_kwh_mes: number
  potencia_placa_w: number
  fator_regional: number
}

export interface RecalculoResult {
  nova_potencia_w: number
  qtd_placas: number
  kwp_sistema: number
}

export interface OverloadResult {
  overload_maximo_kwp: number
  kwp_sistema: number
  status: 'ok' | 'overload'
  mensagem: string
}

/**
 * Calcula o dimensionamento solar básico.
 *
 * Fórmulas:
 *   Geração mensal por placa = potência_placa_kW × 126
 *   Quantidade de placas     = ceil(consumo_kWh_mês / geração_por_placa)
 *   kWp do sistema           = qtd_placas × potência_placa_kW
 */
export function calcularDimensionamento(input: DimensionamentoInput): DimensionamentoResult {
  const fator = input.fator_regional ?? 126
  const potencia_kw = input.potencia_placa_w / 1000
  const geracao_por_placa = potencia_kw * fator
  const qtd_placas = Math.ceil(input.consumo_kwh_mes / geracao_por_placa)
  const kwp_sistema = qtd_placas * potencia_kw

  return {
    geracao_por_placa_kwh: Math.round(geracao_por_placa * 100) / 100,
    qtd_placas,
    kwp_sistema: Math.round(kwp_sistema * 100) / 100,
    consumo_kwh_mes: input.consumo_kwh_mes,
    potencia_placa_w: input.potencia_placa_w,
    fator_regional: fator,
  }
}

/**
 * Recalcula para outra potência de placa mantendo o mesmo kWp.
 *
 * Fórmula: qtd = ceil(kWp_sistema / nova_potência_kW)
 */
export function recalcularOutraPlaca(kwp_sistema: number, nova_potencia_w: number): RecalculoResult {
  const nova_potencia_kw = nova_potencia_w / 1000
  const qtd_placas = Math.ceil(kwp_sistema / nova_potencia_kw)
  return {
    nova_potencia_w,
    qtd_placas,
    kwp_sistema: Math.round(qtd_placas * nova_potencia_kw * 100) / 100,
  }
}

/**
 * Verifica overload do inversor.
 *
 * Fórmula: overload_máximo = potência_inversor_kW × fator_overload
 * Status: kWp_sistema ≤ overload_máximo → ok | vermelho
 */
export function verificarOverload(
  potencia_inversor_kw: number,
  fator_overload: number,
  kwp_sistema: number,
): OverloadResult {
  const overload_maximo = potencia_inversor_kw * fator_overload
  const status = kwp_sistema <= overload_maximo ? 'ok' : 'overload'
  const mensagem = status === 'ok'
    ? `Sistema de ${kwp_sistema.toFixed(2)} kWp dentro do limite de ${overload_maximo.toFixed(2)} kWp`
    : `Sistema de ${kwp_sistema.toFixed(2)} kWp EXCEDE o limite de ${overload_maximo.toFixed(2)} kWp do inversor`

  return {
    overload_maximo_kwp: Math.round(overload_maximo * 100) / 100,
    kwp_sistema,
    status,
    mensagem,
  }
}
