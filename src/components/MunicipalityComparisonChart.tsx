import React, { useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface MunicipalityComparison {
  name: string;
  executed: number;
  reference: number;
  deviation: number;
  comparisonExecuted?: number; // Valor executado no período de comparação
}

interface MunicipalityComparisonChartProps {
  municipalities: MunicipalityComparison[];
  metric: 'executed' | 'deviation' | 'extra';
  currentPeriod?: number;
  comparisonPeriod?: number;
}

const MunicipalityComparisonChart: React.FC<MunicipalityComparisonChartProps> = ({
  municipalities,
  metric,
  currentPeriod,
  comparisonPeriod
}) => {
  const chartData = useMemo(() => {
    const sortedMunicipalities = [...municipalities].sort((a, b) => {
      if (metric === 'executed') return b.executed - a.executed;
      if (metric === 'deviation') return a.deviation - b.deviation;
      return (b.reference - b.executed) - (a.reference - a.executed);
    });

    const topMunicipalities = sortedMunicipalities.slice(0, 10);

    let currentValues: number[];
    let comparisonValues: number[];
    let currentLabel: string;
    let comparisonLabel: string;

    if (metric === 'executed') {
      currentValues = topMunicipalities.map(m => m.executed);
      comparisonValues = topMunicipalities.map(m => m.comparisonExecuted || 0);
      currentLabel = `${currentPeriod || 'Atual'} - Executado`;
      comparisonLabel = `${comparisonPeriod || 'Comparação'} 🗳️ - Executado`;
    } else if (metric === 'deviation') {
      currentValues = topMunicipalities.map(m => m.deviation);
      comparisonValues = topMunicipalities.map(m =>
        m.comparisonExecuted ? ((m.comparisonExecuted / m.reference) - 1) * 100 : 0
      );
      currentLabel = `${currentPeriod || 'Atual'} - Desvio %`;
      comparisonLabel = `${comparisonPeriod || 'Comparação'} 🗳️ - Desvio %`;
    } else {
      currentValues = topMunicipalities.map(m => m.reference - m.executed);
      comparisonValues = topMunicipalities.map(m =>
        m.comparisonExecuted ? m.reference - m.comparisonExecuted : 0
      );
      currentLabel = `${currentPeriod || 'Atual'} - Sobra`;
      comparisonLabel = `${comparisonPeriod || 'Comparação'} 🗳️ - Sobra`;
    }

    const datasets: any[] = [
      {
        label: currentLabel,
        data: currentValues,
        backgroundColor: '#10b981',
        borderRadius: 6,
        borderWidth: 0
      }
    ];

    // Adicionar dataset de comparação se houver dados
    const hasComparisonData = comparisonValues.some(v => v > 0);
    if (hasComparisonData && comparisonPeriod) {
      datasets.push({
        label: comparisonLabel,
        data: comparisonValues,
        backgroundColor: '#3b82f6',
        borderRadius: 6,
        borderWidth: 0
      });
    }

    return {
      labels: topMunicipalities.map(m => m.name),
      datasets
    };
  }, [municipalities, metric, currentPeriod, comparisonPeriod]);

  const options: ChartOptions<'bar'> = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y',
    plugins: {
      legend: {
        display: true,
        position: 'bottom',
        labels: {
          font: { size: 13, weight: '600' },
          padding: 16,
          usePointStyle: true,
          boxWidth: 12,
          boxHeight: 12
        }
      },
      title: {
        display: true,
        text: `Comparação: Top 10 Municípios`,
        font: { size: 16, weight: '700' },
        color: '#2e3138',
        padding: { bottom: 20 }
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const value = context.parsed.x;
            if (metric === 'deviation') {
              return `Desvio: ${value.toFixed(1)}%`;
            }
            return new Intl.NumberFormat('pt-BR', {
              style: 'currency',
              currency: 'BRL',
              notation: 'compact',
              maximumFractionDigits: 1
            }).format(value);
          }
        },
        backgroundColor: '#2e3138',
        padding: 12,
        titleFont: { size: 14, weight: '700' },
        bodyFont: { size: 13 }
      }
    },
    scales: {
      x: {
        beginAtZero: true,
        ticks: {
          callback: function(value) {
            if (metric === 'deviation') {
              return `${value}%`;
            }
            return new Intl.NumberFormat('pt-BR', {
              style: 'currency',
              currency: 'BRL',
              notation: 'compact',
              maximumFractionDigits: 0
            }).format(value as number);
          },
          font: { size: 12 },
          color: '#6b7280'
        },
        grid: { color: '#f5edff' }
      },
      y: {
        ticks: {
          font: { size: 12 },
          color: '#6b7280'
        },
        grid: { display: false }
      }
    }
  };

  return (
    <div style={{
      backgroundColor: '#ffffff',
      borderRadius: '12px',
      padding: '24px',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
      border: '1px solid #f5edff',
      height: '500px'
    }}>
      <Bar data={chartData} options={options} />
    </div>
  );
};

export default MunicipalityComparisonChart;
