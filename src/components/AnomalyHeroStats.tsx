import React from 'react';

interface AnomalyHeroStatsProps {
  totalAnomalies: number;
  criticalCount: number;
  moderateCount: number;
  electionPattern: number;
  maxAnomaly: number;
}

const AnomalyHeroStats: React.FC<AnomalyHeroStatsProps> = ({
  totalAnomalies,
  criticalCount,
  moderateCount,
  electionPattern,
  maxAnomaly
}) => {
  return (
    <div style={{
      backgroundColor: '#2e3138',
      borderRadius: '16px',
      padding: '32px',
      marginBottom: '32px',
      boxShadow: '0 4px 16px rgba(0, 0, 0, 0.15)',
      background: 'linear-gradient(135deg, #2e3138 0%, #3f127d 100%)'
    }}>
      {/* Título Principal */}
      <div style={{
        textAlign: 'center',
        marginBottom: '32px'
      }}>
        <div style={{
          fontSize: '14px',
          fontWeight: '600',
          color: '#d1b3ff',
          textTransform: 'uppercase',
          letterSpacing: '1px',
          marginBottom: '8px'
        }}>
          Análise Estatística Automática
        </div>
        <h2 style={{
          fontSize: '32px',
          fontWeight: '700',
          color: '#ffffff',
          margin: 0,
          lineHeight: '1.2'
        }}>
          🚨 Anomalias Detectadas no Orçamento de Educação
        </h2>
        <p style={{
          fontSize: '15px',
          color: '#ba90fc',
          marginTop: '12px',
          margin: 0
        }}>
          Período analisado: 2015-2024 · Baseado em análise de desvio padrão (σ)
        </p>
      </div>

      {/* Grid de Métricas */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '20px'
      }}>
        {/* Total de Anomalias */}
        <div style={{
          backgroundColor: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '12px',
          padding: '20px',
          border: '1px solid rgba(255, 255, 255, 0.15)',
          backdropFilter: 'blur(10px)',
          transition: 'all 0.3s'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.15)';
          e.currentTarget.style.transform = 'translateY(-4px)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
          e.currentTarget.style.transform = 'translateY(0)';
        }}
        >
          <div style={{
            fontSize: '12px',
            fontWeight: '600',
            color: '#d1b3ff',
            marginBottom: '8px',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            Total de Anomalias
          </div>
          <div style={{
            fontSize: '40px',
            fontWeight: '700',
            color: '#ffffff',
            marginBottom: '4px',
            lineHeight: '1'
          }}>
            {totalAnomalies}
          </div>
          <div style={{
            fontSize: '13px',
            color: '#ba90fc'
          }}>
            Anos com desvio &gt;2σ
          </div>
        </div>

        {/* Anomalias Críticas */}
        <div style={{
          backgroundColor: 'rgba(239, 68, 68, 0.15)',
          borderRadius: '12px',
          padding: '20px',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          backdropFilter: 'blur(10px)',
          transition: 'all 0.3s'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = 'rgba(239, 68, 68, 0.2)';
          e.currentTarget.style.transform = 'translateY(-4px)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'rgba(239, 68, 68, 0.15)';
          e.currentTarget.style.transform = 'translateY(0)';
        }}
        >
          <div style={{
            fontSize: '12px',
            fontWeight: '600',
            color: '#fca5a5',
            marginBottom: '8px',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            🔴 Críticas
          </div>
          <div style={{
            fontSize: '40px',
            fontWeight: '700',
            color: '#ffffff',
            marginBottom: '4px',
            lineHeight: '1'
          }}>
            {criticalCount}
          </div>
          <div style={{
            fontSize: '13px',
            color: '#fca5a5'
          }}>
            Desvio &gt;3σ
          </div>
        </div>

        {/* Anomalias Moderadas */}
        <div style={{
          backgroundColor: 'rgba(245, 158, 11, 0.15)',
          borderRadius: '12px',
          padding: '20px',
          border: '1px solid rgba(245, 158, 11, 0.3)',
          backdropFilter: 'blur(10px)',
          transition: 'all 0.3s'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = 'rgba(245, 158, 11, 0.2)';
          e.currentTarget.style.transform = 'translateY(-4px)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'rgba(245, 158, 11, 0.15)';
          e.currentTarget.style.transform = 'translateY(0)';
        }}
        >
          <div style={{
            fontSize: '12px',
            fontWeight: '600',
            color: '#fcd34d',
            marginBottom: '8px',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            🟡 Moderadas
          </div>
          <div style={{
            fontSize: '40px',
            fontWeight: '700',
            color: '#ffffff',
            marginBottom: '4px',
            lineHeight: '1'
          }}>
            {moderateCount}
          </div>
          <div style={{
            fontSize: '13px',
            color: '#fcd34d'
          }}>
            Desvio 2-3σ
          </div>
        </div>

        {/* Padrão Eleitoral */}
        <div style={{
          backgroundColor: 'rgba(151, 85, 254, 0.15)',
          borderRadius: '12px',
          padding: '20px',
          border: '1px solid rgba(151, 85, 254, 0.3)',
          backdropFilter: 'blur(10px)',
          transition: 'all 0.3s'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = 'rgba(151, 85, 254, 0.2)';
          e.currentTarget.style.transform = 'translateY(-4px)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'rgba(151, 85, 254, 0.15)';
          e.currentTarget.style.transform = 'translateY(0)';
        }}
        >
          <div style={{
            fontSize: '12px',
            fontWeight: '600',
            color: '#d1b3ff',
            marginBottom: '8px',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            🗳️ Padrão Eleitoral
          </div>
          <div style={{
            fontSize: '40px',
            fontWeight: '700',
            color: '#ffffff',
            marginBottom: '4px',
            lineHeight: '1'
          }}>
            {electionPattern >= 0 ? '+' : ''}{electionPattern.toFixed(1)}%
          </div>
          <div style={{
            fontSize: '13px',
            color: '#d1b3ff'
          }}>
            vs anos regulares
          </div>
        </div>

        {/* Maior Anomalia */}
        <div style={{
          backgroundColor: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '12px',
          padding: '20px',
          border: '1px solid rgba(255, 255, 255, 0.15)',
          backdropFilter: 'blur(10px)',
          transition: 'all 0.3s'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.15)';
          e.currentTarget.style.transform = 'translateY(-4px)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
          e.currentTarget.style.transform = 'translateY(0)';
        }}
        >
          <div style={{
            fontSize: '12px',
            fontWeight: '600',
            color: '#d1b3ff',
            marginBottom: '8px',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            📊 Maior Anomalia
          </div>
          <div style={{
            fontSize: '40px',
            fontWeight: '700',
            color: '#ffffff',
            marginBottom: '4px',
            lineHeight: '1'
          }}>
            {maxAnomaly.toFixed(1)}σ
          </div>
          <div style={{
            fontSize: '13px',
            color: '#d1b3ff'
          }}>
            Desvio máximo registrado
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnomalyHeroStats;
