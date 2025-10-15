import React, { useMemo } from 'react';
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
  ChartOptions
} from 'chart.js';
import { Scatter } from 'react-chartjs-2';
import { Cluster } from '../utils/clustering';

ChartJS.register(LinearScale, PointElement, Tooltip, Legend);

interface ClusterScatterChartProps {
  clusters: Cluster[];
}

const ClusterScatterChart: React.FC<ClusterScatterChartProps> = ({ clusters }) => {
  const chartData = useMemo(() => {
    return {
      datasets: clusters.map(cluster => ({
        label: `${cluster.name} (${cluster.points.length})`,
        data: cluster.points.map(p => ({
          x: p.year,
          y: p.deviation
        })),
        backgroundColor: cluster.color,
        pointRadius: 8,
        pointHoverRadius: 12,
        pointBorderWidth: 2,
        pointBorderColor: '#ffffff'
      }))
    };
  }, [clusters]);

  const options: ChartOptions<'scatter'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          font: {
            size: 13,
            weight: '600'
          },
          padding: 16,
          usePointStyle: true,
          pointStyle: 'circle'
        }
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const point = clusters
              .flatMap(c => c.points)
              .find(p => p.year === context.parsed.x && Math.abs(p.deviation - context.parsed.y) < 0.1);

            if (!point) return '';

            return [
              `Ano: ${point.year}${point.isElectionYear ? ' 🗳️' : ''}`,
              `Desvio: ${point.deviation.toFixed(1)}%`,
              `Execução: ${point.executionRate.toFixed(1)}%`
            ];
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
        type: 'linear',
        title: {
          display: true,
          text: 'Ano',
          font: {
            size: 14,
            weight: '600'
          },
          color: '#2e3138'
        },
        ticks: {
          stepSize: 1,
          font: { size: 12 },
          color: '#6b7280'
        },
        grid: {
          color: '#f5edff'
        }
      },
      y: {
        title: {
          display: true,
          text: 'Desvio Orçamentário (%)',
          font: {
            size: 14,
            weight: '600'
          },
          color: '#2e3138'
        },
        ticks: {
          font: { size: 12 },
          color: '#6b7280',
          callback: function(value) {
            return `${value}%`;
          }
        },
        grid: {
          color: '#f5edff'
        }
      }
    }
  };

  return (
    <div style={{
      backgroundColor: '#ffffff',
      borderRadius: '12px',
      padding: '24px',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
      border: '1px solid #f5edff'
    }}>
      <div style={{
        marginBottom: '20px'
      }}>
        <h3 style={{
          fontSize: '18px',
          fontWeight: '600',
          color: '#2e3138',
          marginBottom: '8px'
        }}>
          📊 Análise de Clusters (K-means)
        </h3>
        <p style={{
          fontSize: '13px',
          color: '#6b7280',
          marginBottom: '16px'
        }}>
          Agrupamento automático de anos por padrão de comportamento orçamentário
        </p>

        {/* Descrição dos Clusters */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '12px',
          marginBottom: '20px'
        }}>
          {clusters.map(cluster => (
            <div
              key={cluster.id}
              style={{
                padding: '12px',
                backgroundColor: `${cluster.color}15`,
                border: `2px solid ${cluster.color}`,
                borderRadius: '8px'
              }}
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                marginBottom: '6px'
              }}>
                <div style={{
                  width: '12px',
                  height: '12px',
                  borderRadius: '50%',
                  backgroundColor: cluster.color
                }} />
                <span style={{
                  fontSize: '14px',
                  fontWeight: '700',
                  color: '#2e3138'
                }}>
                  {cluster.name}
                </span>
              </div>
              <div style={{
                fontSize: '12px',
                color: '#6b7280',
                lineHeight: '1.5'
              }}>
                {cluster.description}
              </div>
              <div style={{
                fontSize: '11px',
                color: '#9755fe',
                marginTop: '6px',
                fontWeight: '600'
              }}>
                {cluster.points.length} ano{cluster.points.length !== 1 ? 's' : ''}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Gráfico */}
      <div style={{ height: '450px' }}>
        <Scatter data={chartData} options={options} />
      </div>

      {/* Linha de referência */}
      <div style={{
        marginTop: '16px',
        padding: '12px',
        backgroundColor: '#f9f4ff',
        borderRadius: '6px',
        fontSize: '12px',
        color: '#5219a1',
        textAlign: 'center'
      }}>
        <strong>Linha base (0%)</strong>: Representa a média histórica do orçamento
      </div>
    </div>
  );
};

export default ClusterScatterChart;
