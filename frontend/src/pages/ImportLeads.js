import React, { useState } from 'react';
import Layout from '../components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Upload, Download, AlertCircle, CheckCircle, FileSpreadsheet } from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ImportLeads = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const { toast } = useToast();

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.name.endsWith('.csv')) {
      setFile(selectedFile);
      setResult(null);
    } else {
      toast({
        title: 'Error',
        description: 'Por favor selecciona un archivo CSV',
        variant: 'destructive'
      });
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API}/clinics/bulk`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setResult(response.data);
      toast({
        title: '¡Éxito!',
        description: `${response.data.total_processed} leads importados correctamente`
      });
      setFile(null);
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Error al importar leads',
        variant: 'destructive'
      });
    } finally {
      setUploading(false);
    }
  };

  const downloadTemplate = () => {
    const template = 'clinica,ciudad,email,telefono,website,comunidad_autonoma\\n' +
      'Clínica Dental Madrid Centro,Madrid,info@clinicadental.es,912 345 678,www.clinicadental.es,Madrid\\n' +
      'Fisioterapia Valencia,Valencia,contacto@fisio.com,963 123 456,www.fisio.com,Comunidad Valenciana';
    
    const blob = new Blob([template], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'plantilla_leads.csv';
    a.click();
  };

  return (
    <Layout>
      <div className="space-y-6 max-w-4xl mx-auto">
        {/* Header */}
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 mb-2">Importar Leads</h1>
          <p className="text-slate-600 text-sm">Añade clínicas reales desde archivo CSV</p>
        </div>

        {/* Warning Banner */}
        <Card className="bg-red-50 border-red-200 shadow-sm">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-red-900 mb-1">⚠️ Solo Datos Reales</h3>
                <p className="text-sm text-red-800">
                  El descubrimiento automático está DESACTIVADO. Solo importa clínicas con emails REALES 
                  que hayas verificado. Los emails falsos causan bounces y dañan tu reputación de envío.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Template Download */}
        <Card className="bg-white border-slate-200 shadow-sm">
          <CardHeader className="border-b border-slate-200">
            <CardTitle className="text-lg font-bold text-slate-900">1. Descarga la Plantilla</CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <p className="text-slate-600 mb-4">
              Descarga la plantilla CSV y rellénala con los datos REALES de tus clínicas
            </p>
            <Button
              onClick={downloadTemplate}
              className="bg-[#17a2b8] hover:bg-[#138a9d] text-white"
            >
              <Download className="w-4 h-4 mr-2" />
              Descargar Plantilla CSV
            </Button>

            <div className="mt-6 p-4 bg-slate-50 rounded-lg border border-slate-200">
              <p className="text-sm font-semibold text-slate-700 mb-2">Formato requerido:</p>
              <code className="text-xs text-slate-600 block bg-white p-3 rounded border border-slate-200 overflow-x-auto">
                clinica,ciudad,email,telefono,website,comunidad_autonoma
              </code>
              <p className="text-xs text-slate-500 mt-2">
                * Todos los campos son requeridos excepto telefono y website
              </p>
            </div>
          </CardContent>
        </Card>

        {/* File Upload */}
        <Card className="bg-white border-slate-200 shadow-sm">
          <CardHeader className="border-b border-slate-200">
            <CardTitle className="text-lg font-bold text-slate-900">2. Sube tu Archivo CSV</CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <div className="space-y-4">
              <div>
                <Label className="text-slate-700 font-medium mb-2 block">Seleccionar archivo CSV</Label>
                <Input
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  className="bg-white border-slate-300 text-slate-900"
                />
              </div>

              {file && (
                <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="flex items-center gap-3">
                    <FileSpreadsheet className="w-5 h-5 text-blue-600" />
                    <div>
                      <p className="font-semibold text-blue-900">{file.name}</p>
                      <p className="text-sm text-blue-700">{(file.size / 1024).toFixed(2)} KB</p>
                    </div>
                  </div>
                </div>
              )}

              <Button
                onClick={handleUpload}
                disabled={!file || uploading}
                className="bg-emerald-600 hover:bg-emerald-700 text-white w-full"
              >
                {uploading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2" />
                    Importando...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4 mr-2" />
                    Importar Leads
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Results */}
        {result && (
          <Card className="bg-emerald-50 border-emerald-200 shadow-sm">
            <CardContent className="p-6">
              <div className="flex items-start gap-3">
                <CheckCircle className="w-6 h-6 text-emerald-600 flex-shrink-0" />
                <div className="flex-1">
                  <h3 className="font-semibold text-emerald-900 mb-2">¡Importación Completada!</h3>
                  <div className="space-y-1 text-sm text-emerald-800">
                    <p>✅ Total procesados: <strong>{result.total_processed}</strong></p>
                    <p>✅ Exitosos: <strong>{result.successful}</strong></p>
                    {result.failed > 0 && (
                      <p className="text-red-700">❌ Fallidos: <strong>{result.failed}</strong></p>
                    )}
                    {result.queued > 0 && (
                      <p>📧 Añadidos a cola de email: <strong>{result.queued}</strong></p>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Info Card */}
        <Card className="bg-blue-50 border-blue-200 shadow-sm">
          <CardContent className="p-6">
            <h3 className="font-semibold text-blue-900 mb-2">💡 Consejos</h3>
            <ul className="space-y-2 text-sm text-blue-800">
              <li>✓ Verifica que todos los emails sean REALES antes de importar</li>
              <li>✓ Los leads con score ≥7 se añadirán automáticamente a la cola de emails</li>
              <li>✓ Puedes importar múltiples archivos CSV</li>
              <li>✓ Los duplicados serán detectados automáticamente</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default ImportLeads;
