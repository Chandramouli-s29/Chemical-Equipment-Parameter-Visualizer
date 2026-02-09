import { useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
} from 'chart.js';
import { Bar, Pie, Line } from 'react-chartjs-2';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { BarChart3, PieChart, Activity } from 'lucide-react';
import type { ChartData } from '@/lib/api';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement
);

interface ChartsViewProps {
  chartData: ChartData;
}

export function ChartsView({ chartData }: ChartsViewProps) {
  const colors = useMemo(() => [
    'rgba(59, 130, 246, 0.8)',   // Blue
    'rgba(16, 185, 129, 0.8)',   // Green
    'rgba(249, 115, 22, 0.8)',   // Orange
    'rgba(239, 68, 68, 0.8)',    // Red
    'rgba(139, 92, 246, 0.8)',   // Purple
    'rgba(236, 72, 153, 0.8)',   // Pink
    'rgba(14, 165, 233, 0.8)',   // Sky
    'rgba(245, 158, 11, 0.8)',   // Amber
  ], []);

  const borderColors = useMemo(() => [
    'rgb(59, 130, 246)',
    'rgb(16, 185, 129)',
    'rgb(249, 115, 22)',
    'rgb(239, 68, 68)',
    'rgb(139, 92, 246)',
    'rgb(236, 72, 153)',
    'rgb(14, 165, 233)',
    'rgb(245, 158, 11)',
  ], []);

  // Type Distribution Pie Chart
  const typeDistributionData = useMemo(() => {
    const labels = Object.keys(chartData.type_distribution);
    const data = Object.values(chartData.type_distribution);
    
    return {
      labels,
      datasets: [
        {
          data,
          backgroundColor: colors.slice(0, labels.length),
          borderColor: borderColors.slice(0, labels.length),
          borderWidth: 2,
        },
      ],
    };
  }, [chartData.type_distribution, colors, borderColors]);

  // Average Parameters by Type Bar Chart
  const avgParametersData = useMemo(() => {
    const labels = chartData.labels;
    
    return {
      labels,
      datasets: [
        {
          label: 'Avg Flowrate',
          data: labels.map(type => chartData.avg_flowrate_by_type[type] || 0),
          backgroundColor: 'rgba(59, 130, 246, 0.8)',
          borderColor: 'rgb(59, 130, 246)',
          borderWidth: 1,
        },
        {
          label: 'Avg Pressure',
          data: labels.map(type => chartData.avg_pressure_by_type[type] || 0),
          backgroundColor: 'rgba(249, 115, 22, 0.8)',
          borderColor: 'rgb(249, 115, 22)',
          borderWidth: 1,
        },
        {
          label: 'Avg Temperature',
          data: labels.map(type => chartData.avg_temperature_by_type[type] || 0),
          backgroundColor: 'rgba(239, 68, 68, 0.8)',
          borderColor: 'rgb(239, 68, 68)',
          borderWidth: 1,
        },
      ],
    };
  }, [chartData]);

  // Equipment Count by Type
  const countByTypeData = useMemo(() => {
    return {
      labels: chartData.labels,
      datasets: [
        {
          label: 'Equipment Count',
          data: chartData.type_counts,
          backgroundColor: 'rgba(16, 185, 129, 0.8)',
          borderColor: 'rgb(16, 185, 129)',
          borderWidth: 2,
          fill: true,
        },
      ],
    };
  }, [chartData]);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      // hide built-in legend for pie; we'll render an external legend in React
      legend: {
        position: 'bottom' as const,
        display: true,
        labels: {
          padding: 15,
          font: {
            size: 12,
          },
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        cornerRadius: 8,
      },
      // ensure data labels plugin does not create overlapping annotations
      datalabels: {
        display: false,
      },
    },
  };

  const barOptions = {
    ...chartOptions,
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
      },
      x: {
        grid: {
          display: false,
        },
      },
    },
  };

  return (
    <Tabs defaultValue="distribution" className="space-y-6">
      <TabsList className="grid w-full grid-cols-3 lg:w-[400px]">
        <TabsTrigger value="distribution" className="flex items-center gap-2">
          <PieChart className="h-4 w-4" />
          Distribution
        </TabsTrigger>
        <TabsTrigger value="averages" className="flex items-center gap-2">
          <BarChart3 className="h-4 w-4" />
          Averages
        </TabsTrigger>
        <TabsTrigger value="counts" className="flex items-center gap-2">
          <Activity className="h-4 w-4" />
          Counts
        </TabsTrigger>
      </TabsList>

      <TabsContent value="distribution">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChart className="h-5 w-5 text-blue-500" />
              Equipment Type Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
                {(() => {
                  const labels = typeDistributionData.labels || [];
                  const maxContainerWidth = 980;
                  const pieMaxSize = 560; // cap pie size
                  const pieOptions = {
                    ...chartOptions,
                    maintainAspectRatio: false,
                    plugins: { ...chartOptions.plugins, legend: { display: false } },
                  };

                  return (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', maxWidth: maxContainerWidth, margin: '0 auto', gap: 12 }}>
                      <div style={{ width: '100%', display: 'flex', justifyContent: 'center' }}>
                        <div style={{ width: '100%', maxWidth: pieMaxSize, height: pieMaxSize, boxSizing: 'border-box' }}>
                          <Pie data={typeDistributionData} options={pieOptions} />
                        </div>
                      </div>

                      {/* Legend area: fixed height and scrollable to avoid pushing content */}
                      <div style={{ width: '100%', maxWidth: maxContainerWidth, maxHeight: 220, overflowY: 'auto', padding: '8px 12px' }}>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px 24px', justifyContent: 'center' }}>
                          {typeDistributionData.labels && typeDistributionData.labels.map((lab: any, idx: number) => (
                            <div key={String(lab) + idx} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '6px 10px', borderRadius: 8 }}>
                              <span style={{ width: 28, height: 14, borderRadius: 6, background: (typeDistributionData.datasets && typeDistributionData.datasets[0].backgroundColor && typeDistributionData.datasets[0].backgroundColor[idx]) || '#ddd', boxShadow: 'inset 0 0 0 2px rgba(0,0,0,0.06)' }} />
                              <span style={{ fontSize: 14, color: '#111827' }}>{lab}</span>
                              <span style={{ fontSize: 13, color: '#374151' }}>{ (typeDistributionData.datasets && typeDistributionData.datasets[0].data && typeDistributionData.datasets[0].data[idx] !== undefined) ? ` — ${typeDistributionData.datasets[0].data[idx]}` : '' }</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  );
                })()}
          </CardContent>
        </Card>
      </TabsContent>

      <TabsContent value="averages">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-blue-500" />
              Average Parameters by Equipment Type
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[350px]">
              <Bar data={avgParametersData} options={barOptions} />
            </div>
          </CardContent>
        </Card>
      </TabsContent>

      <TabsContent value="counts">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-blue-500" />
              Equipment Count by Type
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[350px]">
              <Line 
                data={countByTypeData} 
                options={{
                  ...barOptions,
                  elements: {
                    line: {
                      tension: 0.4,
                    },
                  },
                }} 
              />
            </div>
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>
  );
}
