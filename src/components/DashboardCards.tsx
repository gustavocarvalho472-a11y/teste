/**
 * CARDS PRINCIPAIS DO DASHBOARD
 *
 * 4 cards que mostram as métricas consolidadas:
 * 1. Municípios Identificados
 * 2. Orçamento Disponível
 * 3. Gap vs Média Histórica
 * 4. Execução Média
 */

import React from 'react';
import {
  MetricaMunicipios,
  MetricaOrcamentoDisponivel,
  MetricaGapHistorico,
  MetricaExecucaoMedia
} from '../types/budget-analysis';
import {
  formatarMoeda,
  formatarPercentual,
  formatarNumero,
  formatarPontosPercentuais
} from '../utils/formatters';

// ============================================================================
// CARD 1: MUNICÍPIOS IDENTIFICADOS
// ============================================================================

interface MunicipiosCardProps {
  data: MetricaMunicipios;
}

export const MunicipiosCard: React.FC<MunicipiosCardProps> = ({ data }) => {
  return (
    <div
      style={{
        backgroundColor: '#ffffff',
        borderRadius: '16px',
        padding: '24px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
        border: '2px solid #7c3aed',
        transition: 'all 0.3s ease',
        cursor: 'pointer'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-4px)';
        e.currentTarget.style.boxShadow = '0 8px 24px rgba(124, 58, 237, 0.2)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.08)';
      }}
    >
      {/* Ícone e Título */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
        <div
          style={{
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '24px'
          }}
        >
          🎯
        </div>
        <div>
          <div
            style={{
              fontSize: '14px',
              fontWeight: '600',
              color: '#7c3aed',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}
          >
            Municípios Identificados
          </div>
        </div>
      </div>

      {/* Valor Principal */}
      <div style={{ marginBottom: '12px' }}>
        <div
          style={{
            fontSize: '48px',
            fontWeight: '700',
            color: '#7c3aed',
            lineHeight: '1',
            marginBottom: '8px'
          }}
        >
          {formatarNumero(data.total_identificados)}
        </div>
        <div style={{ fontSize: '14px', color: '#6b7280' }}>
          de {formatarNumero(data.total_analisados)} municípios ({formatarPercentual(data.percentual, 1)}
          )
        </div>
      </div>

      {/* Breakdown */}
      <div
        style={{
          marginTop: '16px',
          paddingTop: '16px',
          borderTop: '1px solid #e5e7eb',
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '12px',
          fontSize: '12px'
        }}
      >
        {/* Top 2 Regiões */}
        <div>
          <div style={{ fontWeight: '600', color: '#374151', marginBottom: '4px' }}>
            Por Região:
          </div>
          {data.por_regiao
            .sort((a, b) => b.quantidade - a.quantidade)
            .slice(0, 2)
            .map((r) => (
              <div key={r.regiao} style={{ color: '#6b7280' }}>
                {r.regiao}: {r.quantidade}
              </div>
            ))}
        </div>

        {/* Top 2 Categorias */}
        <div>
          <div style={{ fontWeight: '600', color: '#374151', marginBottom: '4px' }}>
            Por Categoria:
          </div>
          {data.por_categoria
            .sort((a, b) => b.quantidade - a.quantidade)
            .slice(0, 2)
            .map((c) => (
              <div key={c.categoria} style={{ color: '#6b7280' }}>
                {c.categoria}: {c.quantidade}
              </div>
            ))}
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// CARD 2: ORÇAMENTO DISPONÍVEL
// ============================================================================

interface OrcamentoDisponivelCardProps {
  data: MetricaOrcamentoDisponivel;
}

export const OrcamentoDisponivelCard: React.FC<OrcamentoDisponivelCardProps> = ({ data }) => {
  return (
    <div
      style={{
        backgroundColor: '#ffffff',
        borderRadius: '16px',
        padding: '24px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
        border: '2px solid #10b981',
        transition: 'all 0.3s ease',
        cursor: 'pointer'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-4px)';
        e.currentTarget.style.boxShadow = '0 8px 24px rgba(16, 185, 129, 0.2)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.08)';
      }}
    >
      {/* Ícone e Título */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
        <div
          style={{
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '24px'
          }}
        >
          💰
        </div>
        <div>
          <div
            style={{
              fontSize: '14px',
              fontWeight: '600',
              color: '#10b981',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}
          >
            Orçamento Disponível
          </div>
        </div>
      </div>

      {/* Valor Principal */}
      <div style={{ marginBottom: '12px' }}>
        <div
          style={{
            fontSize: '48px',
            fontWeight: '700',
            color: '#10b981',
            lineHeight: '1',
            marginBottom: '8px'
          }}
        >
          {data.total_disponivel_formatado}
        </div>
        <div style={{ fontSize: '14px', color: '#6b7280' }}>não executados até agosto</div>
      </div>

      {/* Estatísticas */}
      <div
        style={{
          marginTop: '16px',
          paddingTop: '16px',
          borderTop: '1px solid #e5e7eb',
          fontSize: '12px'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
          <span style={{ color: '#6b7280' }}>Média por município:</span>
          <span style={{ fontWeight: '600', color: '#374151' }}>
            {formatarMoeda(data.media_por_municipio, 1)}
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
          <span style={{ color: '#6b7280' }}>Mediana:</span>
          <span style={{ fontWeight: '600', color: '#374151' }}>
            {formatarMoeda(data.mediana, 1)}
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ color: '#6b7280' }}>Maior saldo:</span>
          <span style={{ fontWeight: '600', color: '#10b981' }}>
            {formatarMoeda(data.maior_saldo.valor, 1)}
          </span>
        </div>
        <div style={{ fontSize: '11px', color: '#9ca3af', marginTop: '4px' }}>
          {data.maior_saldo.municipio}
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// CARD 3: GAP VS MÉDIA HISTÓRICA
// ============================================================================

interface GapHistoricoCardProps {
  data: MetricaGapHistorico;
}

export const GapHistoricoCard: React.FC<GapHistoricoCardProps> = ({ data }) => {
  return (
    <div
      style={{
        backgroundColor: '#ffffff',
        borderRadius: '16px',
        padding: '24px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
        border: '2px solid #f97316',
        transition: 'all 0.3s ease',
        cursor: 'pointer'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-4px)';
        e.currentTarget.style.boxShadow = '0 8px 24px rgba(249, 115, 22, 0.2)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.08)';
      }}
    >
      {/* Ícone e Título */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
        <div
          style={{
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, #f97316 0%, #ea580c 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '24px'
          }}
        >
          📉
        </div>
        <div>
          <div
            style={{
              fontSize: '14px',
              fontWeight: '600',
              color: '#f97316',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}
          >
            Gap vs Média Histórica
          </div>
        </div>
      </div>

      {/* Valor Principal */}
      <div style={{ marginBottom: '12px' }}>
        <div
          style={{
            fontSize: '48px',
            fontWeight: '700',
            color: '#f97316',
            lineHeight: '1',
            marginBottom: '8px'
          }}
        >
          {data.gap_total_formatado}
        </div>
        <div style={{ fontSize: '14px', color: '#6b7280' }}>ABAIXO da média histórica</div>
      </div>

      {/* Distribuição */}
      <div
        style={{
          marginTop: '16px',
          paddingTop: '16px',
          borderTop: '1px solid #e5e7eb',
          fontSize: '12px'
        }}
      >
        <div style={{ fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
          Distribuição do Desvio:
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
          <span style={{ color: '#6b7280' }}>-10 a -20pp:</span>
          <span style={{ fontWeight: '600', color: '#fbbf24' }}>
            {data.municipios_10_20pp} municípios
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
          <span style={{ color: '#6b7280' }}>-20 a -30pp:</span>
          <span style={{ fontWeight: '600', color: '#f97316' }}>
            {data.municipios_20_30pp} municípios
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ color: '#6b7280' }}>Abaixo de -30pp:</span>
          <span style={{ fontWeight: '600', color: '#dc2626' }}>
            {data.municipios_acima_30pp} municípios
          </span>
        </div>
        <div
          style={{
            marginTop: '12px',
            paddingTop: '8px',
            borderTop: '1px solid #f3f4f6',
            fontSize: '11px',
            color: '#9ca3af'
          }}
        >
          Desvio médio: {formatarPontosPercentuais(data.percentual_medio_desvio)}
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// CARD 4: EXECUÇÃO MÉDIA
// ============================================================================

interface ExecucaoMediaCardProps {
  data: MetricaExecucaoMedia;
}

export const ExecucaoMediaCard: React.FC<ExecucaoMediaCardProps> = ({ data }) => {
  const estaAbaixoBenchmark = data.execucao_media_atual < data.benchmark_agosto;

  return (
    <div
      style={{
        backgroundColor: '#ffffff',
        borderRadius: '16px',
        padding: '24px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
        border: `2px solid ${estaAbaixoBenchmark ? '#ef4444' : '#3b82f6'}`,
        transition: 'all 0.3s ease',
        cursor: 'pointer'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-4px)';
        e.currentTarget.style.boxShadow = `0 8px 24px ${estaAbaixoBenchmark ? 'rgba(239, 68, 68, 0.2)' : 'rgba(59, 130, 246, 0.2)'}`;
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.08)';
      }}
    >
      {/* Ícone e Título */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
        <div
          style={{
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            background: estaAbaixoBenchmark
              ? 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
              : 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '24px'
          }}
        >
          📊
        </div>
        <div>
          <div
            style={{
              fontSize: '14px',
              fontWeight: '600',
              color: estaAbaixoBenchmark ? '#ef4444' : '#3b82f6',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}
          >
            Execução Média
          </div>
        </div>
      </div>

      {/* Valor Principal */}
      <div style={{ marginBottom: '12px' }}>
        <div
          style={{
            fontSize: '48px',
            fontWeight: '700',
            color: estaAbaixoBenchmark ? '#ef4444' : '#3b82f6',
            lineHeight: '1',
            marginBottom: '8px'
          }}
        >
          {formatarPercentual(data.execucao_media_atual, 1)}
        </div>
        <div style={{ fontSize: '14px', color: '#6b7280' }}>
          vs {formatarPercentual(data.benchmark_agosto, 0)} esperado em agosto
        </div>
      </div>

      {/* Comparação com Benchmark */}
      <div
        style={{
          marginTop: '12px',
          padding: '12px',
          borderRadius: '8px',
          backgroundColor: estaAbaixoBenchmark ? '#fef2f2' : '#eff6ff',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}
      >
        <span style={{ fontSize: '24px' }}>{estaAbaixoBenchmark ? '⚠️' : '✅'}</span>
        <div style={{ flex: 1 }}>
          <div
            style={{
              fontSize: '16px',
              fontWeight: '700',
              color: estaAbaixoBenchmark ? '#dc2626' : '#2563eb'
            }}
          >
            {formatarPontosPercentuais(data.diferenca_vs_benchmark)}
          </div>
          <div style={{ fontSize: '11px', color: '#6b7280' }}>
            {estaAbaixoBenchmark ? 'Abaixo do esperado' : 'Acima do esperado'}
          </div>
        </div>
      </div>

      {/* Range */}
      <div
        style={{
          marginTop: '16px',
          paddingTop: '16px',
          borderTop: '1px solid #e5e7eb',
          fontSize: '12px'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
          <span style={{ color: '#6b7280' }}>Menor execução:</span>
          <span style={{ fontWeight: '600', color: '#dc2626' }}>
            {formatarPercentual(data.menor_execucao.percentual, 1)}
          </span>
        </div>
        <div style={{ fontSize: '11px', color: '#9ca3af', marginBottom: '8px', textAlign: 'right' }}>
          {data.menor_execucao.municipio}
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
          <span style={{ color: '#6b7280' }}>Maior execução:</span>
          <span style={{ fontWeight: '600', color: '#10b981' }}>
            {formatarPercentual(data.maior_execucao.percentual, 1)}
          </span>
        </div>
        <div style={{ fontSize: '11px', color: '#9ca3af', textAlign: 'right' }}>
          {data.maior_execucao.municipio}
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// CONTAINER DOS 4 CARDS
// ============================================================================

interface DashboardCardsProps {
  municipios: MetricaMunicipios;
  orcamentoDisponivel: MetricaOrcamentoDisponivel;
  gapHistorico: MetricaGapHistorico;
  execucaoMedia: MetricaExecucaoMedia;
}

export const DashboardCards: React.FC<DashboardCardsProps> = ({
  municipios,
  orcamentoDisponivel,
  gapHistorico,
  execucaoMedia
}) => {
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '24px',
        marginBottom: '32px'
      }}
    >
      <MunicipiosCard data={municipios} />
      <OrcamentoDisponivelCard data={orcamentoDisponivel} />
      <GapHistoricoCard data={gapHistorico} />
      <ExecucaoMediaCard data={execucaoMedia} />
    </div>
  );
};

export default DashboardCards;
