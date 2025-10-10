import React, { useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { BudgetData, IndicatorType } from '../types';
import { formatCurrency, getMonthShortName } from '../utils';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface ComparisonChartProps {
  currentData: BudgetData[];
  comparisonData: BudgetData[];
  indicator: IndicatorType;
  selectedMonths: number[];
  onIndicatorChange: (indicator: IndicatorType) => void;
  onMonthToggle: (month: number) => void;
  currentLabel: string;
  comparisonLabel: string;
}

const ComparisonChart: React.FC<ComparisonChartProps> = ({
  currentData,
  comparisonData,
  indicator,
  selectedMonths,
  onIndicatorChange,
  onMonthToggle,
  currentLabel,
  comparisonLabel
}) => {
  const getValueByIndicator = (data: BudgetData): number => {
    switch (indicator) {
      case 'total-budget':
        return data.planned;
      case 'executed':
        return data.executed;
      case 'available':
        return data.available;
      default:
        return data.planned;
    }
  };

  const chartData = useMemo(() => {
    const labels = selectedMonths.map(m => getMonthShortName(m));

    const currentValues = selectedMonths.map(month => {
      const data = currentData.find(d => d.month === month);
      return data ? getValueByIndicator(data) : 0;
    });

    const comparisonValues = selectedMonths.map(month => {
      const data = comparisonData.find(d => d.month === month);
      return data ? getValueByIndicator(data) : 0;
    });

    return {
      labels,
      datasets: [
        {
          label: currentLabel,
          data: currentValues,
          backgroundColor: '#9755fe',
          borderRadius: 6,
        },
        {
          label: comparisonLabel,
          data: comparisonValues,
          backgroundColor: '#d1b3ff',
          borderRadius: 6,
        }
      ]
    };
  }, [currentData, comparisonData, selectedMonths, indicator, currentLabel, comparisonLabel]);

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
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
            return `${context.dataset.label}: ${formatCurrency(context.parsed.y)}`;
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
            return formatCurrency(value, true);
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

  const indicators = [
    { value: 'total-budget' as IndicatorType, label: 'Orçamento Total' },
    { value: 'executed' as IndicatorType, label: 'Gasto' },
    { value: 'available' as IndicatorType, label: 'Disponível' }
  ];

  const months = Array.from({ length: 12 }, (_, i) => i + 1);

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
          Comparação Dinâmica
        </h3>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
          {/* Dropdown Indicador */}
          <select
            value={indicator}
            onChange={(e) => onIndicatorChange(e.target.value as IndicatorType)}
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
            {indicators.map(ind => (
              <option key={ind.value} value={ind.value}>
                {ind.label}
              </option>
            ))}
          </select>

          {/* Contador de meses */}
          <span style={{
            padding: '8px 12px',
            borderRadius: '6px',
            backgroundColor: '#f5edff',
            color: '#5219a1',
            fontSize: '13px',
            fontWeight: '600'
          }}>
            Meses ({selectedMonths.length})
          </span>
        </div>
      </div>

      {/* Grid de seleção de meses */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(70px, 1fr))',
        gap: '8px',
        marginBottom: '24px'
      }}>
        {months.map(month => (
          <button
            key={month}
            onClick={() => onMonthToggle(month)}
            style={{
              padding: '8px',
              borderRadius: '6px',
              border: selectedMonths.includes(month) ? '2px solid #9755fe' : '1px solid #e1cdfe',
              backgroundColor: selectedMonths.includes(month) ? '#f5edff' : '#ffffff',
              color: selectedMonths.includes(month) ? '#3f127d' : '#6b7280',
              fontSize: '12px',
              fontWeight: selectedMonths.includes(month) ? '600' : '400',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
          >
            {getMonthShortName(month)}
          </button>
        ))}
      </div>

      {/* Gráfico */}
      <div style={{ height: '400px' }}>
        <Bar data={chartData} options={options} />
      </div>

      {/* Resumo */}
      <div style={{
        marginTop: '24px',
        padding: '16px',
        backgroundColor: '#f9f4ff',
        borderRadius: '8px',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px'
      }}>
        <div>
          <div style={{ fontSize: '12px', color: '#5219a1', fontWeight: '600', marginBottom: '4px' }}>
            Total {currentLabel}
          </div>
          <div style={{ fontSize: '16px', fontWeight: '700', color: '#2e3138' }}>
            {formatCurrency(chartData.datasets[0].data.reduce((a, b) => a + b, 0))}
          </div>
        </div>
        <div>
          <div style={{ fontSize: '12px', color: '#5219a1', fontWeight: '600', marginBottom: '4px' }}>
            Total {comparisonLabel}
          </div>
          <div style={{ fontSize: '16px', fontWeight: '700', color: '#2e3138' }}>
            {formatCurrency(chartData.datasets[1].data.reduce((a, b) => a + b, 0))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComparisonChart;
