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
  Legend
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import { BudgetData } from '../types';
import { formatCurrency, getMonthShortName } from '../utils';

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

interface TraditionalChartsProps {
  data: BudgetData[];
  selectedYear: number;
}

const TraditionalCharts: React.FC<TraditionalChartsProps> = ({
  data,
  selectedYear
}) => {
  // Gráfico de Evolução Mensal
  const monthlyEvolutionData = useMemo(() => {
    const yearData = data.filter(d => d.year === selectedYear);
    const months = Array.from({ length: 12 }, (_, i) => i + 1);

    return {
      labels: months.map(m => getMonthShortName(m)),
      datasets: [
        {
          label: 'Planejado',
          data: months.map(month => {
            const item = yearData.find(d => d.month === month);
            return item ? item.planned : 0;
          }),
          borderColor: '#9755fe',
          backgroundColor: 'rgba(151, 85, 254, 0.1)',
          tension: 0.3,
          fill: true,
          pointRadius: 4,
          pointHoverRadius: 6
        },
        {
          label: 'Executado',
          data: months.map(month => {
            const item = yearData.find(d => d.month === month);
            return item ? item.executed : 0;
          }),
          borderColor: '#5219a1',
          backgroundColor: 'rgba(82, 25, 161, 0.1)',
          tension: 0.3,
          fill: true,
          pointRadius: 4,
          pointHoverRadius: 6
        }
      ]
    };
  }, [data, selectedYear]);

  // Gráfico Comparativo Eleitoral
  const electoralComparisonData = useMemo(() => {
    const yearlyData: Record<number, { planned: number; executed: number; isElection: boolean }> = {};

    data.forEach(item => {
      if (!yearlyData[item.year]) {
        yearlyData[item.year] = { planned: 0, executed: 0, isElection: item.isElectionYear };
      }
      yearlyData[item.year].planned += item.planned;
      yearlyData[item.year].executed += item.executed;
    });

    const years = Object.keys(yearlyData).map(Number).sort();

    return {
      labels: years.map(y => y.toString()),
      datasets: [
        {
          label: 'Planejado',
          data: years.map(year => yearlyData[year].planned),
          backgroundColor: years.map(year =>
            yearlyData[year].isElection ? '#ef4444' : '#3b82f6'
          ),
          borderRadius: 6,
        },
        {
          label: 'Executado',
          data: years.map(year => yearlyData[year].executed),
          backgroundColor: years.map(year =>
            yearlyData[year].isElection ? '#fca5a5' : '#93c5fd'
          ),
          borderRadius: 6,
        }
      ]
    };
  }, [data]);

  const lineOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          font: { size: 13, weight: '500' },
          padding: 16,
          usePointStyle: true,
        }
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            return `${context.dataset.label}: ${formatCurrency(context.parsed.y)}`;
          }
        },
        backgroundColor: '#2e3138',
        padding: 12,
        titleFont: { size: 14, weight: '600' },
        bodyFont: { size: 13 }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value: any) {
            return formatCurrency(value, true);
          },
          font: { size: 12 }
        },
        grid: { color: '#f5edff' }
      },
      x: {
        grid: { display: false },
        ticks: { font: { size: 12, weight: '500' } }
      }
    }
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          font: { size: 13, weight: '500' },
          padding: 16,
          usePointStyle: true,
        }
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            return `${context.dataset.label}: ${formatCurrency(context.parsed.y)}`;
          }
        },
        backgroundColor: '#2e3138',
        padding: 12,
        titleFont: { size: 14, weight: '600' },
        bodyFont: { size: 13 }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value: any) {
            return formatCurrency(value, true);
          },
          font: { size: 12 }
        },
        grid: { color: '#f5edff' }
      },
      x: {
        grid: { display: false },
        ticks: { font: { size: 12, weight: '500' } }
      }
    }
  };

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))',
      gap: '24px'
    }}>
      {/* Evolução Mensal */}
      <div style={{
        backgroundColor: '#ffffff',
        borderRadius: '12px',
        padding: '24px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
        border: '1px solid #f5edff'
      }}>
        <h3 style={{
          fontSize: '18px',
          fontWeight: '600',
          color: '#2e3138',
          marginBottom: '24px'
        }}>
          Evolução Mensal {selectedYear}
        </h3>
        <div style={{ height: '350px' }}>
          <Line data={monthlyEvolutionData} options={lineOptions} />
        </div>
      </div>

      {/* Comparativo Eleitoral */}
      <div style={{
        backgroundColor: '#ffffff',
        borderRadius: '12px',
        padding: '24px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
        border: '1px solid #f5edff'
      }}>
        <h3 style={{
          fontSize: '18px',
          fontWeight: '600',
          color: '#2e3138',
          marginBottom: '16px'
        }}>
          Comparativo Eleitoral
        </h3>
        <div style={{
          display: 'flex',
          gap: '16px',
          marginBottom: '16px',
          fontSize: '13px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '3px',
              backgroundColor: '#ef4444'
            }} />
            <span style={{ color: '#6b7280' }}>Anos Eleitorais</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '3px',
              backgroundColor: '#3b82f6'
            }} />
            <span style={{ color: '#6b7280' }}>Anos Regulares</span>
          </div>
        </div>
        <div style={{ height: '320px' }}>
          <Bar data={electoralComparisonData} options={barOptions} />
        </div>
      </div>
    </div>
  );
};

export default TraditionalCharts;
