import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Target, Play, MapPin, Sparkles, AlertCircle } from 'lucide-react';
import axios from 'axios';
import { useToast } from '../hooks/use-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Prospeccion = () => {
  const [stats, setStats] = useState({ by_region: [] });
  const [discoveryStatus, setDiscoveryStatus] = useState({ is_running: false });
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 15000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [statsData, statusData] = await Promise.all([
        axios.get(`${API}/stats/dashboard`),
        axios.get(`${API}/discovery/status`)
      ]);
      setStats(statsData.data);
      setDiscoveryStatus(statusData.data);
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const triggerDiscovery = async () => {
    setLoading(true);
    try {
      await axios.post(`${API}/discovery/trigger`);
      toast({
        title: 'Búsqueda iniciada',
        description: 'El sistema está realizando web scraping de clínicas reales...'
      });
      loadData();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'No se pudo iniciar la búsqueda',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const regionData = stats.by_region || [];
  const madridLeads = regionData.find(r => r._id === 'Madrid')?.count || 0;
  const otherLeads = regionData.filter(r => r._id !== 'Madrid' && r._id !== null);

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 mb-2">Prospección Real</h1>
            <p className="text-slate-600 text-sm">Web scraping de clínicas reales - Sin datos falsos</p>
          </div>
          <Button
            onClick={triggerDiscovery}
            disabled={loading || discoveryStatus.is_running}
            className="bg-[#17a2b8] hover:bg-[#138a9d] text-white shadow-md w-full sm:w-auto"
          >
            {discoveryStatus.is_running ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2" />
                Búsqueda en Curso...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Iniciar Búsqueda Real
              </>
            )}
          </Button>
        </div>

        {/* Warning Banner */}
        <Card className="bg-amber-50 border-amber-200 shadow-sm">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-amber-900 mb-1">Web Scraping Real Activado</h3>
                <p className="text-sm text-amber-800">
                  El sistema ahora busca clínicas REALES de Doctoralia, Páginas Amarillas y Google. 
                  Los resultados pueden tardar varios minutos. Todas las clínicas son verificadas antes de enviar emails.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Status Card */}
        <Card className="bg-white border-slate-200 shadow-sm">
          <CardHeader className="border-b border-slate-200">
            <CardTitle className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Target className="w-5 h-5 text-[#17a2b8]" />
              Estado del Sistema
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg border border-slate-200">
                <div>
                  <p className="text-sm font-medium text-slate-600">Estado</p>
                  <p className="text-lg font-bold text-slate-900">
                    {discoveryStatus.is_running ? 'Buscando...' : 'Inactivo'}
                  </p>
                </div>
                <div className={`w-3 h-3 rounded-full ${
                  discoveryStatus.is_running ? 'bg-emerald-500 animate-pulse' : 'bg-slate-300'
                }`} />
              </div>
              
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-sm font-medium text-blue-900 mb-1">Frecuencia</p>
                <p className="text-slate-700">Ejecuta automáticamente cada 6 horas</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Madrid Priority */}
        <Card className="bg-white border-slate-200 shadow-sm">
          <CardHeader className="border-b border-slate-200">
            <CardTitle className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <MapPin className="w-5 h-5 text-[#17a2b8]" />
              Madrid (Prioridad)
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <div className="text-center py-8">
              <p className="text-5xl font-bold text-slate-900 mb-2">{madridLeads}</p>
              <p className="text-slate-600">Clínicas descubiertas</p>
            </div>
          </CardContent>
        </Card>

        {/* Other Regions */}
        <Card className="bg-white border-slate-200 shadow-sm">
          <CardHeader className="border-b border-slate-200">
            <CardTitle className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-[#17a2b8]" />
              Otras Regiones
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            {otherLeads.length === 0 ? (
              <p className="text-center text-slate-500 py-8">Sin datos de otras regiones aún</p>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {otherLeads.map((region, index) => (
                  <div key={index} className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                    <p className="font-semibold text-slate-900 mb-1">{region._id || 'Sin región'}</p>
                    <p className="text-2xl font-bold text-[#17a2b8]">{region.count}</p>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default Prospeccion;