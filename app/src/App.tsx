import { useState, useEffect } from 'react';
import { Toaster, toast } from 'sonner';
import { 
  Upload, 
  FileText, 
  BarChart3, 
  History, 
  LogOut, 
  Download,
  Activity,
  Thermometer,
  Gauge,
  Droplets
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { LoginForm } from '@/components/LoginForm';
import { FileUpload } from '@/components/FileUpload';
import { DataTable } from '@/components/DataTable';
import { ChartsView } from '@/components/ChartsView';
import { HistoryView } from '@/components/HistoryView';
import { api } from '@/lib/api';
import type { Dataset, SummaryData, ChartData } from '@/lib/api';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [currentDatasetId, setCurrentDatasetId] = useState<number | null>(null);
  const [currentDatasetName, setCurrentDatasetName] = useState<string>('');
  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [activeTab, setActiveTab] = useState('upload');

  // Check if user is already authenticated
  useEffect(() => {
    const auth = localStorage.getItem('auth');
    if (auth) {
      setIsAuthenticated(true);
      fetchDatasets();
    }
  }, []);

  const handleLogin = async (username: string, password: string) => {
    setIsLoading(true);
    try {
      const success = await api.login(username, password);
      if (success) {
        setIsAuthenticated(true);
        localStorage.setItem('auth', btoa(`${username}:${password}`));
        toast.success('Login successful!');
        fetchDatasets();
      } else {
        toast.error('Invalid credentials');
      }
    } catch (error) {
      toast.error('Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('auth');
    setIsAuthenticated(false);
    setCurrentDatasetId(null);
    setCurrentDatasetName('');
    setSummary(null);
    setChartData(null);
    toast.info('Logged out');
  };

  const fetchDatasets = async () => {
    try {
      const data = await api.getDatasets();
      setDatasets(data);
    } catch (error) {
      toast.error('Failed to fetch datasets');
    }
  };

  const handleFileUpload = async (file: File, name: string) => {
    setIsLoading(true);
    try {
      const result = await api.uploadCSV(file, name);
      toast.success('File uploaded successfully!');
      setCurrentDatasetId(result.dataset_id);
      setCurrentDatasetName(name);
      setSummary(result.summary);
      fetchDatasets();
      
      // Fetch chart data for the new dataset
      const chartDataResult = await api.getChartData(result.dataset_id);
      setChartData(chartDataResult);
      
      setActiveTab('data');
    } catch (error) {
      toast.error('Upload failed: ' + (error as Error).message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDatasetSelect = async (dataset: Dataset) => {
    setIsLoading(true);
    try {
      setCurrentDatasetId(dataset.id);
      setCurrentDatasetName(dataset.name);
      
      // Fetch summary
      const summaryData = await api.getSummary(dataset.id);
      setSummary(summaryData);
      
      // Fetch chart data
      const chartDataResult = await api.getChartData(dataset.id);
      setChartData(chartDataResult);
      
      setActiveTab('data');
    } catch (error) {
      toast.error('Failed to load dataset');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!currentDatasetId) return;
    
    setIsLoading(true);
    try {
      await api.downloadPDF(currentDatasetId, currentDatasetName);
      toast.success('PDF downloaded!');
    } catch (error) {
      toast.error('Failed to download PDF');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
        <LoginForm onLogin={handleLogin} isLoading={isLoading} />
        <Toaster position="top-center" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-slate-900 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-blue-500 p-2 rounded-lg">
                <Activity className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold">Chemical Equipment Visualizer</h1>
                <p className="text-slate-400 text-sm">Data Analytics Platform</p>
              </div>
            </div>
            <Button 
              variant="ghost" 
              onClick={handleLogout}
              className="text-slate-300 hover:text-white hover:bg-slate-800"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 lg:w-[400px]">
            <TabsTrigger value="upload" className="flex items-center gap-2">
              <Upload className="h-4 w-4" />
              Upload
            </TabsTrigger>
            <TabsTrigger value="data" className="flex items-center gap-2" disabled={!currentDatasetId}>
              <BarChart3 className="h-4 w-4" />
              Data & Charts
            </TabsTrigger>
            <TabsTrigger value="history" className="flex items-center gap-2">
              <History className="h-4 w-4" />
              History
            </TabsTrigger>
          </TabsList>

          {/* Upload Tab */}
          <TabsContent value="upload" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="h-5 w-5 text-blue-500" />
                  Upload Equipment Data
                </CardTitle>
              </CardHeader>
              <CardContent>
                <FileUpload onUpload={handleFileUpload} isLoading={isLoading} />
              </CardContent>
            </Card>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center space-x-4">
                    <div className="bg-blue-100 p-3 rounded-full">
                      <FileText className="h-6 w-6 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-sm text-slate-500">Total Datasets</p>
                      <p className="text-2xl font-bold">{datasets.length}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center space-x-4">
                    <div className="bg-green-100 p-3 rounded-full">
                      <Droplets className="h-6 w-6 text-green-600" />
                    </div>
                    <div>
                      <p className="text-sm text-slate-500">Avg Flowrate</p>
                      <p className="text-2xl font-bold">
                        {summary?.avg_flowrate?.toFixed(1) || '-'}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center space-x-4">
                    <div className="bg-orange-100 p-3 rounded-full">
                      <Gauge className="h-6 w-6 text-orange-600" />
                    </div>
                    <div>
                      <p className="text-sm text-slate-500">Avg Pressure</p>
                      <p className="text-2xl font-bold">
                        {summary?.avg_pressure?.toFixed(1) || '-'}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center space-x-4">
                    <div className="bg-red-100 p-3 rounded-full">
                      <Thermometer className="h-6 w-6 text-red-600" />
                    </div>
                    <div>
                      <p className="text-sm text-slate-500">Avg Temperature</p>
                      <p className="text-2xl font-bold">
                        {summary?.avg_temperature?.toFixed(1) || '-'}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Data & Charts Tab */}
          <TabsContent value="data" className="space-y-6">
            {currentDatasetId && summary && (
              <>
                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
                    <CardContent className="p-6">
                      <p className="text-sm text-blue-600 font-medium">Total Equipment</p>
                      <p className="text-3xl font-bold text-blue-900">{summary.total_count}</p>
                    </CardContent>
                  </Card>
                  <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
                    <CardContent className="p-6">
                      <p className="text-sm text-green-600 font-medium">Equipment Types</p>
                      <p className="text-3xl font-bold text-green-900">
                        {Object.keys(summary.type_distribution).length}
                      </p>
                    </CardContent>
                  </Card>
                  <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
                    <CardContent className="p-6">
                      <p className="text-sm text-purple-600 font-medium">Current Dataset</p>
                      <p className="text-lg font-bold text-purple-900 truncate">{currentDatasetName}</p>
                    </CardContent>
                  </Card>
                </div>

                {/* Charts */}
                {chartData && (
                  <ChartsView chartData={chartData} />
                )}

                {/* Data Table */}
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between">
                    <CardTitle className="flex items-center gap-2">
                      <FileText className="h-5 w-5 text-blue-500" />
                      Equipment Details
                    </CardTitle>
                    <Button onClick={handleDownloadPDF} disabled={isLoading}>
                      <Download className="h-4 w-4 mr-2" />
                      Download PDF Report
                    </Button>
                  </CardHeader>
                  <CardContent>
                    <DataTable datasetId={currentDatasetId} />
                  </CardContent>
                </Card>
              </>
            )}
          </TabsContent>

          {/* History Tab */}
          <TabsContent value="history">
            <HistoryView 
              datasets={datasets} 
              onSelect={handleDatasetSelect}
              isLoading={isLoading}
            />
          </TabsContent>
        </Tabs>
      </main>

      <Toaster position="top-center" />
    </div>
  );
}

export default App;
