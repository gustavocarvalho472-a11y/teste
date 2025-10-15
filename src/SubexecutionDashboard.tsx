import React, { useState, useMemo } from 'react';
import SubexecutionFilters from './components/SubexecutionFilters';
import MunicipalityCard from './components/MunicipalityCard';
import MunicipalityRankingTable from './components/MunicipalityRankingTable';
import { municipalityBudgetData } from './mockData/municipalityData';
import { ComparisonMode, EntityType } from './types/municipality';
import { formatCurrency } from './utils';

function SubexecutionDashboard() {
  const [comparisonMode, setComparisonMode] = useState<ComparisonMode>('avg-electoral');
  const [entityType, setEntityType] = useState<EntityType | 'all'>('all');

  // Filtra e ordena municípios
  const filteredAndSortedMunicipalities = useMemo(() => {
    let filtered = [...municipalityBudgetData];

    // Filtra por tipo de entidade
    if (entityType !== 'all') {
      filtered = filtered.filter(m => m.type === entityType);
    }

    // Ordena por severity score (prioritário) e depois por dinheiro extra sobrando
    filtered.sort((a, b) => {
      // Primeiro por severity score
      if (b.severityScore !== a.severityScore) {
        return b.severityScore - a.severityScore;
      }

      // Depois por dinheiro extra sobrando
      const getExtra = (mun: typeof a) => {
        switch (comparisonMode) {
          case 'avg-electoral': return mun.comparison.avgElectoral.extraAvailable;
          case 'last-electoral': return mun.comparison.lastElectoral.extraAvailable;
          case 'avg-all': return mun.comparison.avgAll.extraAvailable;
          case 'previous-year': return mun.comparison.previousYear.extraAvailable;
        }
      };

      return getExtra(b) - getExtra(a);
    });

    return filtered;
  }, [entityType, comparisonMode]);

  // Conta anomalias
  const anomalyCount = useMemo(() => {
    return filteredAndSortedMunicipalities.filter(m => {
      const comparison = comparisonMode === 'avg-electoral' ? m.comparison.avgElectoral :
                        comparisonMode === 'last-electoral' ? m.comparison.lastElectoral :
                        comparisonMode === 'avg-all' ? m.comparison.avgAll :
                        m.comparison.previousYear;
      return comparison.isAnomaly;
    }).length;
  }, [filteredAndSortedMunicipalities, comparisonMode]);

  // Top 3 para destaque
  const top3 = filteredAndSortedMunicipalities.slice(0, 3);

  // Estatísticas gerais detalhadas
  const stats = useMemo(() => {
    const getComparison = (mun: typeof filteredAndSortedMunicipalities[0]) => {
      switch (comparisonMode) {
        case 'avg-electoral': return mun.comparison.avgElectoral;
        case 'last-electoral': return mun.comparison.lastElectoral;
        case 'avg-all': return mun.comparison.avgAll;
        case 'previous-year': return mun.comparison.previousYear;
      }
    };

    const totalExtra = filteredAndSortedMunicipalities.reduce((sum, m) => {
      const comp = getComparison(m);
      return sum + (comp.referenceAmount - comp.executedAmount);
    }, 0);

    const totalBudget = filteredAndSortedMunicipalities.reduce((sum, m) => sum + m.totalBudget, 0);
    const totalExecuted = filteredAndSortedMunicipalities.reduce((sum, m) => sum + m.executed, 0);

    const avgDeviation = filteredAndSortedMunicipalities.reduce((sum, m) => {
      return sum + Math.abs(getComparison(m).percentageDeviation);
    }, 0) / (filteredAndSortedMunicipalities.length || 1);

    // Contar por severidade
    const critical = filteredAndSortedMunicipalities.filter(m => getComparison(m).severity === 'critical').length;
    const high = filteredAndSortedMunicipalities.filter(m => getComparison(m).severity === 'high').length;
    const moderate = filteredAndSortedMunicipalities.filter(m => getComparison(m).severity === 'moderate').length;

    // Ranking por estado
    const byState = filteredAndSortedMunicipalities.reduce((acc, m) => {
      if (!acc[m.state]) {
        acc[m.state] = { count: 0, totalExtra: 0, totalBudget: 0 };
      }
      acc[m.state].count++;
      acc[m.state].totalExtra += (getComparison(m).referenceAmount - getComparison(m).executedAmount);
      acc[m.state].totalBudget += m.totalBudget;
      return acc;
    }, {} as Record<string, { count: number; totalExtra: number; totalBudget: number }>);

    const stateRanking = Object.entries(byState)
      .map(([state, data]) => ({
        state,
        count: data.count,
        totalExtra: data.totalExtra,
        avgExtra: data.totalExtra / data.count,
        totalBudget: data.totalBudget
      }))
      .sort((a, b) => b.totalExtra - a.totalExtra)
      .slice(0, 5);

    return {
      totalExtra,
      totalBudget,
      totalExecuted,
      avgDeviation,
      critical,
      high,
      moderate,
      stateRanking,
      executionRate: (totalExecuted / totalBudget) * 100
    };
  }, [filteredAndSortedMunicipalities, comparisonMode]);

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
        background: 'linear-gradient(135deg, #2e3138 0%, #3f127d 100%)'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <div style={{
            fontSize: '14px',
            fontWeight: '600',
            color: '#d1b3ff',
            textTransform: 'uppercase',
            letterSpacing: '1px',
            marginBottom: '8px'
          }}>
            Análise Automática de Subexecução Orçamentária
          </div>
          <h1 style={{
            fontSize: '36px',
            fontWeight: '700',
            color: '#ffffff',
            margin: 0,
            lineHeight: '1.2'
          }}>
            🎯 Ranking de Municípios por Recursos Disponíveis
          </h1>
          <p style={{
            fontSize: '15px',
            color: '#ba90fc',
            marginTop: '12px',
            margin: 0
          }}>
            Identificação automática de municípios com maior subexecução orçamentária · Prioriza recursos não utilizados
          </p>
        </div>

        {/* Stats Grid - Principal */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '16px',
          marginBottom: '16px'
        }}>
          <div style={{
            backgroundColor: 'rgba(16, 185, 129, 0.15)',
            borderRadius: '12px',
            padding: '20px',
            border: '2px solid rgba(16, 185, 129, 0.3)',
            backdropFilter: 'blur(10px)'
          }}>
            <div style={{
              fontSize: '11px',
              fontWeight: '700',
              color: '#6ee7b7',
              marginBottom: '8px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              💰 Total Disponível (Sobra)
            </div>
            <div style={{
              fontSize: '36px',
              fontWeight: '700',
              color: '#ffffff',
              lineHeight: '1',
              marginBottom: '8px'
            }}>
              {formatCurrency(stats.totalExtra, true)}
            </div>
            <div style={{
              fontSize: '12px',
              color: '#a7f3d0',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <span>📈</span>
              <span>de {formatCurrency(stats.totalBudget, true)} orçado</span>
            </div>
          </div>

          <div style={{
            backgroundColor: 'rgba(59, 130, 246, 0.15)',
            borderRadius: '12px',
            padding: '20px',
            border: '2px solid rgba(59, 130, 246, 0.3)',
            backdropFilter: 'blur(10px)'
          }}>
            <div style={{
              fontSize: '11px',
              fontWeight: '700',
              color: '#93c5fd',
              marginBottom: '8px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              📊 Taxa de Execução Média
            </div>
            <div style={{
              fontSize: '36px',
              fontWeight: '700',
              color: '#ffffff',
              lineHeight: '1',
              marginBottom: '8px'
            }}>
              {stats.executionRate.toFixed(1)}%
            </div>
            <div style={{
              fontSize: '12px',
              color: '#bfdbfe',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <span>💡</span>
              <span>{formatCurrency(stats.totalExecuted, true)} executado</span>
            </div>
          </div>

          <div style={{
            backgroundColor: 'rgba(239, 68, 68, 0.15)',
            borderRadius: '12px',
            padding: '20px',
            border: '2px solid rgba(239, 68, 68, 0.3)',
            backdropFilter: 'blur(10px)'
          }}>
            <div style={{
              fontSize: '11px',
              fontWeight: '700',
              color: '#fca5a5',
              marginBottom: '8px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              🚨 Desvio do Padrão
            </div>
            <div style={{
              fontSize: '36px',
              fontWeight: '700',
              color: '#ffffff',
              lineHeight: '1',
              marginBottom: '8px'
            }}>
              {stats.avgDeviation.toFixed(1)}%
            </div>
            <div style={{
              fontSize: '12px',
              color: '#fecaca',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <span>⚠️</span>
              <span>{stats.critical} críticos, {stats.high} altos</span>
            </div>
          </div>

          <div style={{
            backgroundColor: 'rgba(168, 85, 247, 0.15)',
            borderRadius: '12px',
            padding: '20px',
            border: '2px solid rgba(168, 85, 247, 0.3)',
            backdropFilter: 'blur(10px)'
          }}>
            <div style={{
              fontSize: '11px',
              fontWeight: '700',
              color: '#d8b4fe',
              marginBottom: '8px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              📍 Municípios Analisados
            </div>
            <div style={{
              fontSize: '36px',
              fontWeight: '700',
              color: '#ffffff',
              lineHeight: '1',
              marginBottom: '8px'
            }}>
              {filteredAndSortedMunicipalities.length}
            </div>
            <div style={{
              fontSize: '12px',
              color: '#e9d5ff',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <span>🗺️</span>
              <span>{stats.stateRanking.length} estados diferentes</span>
            </div>
          </div>
        </div>

        {/* Ranking de Estados */}
        <div style={{
          backgroundColor: 'rgba(255, 255, 255, 0.08)',
          borderRadius: '12px',
          padding: '20px',
          border: '1px solid rgba(255, 255, 255, 0.12)',
          backdropFilter: 'blur(10px)'
        }}>
          <div style={{
            fontSize: '13px',
            fontWeight: '700',
            color: '#ffffff',
            marginBottom: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <span>🏆</span>
            <span>Top 5 Estados com Maior Subexecução</span>
          </div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
            gap: '12px'
          }}>
            {stats.stateRanking.map((state, index) => (
              <div key={state.state} style={{
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                borderRadius: '8px',
                padding: '12px',
                border: '1px solid rgba(255, 255, 255, 0.1)'
              }}>
                <div style={{
                  fontSize: '11px',
                  color: '#d1b3ff',
                  fontWeight: '600',
                  marginBottom: '4px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}>
                  <span>{index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `${index + 1}º`}</span>
                  <span>{state.state}</span>
                </div>
                <div style={{
                  fontSize: '18px',
                  fontWeight: '700',
                  color: '#ffffff',
                  marginBottom: '2px'
                }}>
                  {formatCurrency(state.totalExtra, true)}
                </div>
                <div style={{
                  fontSize: '10px',
                  color: '#ba90fc'
                }}>
                  {state.count} município{state.count > 1 ? 's' : ''}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Filtros */}
      <SubexecutionFilters
        comparisonMode={comparisonMode}
        onComparisonModeChange={setComparisonMode}
        entityType={entityType}
        onEntityTypeChange={setEntityType}
        totalCount={filteredAndSortedMunicipalities.length}
        anomalyCount={anomalyCount}
      />

      {/* Top 3 Cards */}
      <div style={{ marginBottom: '32px' }}>
        <h2 style={{
          fontSize: '24px',
          fontWeight: '700',
          color: '#2e3138',
          marginBottom: '20px'
        }}>
          🏆 Top 3 Municípios com Maior Subexecução
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
          gap: '24px'
        }}>
          {top3.map((mun, index) => (
            <MunicipalityCard
              key={mun.id}
              municipality={mun}
              comparisonMode={comparisonMode}
              rank={index + 1}
            />
          ))}
        </div>
      </div>

      {/* Tabela Completa */}
      <MunicipalityRankingTable
        municipalities={filteredAndSortedMunicipalities}
        comparisonMode={comparisonMode}
      />

      {/* Footer */}
      <div style={{
        marginTop: '48px',
        padding: '24px',
        textAlign: 'center',
        color: '#6b7280',
        fontSize: '13px'
      }}>
        <p style={{ margin: 0 }}>
          Dashboard de Análise de Subexecução Orçamentária Municipal · Educação Brasil 2024
        </p>
        <p style={{ margin: '8px 0 0 0', fontSize: '12px' }}>
          Prioriza municípios com maior disponibilidade de recursos não executados vs períodos anteriores
        </p>
      </div>
    </div>
  );
}

export default SubexecutionDashboard;
