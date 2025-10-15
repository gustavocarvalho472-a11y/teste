import React, { useState } from 'react';

interface RegionData {
  name: string;
  value: number;
  deviation: number;
  states: string[];
}

interface BrazilMapProps {
  regionData: RegionData[];
  onRegionClick?: (region: string) => void;
}

const BrazilMap: React.FC<BrazilMapProps> = ({ regionData, onRegionClick }) => {
  const [hoveredRegion, setHoveredRegion] = useState<string | null>(null);

  // Calcula cor baseada no desvio (heatmap)
  const getColor = (deviation: number): string => {
    if (deviation < -20) return '#dc2626'; // Vermelho escuro
    if (deviation < -10) return '#ef4444'; // Vermelho
    if (deviation < -5) return '#f87171'; // Vermelho claro
    if (deviation < 5) return '#60a5fa'; // Azul claro
    if (deviation < 10) return '#3b82f6'; // Azul
    if (deviation < 20) return '#2563eb'; // Azul escuro
    return '#1e40af'; // Azul muito escuro
  };

  const regions = [
    {
      id: 'norte',
      name: 'Norte',
      path: 'M180,50 L250,50 L280,120 L260,180 L200,160 L150,120 Z',
      textX: 210,
      textY: 110
    },
    {
      id: 'nordeste',
      name: 'Nordeste',
      path: 'M280,120 L380,100 L420,150 L400,200 L340,220 L300,200 L260,180 Z',
      textX: 340,
      textY: 160
    },
    {
      id: 'centro-oeste',
      name: 'Centro-Oeste',
      path: 'M200,160 L260,180 L300,200 L280,280 L200,300 L150,240 Z',
      textX: 230,
      textY: 230
    },
    {
      id: 'sudeste',
      name: 'Sudeste',
      path: 'M280,280 L340,260 L380,300 L360,360 L300,340 Z',
      textX: 330,
      textY: 300
    },
    {
      id: 'sul',
      name: 'Sul',
      path: 'M280,340 L320,360 L300,420 L240,420 L220,380 Z',
      textX: 270,
      textY: 380
    }
  ];

  const getRegionData = (regionName: string) => {
    return regionData.find(r => r.name.toLowerCase() === regionName.toLowerCase());
  };

  return (
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
        marginBottom: '8px'
      }}>
        🗺️ Análise Regional
      </h3>
      <p style={{
        fontSize: '13px',
        color: '#6b7280',
        marginBottom: '24px'
      }}>
        Heatmap de subexecução por região do Brasil
      </p>

      <div style={{ display: 'flex', gap: '24px', alignItems: 'flex-start' }}>
        {/* Mapa SVG */}
        <div style={{ flex: '1 1 400px' }}>
          <svg viewBox="0 0 500 500" style={{ width: '100%', height: 'auto', maxWidth: '400px' }}>
            {regions.map(region => {
              const data = getRegionData(region.name);
              const isHovered = hoveredRegion === region.id;

              return (
                <g key={region.id}>
                  <path
                    d={region.path}
                    fill={data ? getColor(data.deviation) : '#e5e7eb'}
                    stroke={isHovered ? '#9755fe' : '#ffffff'}
                    strokeWidth={isHovered ? 4 : 2}
                    style={{
                      cursor: 'pointer',
                      transition: 'all 0.3s',
                      filter: isHovered ? 'brightness(1.1)' : 'none'
                    }}
                    onMouseEnter={() => setHoveredRegion(region.id)}
                    onMouseLeave={() => setHoveredRegion(null)}
                    onClick={() => onRegionClick && onRegionClick(region.name)}
                  />
                  <text
                    x={region.textX}
                    y={region.textY}
                    textAnchor="middle"
                    fill="#ffffff"
                    fontSize="14"
                    fontWeight="700"
                    style={{
                      pointerEvents: 'none',
                      textShadow: '1px 1px 2px rgba(0,0,0,0.5)'
                    }}
                  >
                    {region.name.split('-')[0]}
                  </text>
                </g>
              );
            })}
          </svg>

          {/* Legenda */}
          <div style={{
            marginTop: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '11px',
            color: '#6b7280'
          }}>
            <span style={{ fontWeight: '600' }}>Legenda:</span>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}>
              <div style={{
                width: '20px',
                height: '12px',
                background: 'linear-gradient(to right, #dc2626, #f87171, #60a5fa, #2563eb, #1e40af)',
                borderRadius: '2px'
              }} />
              <span>Corte ← | → Aumento</span>
            </div>
          </div>
        </div>

        {/* Dados Regionais */}
        <div style={{ flex: '1 1 300px' }}>
          {regionData.map(region => (
            <div
              key={region.name}
              style={{
                padding: '16px',
                marginBottom: '12px',
                backgroundColor: '#f9f4ff',
                borderRadius: '8px',
                border: '1px solid #e1cdfe',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={() => setHoveredRegion(region.name.toLowerCase().replace(/-/g, ''))}
              onMouseLeave={() => setHoveredRegion(null)}
              onClick={() => onRegionClick && onRegionClick(region.name)}
            >
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '8px'
              }}>
                <span style={{
                  fontSize: '14px',
                  fontWeight: '600',
                  color: '#2e3138'
                }}>
                  {region.name}
                </span>
                <span style={{
                  fontSize: '16px',
                  fontWeight: '700',
                  color: region.deviation < 0 ? '#ef4444' : '#10b981'
                }}>
                  {region.deviation >= 0 ? '+' : ''}{region.deviation.toFixed(1)}%
                </span>
              </div>
              <div style={{
                fontSize: '12px',
                color: '#6b7280',
                marginBottom: '8px'
              }}>
                Estados: {region.states.join(', ')}
              </div>
              <div style={{
                fontSize: '13px',
                fontWeight: '600',
                color: '#5219a1'
              }}>
                {new Intl.NumberFormat('pt-BR', {
                  style: 'currency',
                  currency: 'BRL',
                  notation: 'compact',
                  maximumFractionDigits: 1
                }).format(region.value)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default BrazilMap;
