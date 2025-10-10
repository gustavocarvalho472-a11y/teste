import React, { useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { BudgetData, AnalysisMode } from '../types';
import { formatCurrency, formatPerCapita, calculateVariation } from '../utils';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface TrendAnalysisChartProps {
  data: BudgetData[];
  analysisMode: AnalysisMode;
  onModeChange: (mode: AnalysisMode) => void;
}

const TrendAnalysisChart: React.FC<TrendAnalysisChartProps> = ({
  data,
  analysisMode,
  onModeChange
}) => {
  const getValue = (item: BudgetData): number => {
    switch (analysisMode) {
      case 'per-capita':
        return item.executed / item.population;
      case 'per-student':
        return item.executed / item.students;
      default:
        return item.executed;
    }
  };

  const chartData = useMemo(() => {
    // Agrupa por ano
    const yearlyData: Record<number, { value: number; isElection: boolean; population: number; students: number }> = {};

    data.forEach(item => {
      if (!yearlyData[item.year]) {
        yearlyData[item.year] = {
          value: 0,
          isElection: item.isElectionYear,
          population: item.population,
          students: item.students
        };
      }
      yearlyData[item.year].value += getValue(item);
    });

    const years = Object.keys(yearlyData).map(Number).sort();
    const values = years.map(year => yearlyData[year].value);

    return {
      labels: years.map(y => y.toString()),
      datasets: [{
        label: analysisMode === 'per-capita' ? 'Gasto per Capita' :
               analysisMode === 'per-student' ? 'Gasto por Estudante' : 'Gasto Total',
        data: values,
        borderColor: '#9755fe',
        backgroundColor: 'rgba(151, 85, 254, 0.1)',
        pointBackgroundColor: years.map(year =>
          yearlyData[year].isElection ? '#ef4444' : '#3b82f6'
        ),
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 8,
        pointHoverRadius: 10,
        tension: 0.3,
        fill: true
      }],
      metadata: yearlyData
    };
  }, [data, analysisMode]);

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top' as const,
        labels: {
          font: {
            size: 13,
            weight: '500'
          },
          padding: 16,
          usePointStyle: true,
        }
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const year = parseInt(context.label);
            const metadata = chartData.metadata[year];
            const value = context.parsed.y;

            let label = `Valor: ${analysisMode === 'absolute' ? formatCurrency(value) : formatPerCapita(value)}`;

            if (context.dataIndex > 0) {
              const prevValue = context.dataset.data[context.dataIndex - 1];
              const growth = calculateVariation(value, prevValue);
              label += `\nCrescimento: ${growth >= 0 ? '+' : ''}${growth.toFixed(1)}%`;
            }

            if (analysisMode === 'per-capita') {
              label += `\nPopulação: ${(metadata.population / 1000000).toFixed(1)}M`;
            } else if (analysisMode === 'per-student') {
              label += `\nEstudantes: ${(metadata.students / 1000000).toFixed(1)}M`;
            }

            label += metadata.isElection ? '\n🗳️ Ano Eleitoral' : '\n📊 Ano Regular';

            return label.split('\n');
          }
        },
        backgroundColor: '#2e3138',
        padding: 12,
        titleFont: {
          size: 14,
          weight: '600'
        },
        bodyFont: {
          size: 13
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value: any) {
            return analysisMode === 'absolute'
              ? formatCurrency(value, true)
              : formatPerCapita(value);
          },
          font: {
            size: 12
          }
        },
        grid: {
          color: '#f5edff'
        }
      },
      x: {
        grid: {
          display: false
        },
        ticks: {
          font: {
            size: 12,
            weight: '500'
          }
        }
      }
    }
  };

  // Cálculos do resumo analítico
  const summary = useMemo(() => {
    const years = Object.keys(chartData.metadata).map(Number).sort();
    const values = years.map(year => chartData.metadata[year].value);

    const growthRates = values.slice(1).map((val, idx) =>
      calculateVariation(val, values[idx])
    );
    const avgGrowth = growthRates.reduce((a, b) => a + b, 0) / growthRates.length;

    const maxValue = Math.max(...values);
    const maxYear = years[values.indexOf(maxValue)];

    const electionValues = years
      .filter(y => chartData.metadata[y].isElection)
      .map(y => chartData.metadata[y].value);
    const nonElectionValues = years
      .filter(y => !chartData.metadata[y].isElection)
      .map(y => chartData.metadata[y].value);

    const avgElection = electionValues.reduce((a, b) => a + b, 0) / electionValues.length;
    const avgNonElection = nonElectionValues.reduce((a, b) => a + b, 0) / nonElectionValues.length;
    const electionPattern = calculateVariation(avgElection, avgNonElection);

    return {
      avgGrowth,
      maxValue,
      maxYear,
      electionPattern,
      population: chartData.metadata[years[years.length - 1]].population,
      students: chartData.metadata[years[years.length - 1]].students
    };
  }, [chartData]);

  const modes = [
    { value: 'absolute' as AnalysisMode, label: 'Valores Absolutos' },
    { value: 'per-capita' as AnalysisMode, label: 'Per Capita' },
    { value: 'per-student' as AnalysisMode, label: 'Por Estudante' }
  ];

  return (
    <div style={{
      backgroundColor: '#ffffff',
      borderRadius: '12px',
      padding: '24px',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
      border: '1px solid #f5edff'
    }}>
      {/* Controles */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        <h3 style={{
          fontSize: '18px',
          fontWeight: '600',
          color: '#2e3138',
          margin: 0
        }}>
          Análise de Tendências
        </h3>

        <select
          value={analysisMode}
          onChange={(e) => onModeChange(e.target.value as AnalysisMode)}
          style={{
            padding: '8px 16px',
            borderRadius: '6px',
            border: '1px solid #d1b3ff',
            backgroundColor: '#ffffff',
            color: '#2e3138',
            fontSize: '14px',
            fontWeight: '500',
            cursor: 'pointer',
            outline: 'none'
          }}
        >
          {modes.map(mode => (
            <option key={mode.value} value={mode.value}>
              {mode.label}
            </option>
          ))}
        </select>
      </div>

      {/* Legenda */}
      <div style={{
        display: 'flex',
        gap: '24px',
        marginBottom: '16px',
        fontSize: '13px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            backgroundColor: '#ef4444'
          }} />
          <span style={{ color: '#6b7280' }}>Ano Eleitoral</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            backgroundColor: '#3b82f6'
          }} />
          <span style={{ color: '#6b7280' }}>Ano Regular</span>
        </div>
      </div>

      {/* Gráfico */}
      <div style={{ height: '400px' }}>
        <Line data={chartData} options={options} />
      </div>

      {/* Resumo Analítico */}
      <div style={{
        marginTop: '24px',
        padding: '20px',
        backgroundColor: '#f9f4ff',
        borderRadius: '8px',
        border: '1px solid #e1cdfe'
      }}>
        <div style={{
          fontSize: '14px',
          fontWeight: '600',
          color: '#3f127d',
          marginBottom: '16px'
        }}>
          Resumo Analítico
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '16px'
        }}>
          <div>
            <div style={{ fontSize: '12px', color: '#5219a1', marginBottom: '4px' }}>
              Crescimento Médio Anual
            </div>
            <div style={{ fontSize: '18px', fontWeight: '700', color: '#2e3138' }}>
              {summary.avgGrowth >= 0 ? '+' : ''}{summary.avgGrowth.toFixed(1)}%
            </div>
          </div>

          <div>
            <div style={{ fontSize: '12px', color: '#5219a1', marginBottom: '4px' }}>
              Maior Valor Histórico
            </div>
            <div style={{ fontSize: '18px', fontWeight: '700', color: '#2e3138' }}>
              {analysisMode === 'absolute'
                ? formatCurrency(summary.maxValue, true)
                : formatPerCapita(summary.maxValue)
              } ({summary.maxYear})
            </div>
          </div>

          <div>
            <div style={{ fontSize: '12px', color: '#5219a1', marginBottom: '4px' }}>
              Padrão Eleitoral
            </div>
            <div style={{
              fontSize: '18px',
              fontWeight: '700',
              color: summary.electionPattern >= 0 ? '#10b981' : '#ef4444'
            }}>
              {summary.electionPattern >= 0 ? '+' : ''}{summary.electionPattern.toFixed(1)}%
            </div>
            <div style={{ fontSize: '11px', color: '#6b7280', marginTop: '2px' }}>
              vs anos regulares
            </div>
          </div>

          {analysisMode !== 'absolute' && (
            <div>
              <div style={{ fontSize: '12px', color: '#5219a1', marginBottom: '4px' }}>
                Base {analysisMode === 'per-capita' ? 'Populacional' : 'Estudantil'}
              </div>
              <div style={{ fontSize: '18px', fontWeight: '700', color: '#2e3138' }}>
                {analysisMode === 'per-capita'
                  ? (summary.population / 1000000).toFixed(1) + 'M'
                  : (summary.students / 1000000).toFixed(1) + 'M'
                }
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TrendAnalysisChart;
