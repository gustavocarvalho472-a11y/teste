// Página de Demonstração - Cards de Oportunidades Comerciais

import React from 'react';
import OportunidadeCard from './components/OportunidadeCard';
import { OportunidadeData } from './types/oportunidade';
import { calcularOportunidade } from './utils/oportunidadeCalculator';

const OportunidadesPage: React.FC = () => {
  // Dados simulados realistas
  const dadosSimulados = [
    // PREMIUM - São Paulo
    calcularOportunidade({
      municipio: 'São Paulo',
      estado: 'SP',
      categoria: 'Educação',
      historico: [
        { ano: 2020, totalContratos: 4200, valorExecutado: 2850000000 },
        { ano: 2021, totalContratos: 4350, valorExecutado: 2920000000 },
        { ano: 2022, totalContratos: 4280, valorExecutado: 3080000000 },
        { ano: 2023, totalContratos: 4450, valorExecutado: 3150000000 },
        { ano: 2024, totalContratos: 4320, valorExecutado: 3100000000 }
      ],
      anoAtual: {
        fechados: 1200,
        executado: 950000000,
        editaisAtivos: {
          quantidade: 285,
          valor: 1200000000
        }
      }
    }),

    // FORTE - Rio de Janeiro
    calcularOportunidade({
      municipio: 'Rio de Janeiro',
      estado: 'RJ',
      categoria: 'Saúde',
      historico: [
        { ano: 2020, totalContratos: 3100, valorExecutado: 1850000000 },
        { ano: 2021, totalContratos: 3250, valorExecutado: 1920000000 },
        { ano: 2022, totalContratos: 3180, valorExecutado: 1980000000 },
        { ano: 2023, totalContratos: 3350, valorExecutado: 2050000000 },
        { ano: 2024, totalContratos: 3220, valorExecutado: 2000000000 }
      ],
      anoAtual: {
        fechados: 1100,
        executado: 720000000,
        editaisAtivos: {
          quantidade: 198,
          valor: 850000000
        }
      }
    }),

    // BOA - Brasília
    calcularOportunidade({
      municipio: 'Brasília',
      estado: 'DF',
      categoria: 'Infraestrutura',
      historico: [
        { ano: 2020, totalContratos: 2800, valorExecutado: 1550000000 },
        { ano: 2021, totalContratos: 2950, valorExecutado: 1620000000 },
        { ano: 2022, totalContratos: 2880, valorExecutado: 1680000000 },
        { ano: 2023, totalContratos: 3050, valorExecutado: 1750000000 },
        { ano: 2024, totalContratos: 2920, valorExecutado: 1700000000 }
      ],
      anoAtual: {
        fechados: 1150,
        executado: 650000000,
        editaisAtivos: {
          quantidade: 164,
          valor: 720000000
        }
      }
    }),

    // PREMIUM - Belo Horizonte
    calcularOportunidade({
      municipio: 'Belo Horizonte',
      estado: 'MG',
      categoria: 'Educação',
      historico: [
        { ano: 2020, totalContratos: 2200, valorExecutado: 980000000 },
        { ano: 2021, totalContratos: 2350, valorExecutado: 1020000000 },
        { ano: 2022, totalContratos: 2280, valorExecutado: 1080000000 },
        { ano: 2023, totalContratos: 2450, valorExecutado: 1150000000 },
        { ano: 2024, totalContratos: 2320, valorExecutado: 1100000000 }
      ],
      anoAtual: {
        fechados: 650,
        executado: 380000000,
        editaisAtivos: {
          quantidade: 142,
          valor: 450000000
        }
      }
    })
  ];

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#FAF8FF',
      padding: '32px'
    }}>
      {/* Header */}
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        marginBottom: '32px'
      }}>
        <h1 style={{
          fontSize: '32px',
          fontWeight: '700',
          color: '#1A1A1A',
          marginBottom: '8px'
        }}>
          💎 Oportunidades Comerciais
        </h1>
        <p style={{
          fontSize: '16px',
          color: '#6B7280',
          margin: 0
        }}>
          Municípios com orçamento disponível acima do padrão histórico
        </p>

        {/* Stats Bar */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '16px',
          marginTop: '24px'
        }}>
          <StatCard
            label="Total Oportunidades"
            value={dadosSimulados.length.toString()}
            color="#10b981"
          />
          <StatCard
            label="Premium"
            value={dadosSimulados.filter(d => d.nivel === 'PREMIUM').length.toString()}
            color="#10b981"
          />
          <StatCard
            label="Forte"
            value={dadosSimulados.filter(d => d.nivel === 'FORTE').length.toString()}
            color="#3b82f6"
          />
          <StatCard
            label="Boa"
            value={dadosSimulados.filter(d => d.nivel === 'BOA').length.toString()}
            color="#7c3aed"
          />
        </div>
      </div>

      {/* Grid de Cards */}
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(600px, 1fr))',
        gap: '32px'
      }}>
        {dadosSimulados.map((opp, i) => (
          <OportunidadeCard key={i} data={opp} />
        ))}
      </div>

      {/* Footer */}
      <div style={{
        maxWidth: '1400px',
        margin: '48px auto 0',
        padding: '24px',
        textAlign: 'center',
        color: '#6B7280',
        fontSize: '14px',
        borderTop: '1px solid #E5E7EB'
      }}>
        <p style={{ margin: 0 }}>
          Dashboard de Oportunidades Comerciais · Análise de Licitações Municipais
        </p>
      </div>
    </div>
  );
};

const StatCard: React.FC<{ label: string; value: string; color: string }> = ({ label, value, color }) => (
  <div style={{
    backgroundColor: '#FFFFFF',
    padding: '20px',
    borderRadius: '12px',
    border: '2px solid #E5E7EB',
    textAlign: 'center'
  }}>
    <div style={{
      fontSize: '11px',
      fontWeight: '700',
      color: '#6B7280',
      textTransform: 'uppercase',
      marginBottom: '8px'
    }}>
      {label}
    </div>
    <div style={{
      fontSize: '32px',
      fontWeight: '700',
      color: color
    }}>
      {value}
    </div>
  </div>
);

export default OportunidadesPage;
