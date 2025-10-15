import React, { useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface YearlyData {
  year: number;
  executed: number;
  reference: number;
  deviation: number;
}

interface MunicipalityTimeSeriesChartProps {
  municipalityName: string;
  data: YearlyData[];
  chartType: 'line' | 'bar';
  comparisonYear?: number;
  comparisonValue?: number;
}

const MunicipalityTimeSeriesChart: React.FC<MunicipalityTimeSeriesChartProps> = ({
  municipalityName,
  data,
  chartType,
  comparisonYear,
  comparisonValue
}) => {
  const chartData = useMemo(() => {
    console.log('MunicipalityTimeSeriesChart - Comparison Year:', comparisonYear);
    console.log('MunicipalityTimeSeriesChart - Comparison Value:', comparisonValue);
    console.log('MunicipalityTimeSeriesChart - Data:', data);

    const datasets: any[] = [
      {
        label: 'Executado',
        data: data.map(d => d.executed),
        backgroundColor: '#9755fe',
        borderColor: '#9755fe',
        borderWidth: 3,
        pointRadius: 6,
        pointHoverRadius: 8,
        tension: 0.4
      },
      {
        label: 'Referência (Orçamento Total)',
        data: data.map(d => d.reference),
        backgroundColor: '#6b7280',
        borderColor: '#6b7280',
        borderWidth: 3,
        borderDash: [5, 5],
        pointRadius: 6,
        pointHoverRadius: 8,
        tension: 0.4
      }
    ];

    // Adicionar linha de comparação com ano eleitoral se fornecido
    if (comparisonYear && comparisonValue !== undefined && comparisonValue > 0) {
      console.log('ADICIONANDO LINHA DE COMPARAÇÃO!');
      datasets.push({
        label: `📊 ${comparisonYear} (Ano Eleitoral)`,
        data: data.map(() => comparisonValue),
        backgroundColor: '#ef4444',
        borderColor: '#ef4444',
        borderWidth: 3,
        borderDash: [10, 5],
        pointRadius: 0,
        pointHoverRadius: 6,
        tension: 0,
        fill: false
      });
    }

    return {
      labels: data.map(d => d.year.toString()),
      datasets
    };
  }, [data, comparisonYear, comparisonValue]);

  const options: ChartOptions<'line' | 'bar'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          font: { size: 13, weight: '600' },
          padding: 16,
          usePointStyle: true
        }
      },
      title: {
        display: true,
        text: `Série Temporal: ${municipalityName}`,
        font: { size: 16, weight: '700' },
        color: '#2e3138',
        padding: { bottom: 20 }
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const label = context.dataset.label || '';
            const value = context.parsed.y;
            const formatted = new Intl.NumberFormat('pt-BR', {
              style: 'currency',
              currency: 'BRL',
              notation: 'compact',
              maximumFractionDigits: 1
            }).format(value);
            return `${label}: ${formatted}`;
          }
        },
        backgroundColor: '#2e3138',
        padding: 12,
        titleFont: { size: 14, weight: '700' },
        bodyFont: { size: 13 }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value) {
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
      x: {
        ticks: {
          font: { size: 12 },
          color: '#6b7280'
        },
        grid: { display: false }
      }
    }
  };

  const ChartComponent = chartType === 'line' ? Line : Bar;

  return (
    <div style={{
      backgroundColor: '#ffffff',
      borderRadius: '12px',
      padding: '24px',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
      border: '1px solid #f5edff',
      height: '400px'
    }}>
      <ChartComponent data={chartData} options={options} />
    </div>
  );
};

export default MunicipalityTimeSeriesChart;
