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

interface Municipality {
  id: string;
  name: string;
  [key: string]: any;
}

interface ComparisonChartProps {
  currentData: BudgetData[];
  comparisonData: BudgetData[];
  indicator: IndicatorType;
  selectedMonths: number[];
  onIndicatorChange: (indicator: IndicatorType) => void;
  onMonthToggle: (month: number) => void;
  currentLabel: string;
  comparisonLabel: string;
  currentPeriod: number;
  comparisonPeriod: string;
  onCurrentPeriodChange: (period: number) => void;
  onComparisonPeriodChange: (period: string) => void;
  selectedMunicipality: string;
  onMunicipalityChange: (municipality: string) => void;
  municipalities: Municipality[];
}

const ComparisonChart: React.FC<ComparisonChartProps> = ({
  currentData,
  comparisonData,
  indicator,
  selectedMonths,
  onIndicatorChange,
  onMonthToggle,
  currentLabel,
  comparisonLabel,
  currentPeriod,
  comparisonPeriod,
  onCurrentPeriodChange,
  onComparisonPeriodChange,
  selectedMunicipality,
  onMunicipalityChange,
  municipalities
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
          backgroundColor: 'rgba(124, 58, 237, 0.7)',
          borderRadius: 8,
          borderWidth: 0,
        },
        {
          label: comparisonLabel,
          data: comparisonValues,
          backgroundColor: 'rgba(196, 181, 253, 0.6)',
          borderRadius: 8,
          borderWidth: 0,
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
          color: 'rgba(124, 58, 237, 0.08)',
          lineWidth: 1
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
      border: '1px solid rgba(124, 58, 237, 0.1)'
    }}>
      {/* Cabeçalho com título e subtítulo */}
      <div style={{
        marginBottom: '20px'
      }}>
        <h3 style={{
          fontSize: '24px',
          fontWeight: '700',
          color: '#2e3138',
          margin: 0,
          marginBottom: '4px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <span className="material-icons" style={{ fontSize: '24px', color: '#6941C6' }}>show_chart</span>
          <span>Comparação Dinâmica</span>
        </h3>
        <p style={{
          fontSize: '14px',
          color: '#6b7280',
          margin: 0
        }}>
          Selecione um município e compare períodos
        </p>
      </div>

      {/* Controles */}
      <div style={{
        display: 'flex',
        justifyContent: 'flex-end',
        alignItems: 'center',
        marginBottom: '24px',
        flexWrap: 'wrap',
        gap: '12px'
      }}>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
          {/* Dropdown Município */}
          <select
            value={selectedMunicipality}
            onChange={(e) => onMunicipalityChange(e.target.value)}
            style={{
              padding: '8px 16px',
              borderRadius: '8px',
              border: '1px solid rgba(124, 58, 237, 0.2)',
              backgroundColor: '#ffffff',
              color: '#2e3138',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer',
              outline: 'none',
              minWidth: '180px'
            }}
          >
            {municipalities.map(m => (
              <option key={m.id} value={m.name}>{m.name}</option>
            ))}
          </select>

          {/* Dropdown Período Atual */}
          <select
            value={currentPeriod}
            onChange={(e) => onCurrentPeriodChange(Number(e.target.value))}
            style={{
              padding: '8px 16px',
              borderRadius: '8px',
              border: '1px solid rgba(124, 58, 237, 0.2)',
              backgroundColor: '#ffffff',
              color: '#2e3138',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer',
              outline: 'none'
            }}
          >
            <option value={2025}>2025</option>
            <option value={2024}>2024</option>
            <option value={2023}>2023</option>
          </select>

          {/* Dropdown Comparar com */}
          <select
            value={comparisonPeriod}
            onChange={(e) => onComparisonPeriodChange(e.target.value)}
            style={{
              padding: '8px 16px',
              borderRadius: '8px',
              border: '1px solid rgba(124, 58, 237, 0.2)',
              backgroundColor: '#ffffff',
              color: '#2e3138',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer',
              outline: 'none'
            }}
          >
            <option value="avg-2022-2024">Média 2022-2024</option>
            <option value="2024">2024 🗳️</option>
            <option value="2023">2023</option>
            <option value="2022">2022</option>
            <option value="avg-election">Média Anos Eleitorais</option>
          </select>

          {/* Dropdown Indicador */}
          <select
            value={indicator}
            onChange={(e) => onIndicatorChange(e.target.value as IndicatorType)}
            style={{
              padding: '8px 16px',
              borderRadius: '8px',
              border: '1px solid rgba(124, 58, 237, 0.2)',
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
            borderRadius: '8px',
            backgroundColor: 'rgba(124, 58, 237, 0.1)',
            color: '#7C3AED',
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
              borderRadius: '8px',
              border: selectedMonths.includes(month) ? '1.5px solid rgba(124, 58, 237, 0.5)' : '1px solid rgba(124, 58, 237, 0.15)',
              backgroundColor: selectedMonths.includes(month) ? 'rgba(124, 58, 237, 0.08)' : '#ffffff',
              color: selectedMonths.includes(month) ? '#7C3AED' : '#6b7280',
              fontSize: '12px',
              fontWeight: selectedMonths.includes(month) ? '600' : '500',
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
