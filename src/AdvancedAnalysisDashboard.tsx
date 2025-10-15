import React, { useMemo } from 'react';
import BrazilMap from './components/BrazilMap';
import ExceptionalPeriodCard from './components/ExceptionalPeriodCard';
import ClusterScatterChart from './components/ClusterScatterChart';
import { enrichedMockData } from './mockDataEnriched';
import { kMeansClustering, identifyBehaviorPatterns, ClusterPoint } from './utils/clustering';
import { calculateMean } from './utils/anomalyDetection';

function AdvancedAnalysisDashboard() {
  // Agrupa dados por ano para clustering
  const yearlyData = useMemo(() => {
    const grouped: Record<number, { total: number; count: number; isElection: boolean }> = {};

    enrichedMockData.forEach(item => {
      if (!grouped[item.year]) {
        grouped[item.year] = { total: 0, count: 0, isElection: item.isElectionYear };
      }
      grouped[item.year].total += item.executed;
      grouped[item.year].count++;
    });

    const years = Object.keys(grouped).map(Number);
    const values = years.map(y => grouped[y].total);
    const mean = calculateMean(values);

    return years.map(year => ({
      year,
      value: grouped[year].total,
      deviation: ((grouped[year].total - mean) / mean) * 100,
      isElectionYear: grouped[year].isElection,
      executionRate: (grouped[year].total / grouped[year].count) * 0.85 // Aproximação
    }));
  }, []);

  // Clustering
  const clusterPoints: ClusterPoint[] = yearlyData.map(y => ({
    year: y.year,
    value: y.value,
    deviation: y.deviation,
    isElectionYear: y.isElectionYear,
    executionRate: y.executionRate
  }));

  const clusters = useMemo(() => kMeansClustering(clusterPoints, 4), [clusterPoints]);
  const patterns = useMemo(() => identifyBehaviorPatterns(clusters), [clusters]);

  // Dados regionais
  const regionData = useMemo(() => [
    {
      name: 'Norte',
      value: 18500000000,
      deviation: -12.3,
      states: ['AM', 'PA', 'AC', 'RO', 'RR', 'AP', 'TO']
    },
    {
      name: 'Nordeste',
      value: 35200000000,
      deviation: -15.7,
      states: ['MA', 'PI', 'CE', 'RN', 'PB', 'PE', 'AL', 'SE', 'BA']
    },
    {
      name: 'Centro-Oeste',
      value: 21800000000,
      deviation: -8.4,
      states: ['MT', 'MS', 'GO', 'DF']
    },
    {
      name: 'Sudeste',
      value: 58900000000,
      deviation: -18.2,
      states: ['SP', 'RJ', 'MG', 'ES']
    },
    {
      name: 'Sul',
      value: 22400000000,
      deviation: -10.1,
      states: ['PR', 'SC', 'RS']
    }
  ], []);

  // Períodos excepcionais
  const exceptionalPeriods = useMemo(() => [
    {
      id: 'pandemia',
      name: 'Pandemia COVID-19',
      icon: '🦠',
      years: [2020, 2021],
      description: 'Período de crise sanitária global que impactou significativamente o orçamento de educação com fechamento de escolas e redução de atividades presenciais.',
      avgDeviation: -18.2,
      totalImpact: -27300000000,
      color: '#ef4444',
      recovery: {
        year: 2022,
        recovered: 12.4
      }
    },
    {
      id: 'crise-2016',
      name: 'Crise Econômica 2015-2016',
      icon: '⚠️',
      years: [2015, 2016],
      description: 'Recessão econômica brasileira com impeachment presidencial, resultando em forte ajuste fiscal e cortes no orçamento de educação.',
      avgDeviation: -14.8,
      totalImpact: -19800000000,
      color: '#f59e0b',
      recovery: {
        year: 2017,
        recovered: 8.2
      }
    },
    {
      id: 'corte-2019',
      name: 'Corte Histórico 2019',
      icon: '🔴',
      years: [2019],
      description: 'Maior corte orçamentário registrado na série histórica, com redução de 23% no orçamento de educação logo no primeiro ano do governo Bolsonaro.',
      avgDeviation: -23.4,
      totalImpact: -34500000000,
      color: '#dc2626'
    }
  ], []);

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f9f4ff',
      padding: '32px',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    }}>
      {/* Hero Section */}
      <div style={{
        backgroundColor: '#2e3138',
        borderRadius: '16px',
        padding: '40px',
        marginBottom: '32px',
        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.15)',
        background: 'linear-gradient(135deg, #2e3138 0%, #5219a1 100%)'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            fontSize: '14px',
            fontWeight: '600',
            color: '#d1b3ff',
            textTransform: 'uppercase',
            letterSpacing: '1px',
            marginBottom: '8px'
          }}>
            Análise Avançada com Machine Learning
          </div>
          <h1 style={{
            fontSize: '36px',
            fontWeight: '700',
            color: '#ffffff',
            margin: 0,
            lineHeight: '1.2',
            marginBottom: '12px'
          }}>
            🧠 Dashboard de Inteligência Orçamentária
          </h1>
          <p style={{
            fontSize: '16px',
            color: '#ba90fc',
            margin: 0
          }}>
            Clustering K-means · Análise Regional · Períodos Excepcionais · Padrões de Comportamento
          </p>
        </div>
      </div>

      {/* Padrões Identificados */}
      <div style={{
        backgroundColor: '#ffffff',
        borderRadius: '12px',
        padding: '24px',
        marginBottom: '32px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
        border: '1px solid #f5edff'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          marginBottom: '16px'
        }}>
          <span style={{ fontSize: '24px' }}>🔍</span>
          <h2 style={{
            fontSize: '20px',
            fontWeight: '600',
            color: '#2e3138',
            margin: 0
          }}>
            Padrões Identificados Automaticamente
          </h2>
        </div>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '12px'
        }}>
          {patterns.map((pattern, index) => (
            <div
              key={index}
              style={{
                padding: '12px 16px',
                backgroundColor: '#f9f4ff',
                borderRadius: '8px',
                borderLeft: '4px solid #9755fe',
                fontSize: '14px',
                color: '#2e3138',
                lineHeight: '1.6'
              }}
            >
              <strong>{index + 1}.</strong> {pattern}
            </div>
          ))}
        </div>
      </div>

      {/* Gráfico de Clusters */}
      <div style={{ marginBottom: '32px' }}>
        <ClusterScatterChart clusters={clusters} />
      </div>

      {/* Mapa Regional */}
      <div style={{ marginBottom: '32px' }}>
        <BrazilMap
          regionData={regionData}
          onRegionClick={(region) => console.log('Região clicada:', region)}
        />
      </div>

      {/* Períodos Excepcionais */}
      <div style={{ marginBottom: '32px' }}>
        <h2 style={{
          fontSize: '24px',
          fontWeight: '700',
          color: '#2e3138',
          marginBottom: '20px'
        }}>
          ⚡ Períodos Excepcionais
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
          gap: '24px'
        }}>
          {exceptionalPeriods.map(period => (
            <ExceptionalPeriodCard key={period.id} period={period} />
          ))}
        </div>
      </div>

      {/* Resumo Executivo */}
      <div style={{
        backgroundColor: '#ffffff',
        borderRadius: '12px',
        padding: '32px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
        border: '1px solid #f5edff'
      }}>
        <h2 style={{
          fontSize: '20px',
          fontWeight: '700',
          color: '#2e3138',
          marginBottom: '16px'
        }}>
          📋 Resumo Executivo
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '24px'
        }}>
          <div>
            <div style={{
              fontSize: '13px',
              fontWeight: '600',
              color: '#5219a1',
              marginBottom: '8px',
              textTransform: 'uppercase'
            }}>
              Clusters Identificados
            </div>
            <div style={{
              fontSize: '32px',
              fontWeight: '700',
              color: '#2e3138',
              marginBottom: '4px'
            }}>
              {clusters.length}
            </div>
            <div style={{
              fontSize: '13px',
              color: '#6b7280'
            }}>
              Padrões de comportamento distintos
            </div>
          </div>

          <div>
            <div style={{
              fontSize: '13px',
              fontWeight: '600',
              color: '#5219a1',
              marginBottom: '8px',
              textTransform: 'uppercase'
            }}>
              Regiões Analisadas
            </div>
            <div style={{
              fontSize: '32px',
              fontWeight: '700',
              color: '#2e3138',
              marginBottom: '4px'
            }}>
              5
            </div>
            <div style={{
              fontSize: '13px',
              color: '#6b7280'
            }}>
              Todas com subexecução identificada
            </div>
          </div>

          <div>
            <div style={{
              fontSize: '13px',
              fontWeight: '600',
              color: '#5219a1',
              marginBottom: '8px',
              textTransform: 'uppercase'
            }}>
              Períodos Excepcionais
            </div>
            <div style={{
              fontSize: '32px',
              fontWeight: '700',
              color: '#2e3138',
              marginBottom: '4px'
            }}>
              3
            </div>
            <div style={{
              fontSize: '13px',
              color: '#6b7280'
            }}>
              Crises e eventos de alto impacto
            </div>
          </div>

          <div>
            <div style={{
              fontSize: '13px',
              fontWeight: '600',
              color: '#5219a1',
              marginBottom: '8px',
              textTransform: 'uppercase'
            }}>
              Anos Analisados
            </div>
            <div style={{
              fontSize: '32px',
              fontWeight: '700',
              color: '#2e3138',
              marginBottom: '4px'
            }}>
              {yearlyData.length}
            </div>
            <div style={{
              fontSize: '13px',
              color: '#6b7280'
            }}>
              Série histórica completa (2015-2024)
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div style={{
        marginTop: '48px',
        padding: '16px',
        textAlign: 'center',
        color: '#6b7280',
        fontSize: '13px'
      }}>
        <p style={{ margin: 0 }}>
          Dashboard de Análise Avançada · Powered by K-means Clustering & Statistical Analysis
        </p>
      </div>
    </div>
  );
}

export default AdvancedAnalysisDashboard;
