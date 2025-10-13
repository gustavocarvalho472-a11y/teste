import React, { useMemo } from 'react';
import AnomalyHeroStats from './components/AnomalyHeroStats';
import AnomalyTimeline from './components/AnomalyTimeline';
import AnomalyCard from './components/AnomalyCard';
import { enrichedMockData } from './mockDataEnriched';
import { detectYearlyAnomalies, getTopAnomalies, calculateAnomalyStats } from './utils/anomalyDetection';

function AnomalyDashboard() {
  // Agrupa dados por ano
  const yearlyData = useMemo(() => {
    const grouped: Record<number, { total: number; count: number; isElection: boolean }> = {};

    enrichedMockData.forEach(item => {
      if (!grouped[item.year]) {
        grouped[item.year] = { total: 0, count: 0, isElection: item.isElectionYear };
      }
      grouped[item.year].total += item.executed;
      grouped[item.year].count++;
    });

    return Object.keys(grouped).map(year => ({
      year: parseInt(year),
      value: grouped[parseInt(year)].total,
      isElectionYear: grouped[parseInt(year)].isElection
    }));
  }, []);

  // Detecta anomalias
  const anomalies = useMemo(() => {
    return detectYearlyAnomalies(yearlyData);
  }, [yearlyData]);

  // Top 3 anomalias
  const topAnomalies = useMemo(() => {
    return getTopAnomalies(anomalies, 3);
  }, [anomalies]);

  // Estatísticas gerais
  const stats = useMemo(() => {
    return calculateAnomalyStats(anomalies);
  }, [anomalies]);

  // Insights automáticos
  const insights = useMemo(() => {
    const insights: string[] = [];

    if (stats.electionPattern > 5) {
      insights.push(`Anos eleitorais apresentam aumento médio de ${stats.electionPattern.toFixed(1)}% no orçamento`);
    } else if (stats.electionPattern < -5) {
      insights.push(`Anos eleitorais têm redução média de ${Math.abs(stats.electionPattern).toFixed(1)}% no orçamento`);
    }

    const largestDrop = topAnomalies.find(a => a.zScore < 0);
    if (largestDrop) {
      insights.push(`Maior corte histórico: ${largestDrop.year} (${largestDrop.percentageDeviation.toFixed(1)}%)`);
    }

    const pandemicYears = anomalies.filter(a =>
      (a.year === 2020 || a.year === 2021) && a.zScore < 0
    );
    if (pandemicYears.length > 0) {
      const avgPandemicImpact = pandemicYears.reduce((sum, a) => sum + a.percentageDeviation, 0) / pandemicYears.length;
      insights.push(`Pandemia impactou ${Math.abs(avgPandemicImpact).toFixed(1)}% do orçamento (2020-2021)`);
    }

    if (stats.criticalCount > 0) {
      insights.push(`${stats.criticalCount} ano(s) com anomalia crítica (>3σ) detectada`);
    }

    const cyclicPattern = anomalies.filter(a => a.isElectionYear && a.zScore > 0).length;
    if (cyclicPattern >= 3) {
      insights.push(`Padrão cíclico detectado: aumentos consistentes em anos eleitorais`);
    }

    return insights;
  }, [anomalies, topAnomalies, stats]);

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f9f4ff',
      padding: '32px',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    }}>
      {/* Hero Stats */}
      <AnomalyHeroStats
        totalAnomalies={stats.totalAnomalies}
        criticalCount={stats.criticalCount}
        moderateCount={stats.moderateCount}
        electionPattern={stats.electionPattern}
        maxAnomaly={stats.maxAnomaly}
      />

      {/* Timeline */}
      <div style={{ marginBottom: '32px' }}>
        <AnomalyTimeline anomalies={anomalies} />
      </div>

      {/* Insights Automáticos */}
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
          <span style={{ fontSize: '24px' }}>💡</span>
          <h3 style={{
            fontSize: '18px',
            fontWeight: '600',
            color: '#2e3138',
            margin: 0
          }}>
            Insights Principais
          </h3>
        </div>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '12px'
        }}>
          {insights.map((insight, index) => (
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
              <strong>{index + 1}.</strong> {insight}
            </div>
          ))}
        </div>
      </div>

      {/* Top 3 Anomalias */}
      <div style={{ marginBottom: '32px' }}>
        <h2 style={{
          fontSize: '24px',
          fontWeight: '700',
          color: '#2e3138',
          marginBottom: '20px'
        }}>
          🎯 Maiores Anomalias Detectadas
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
          gap: '24px'
        }}>
          {topAnomalies.map((anomaly, index) => (
            <AnomalyCard
              key={anomaly.year}
              anomaly={anomaly}
              rank={index + 1}
            />
          ))}
        </div>
      </div>

      {/* Footer com explicação metodológica */}
      <div style={{
        marginTop: '48px',
        padding: '24px',
        backgroundColor: '#ffffff',
        borderRadius: '12px',
        border: '1px solid #e1cdfe'
      }}>
        <h4 style={{
          fontSize: '16px',
          fontWeight: '600',
          color: '#3f127d',
          marginBottom: '12px'
        }}>
          📚 Metodologia de Análise
        </h4>
        <div style={{
          fontSize: '13px',
          color: '#6b7280',
          lineHeight: '1.8'
        }}>
          <p style={{ margin: '0 0 8px 0' }}>
            <strong>Detecção de Anomalias:</strong> Utilizamos análise estatística baseada em Z-score (desvio padrão)
            para identificar anos com comportamento orçamentário significativamente diferente da média histórica.
          </p>
          <p style={{ margin: '0 0 8px 0' }}>
            <strong>Classificação:</strong> 🔴 Crítico (&gt;3σ), 🟡 Moderado (2-3σ), 🟢 Normal (&lt;2σ)
          </p>
          <p style={{ margin: '0' }}>
            <strong>Contexto:</strong> Análise considera eventos políticos (eleições, mudanças de governo),
            econômicos (crises) e sanitários (pandemia) para interpretação dos desvios.
          </p>
        </div>
      </div>

      {/* Footer */}
      <div style={{
        marginTop: '32px',
        padding: '16px',
        textAlign: 'center',
        color: '#6b7280',
        fontSize: '13px'
      }}>
        <p style={{ margin: 0 }}>
          Dashboard de Análise Estatística de Anomalias Orçamentárias · Educação Brasil (2015-2024)
        </p>
        <p style={{ margin: '8px 0 0 0', fontSize: '12px' }}>
          Powered by Claude Code · Análise automática baseada em desvio padrão
        </p>
      </div>
    </div>
  );
}

export default AnomalyDashboard;
