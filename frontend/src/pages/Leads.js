import React, { useState } from 'react';
import Layout from '../components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Sparkles, Download, Upload, Plus, Search, ExternalLink } from 'lucide-react';
import { allMockLeads } from '../data/mockLeads';

const Leads = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [scoreFilter, setScoreFilter] = useState('all');

  const filteredLeads = allMockLeads.filter(lead => {
    const matchesSearch = lead.clinica.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          lead.ciudad.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          lead.email.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || lead.estado === statusFilter;
    const matchesScore = scoreFilter === 'all' || 
                         (scoreFilter === '7+' && lead.score && lead.score >= 7) ||
                         (scoreFilter === '8+' && lead.score && lead.score >= 8) ||
                         (scoreFilter === '9+' && lead.score && lead.score >= 9);
    
    return matchesSearch && matchesStatus && matchesScore;
  });

  const leadsWithScore = allMockLeads.filter(l => l.score && l.score >= 7).length;

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Leads</h1>
            <p className="text-slate-400 text-sm">{allMockLeads.length} clínicas en base de datos</p>
          </div>
          <div className="flex gap-3">
            <Button className="bg-yellow-500 hover:bg-yellow-600 text-slate-900 font-medium">
              <Sparkles className="w-4 h-4 mr-2" />
              Analizar con IA
              <span className="ml-2 bg-slate-900 text-yellow-500 px-2 py-0.5 rounded text-xs font-bold">
                {leadsWithScore}
              </span>
            </Button>
            <Button variant="outline" className="border-teal-500 text-teal-400 hover:bg-teal-500/10">
              <Download className="w-4 h-4 mr-2" />
              Exportar para envío
            </Button>
            <Button variant="outline" className="border-slate-600 text-slate-300 hover:bg-slate-800">
              <Upload className="w-4 h-4 mr-2" />
              Importar
            </Button>
            <Button className="bg-yellow-500 hover:bg-yellow-600 text-slate-900 font-medium">
              <Plus className="w-4 h-4 mr-2" />
              Nuevo Lead
            </Button>
          </div>
        </div>

        {/* Filters */}
        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="p-6">
            <div className="flex gap-4 items-center">
              {/* Search */}
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <Input
                  placeholder="Buscar clínica, ciudad, email..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 bg-slate-800 border-slate-700 text-white placeholder:text-slate-500"
                />
              </div>

              {/* Status Filter */}
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-[200px] bg-slate-800 border-slate-700 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-800 border-slate-700">
                  <SelectItem value="all" className="text-white">Todos</SelectItem>
                  <SelectItem value="Sin contactar" className="text-white">Sin contactar</SelectItem>
                  <SelectItem value="Email enviado" className="text-white">Email enviado</SelectItem>
                  <SelectItem value="Respondió" className="text-white">Respondió</SelectItem>
                  <SelectItem value="Llamada programada" className="text-white">Llamada programada</SelectItem>
                  <SelectItem value="Cliente" className="text-white">Cliente</SelectItem>
                  <SelectItem value="Descartado" className="text-white">Descartado</SelectItem>
                </SelectContent>
              </Select>

              {/* Score Filter */}
              <Select value={scoreFilter} onValueChange={setScoreFilter}>
                <SelectTrigger className="w-[200px] bg-slate-800 border-slate-700 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-800 border-slate-700">
                  <SelectItem value="all" className="text-white">Todos los scores</SelectItem>
                  <SelectItem value="7+" className="text-white">Score ≥ 7</SelectItem>
                  <SelectItem value="8+" className="text-white">Score ≥ 8</SelectItem>
                  <SelectItem value="9+" className="text-white">Score ≥ 9</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Leads Table */}
        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-800">
                    <th className="text-left py-4 px-6 text-xs font-medium text-slate-400 uppercase">CLÍNICA</th>
                    <th className="text-left py-4 px-6 text-xs font-medium text-slate-400 uppercase">CIUDAD</th>
                    <th className="text-left py-4 px-6 text-xs font-medium text-slate-400 uppercase">EMAIL</th>
                    <th className="text-left py-4 px-6 text-xs font-medium text-slate-400 uppercase">SCORE</th>
                    <th className="text-left py-4 px-6 text-xs font-medium text-slate-400 uppercase">ESTADO</th>
                    <th className="text-left py-4 px-6 text-xs font-medium text-slate-400 uppercase">ACCIONES</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredLeads.map((lead) => (
                    <tr key={lead.id} className="border-b border-slate-800 hover:bg-slate-800/50 transition-colors">
                      <td className="py-4 px-6">
                        <div>
                          <div className="text-white text-sm font-medium">{lead.clinica}</div>
                          <div className="text-slate-500 text-xs mt-0.5">{lead.telefono}</div>
                        </div>
                      </td>
                      <td className="py-4 px-6 text-slate-300 text-sm">{lead.ciudad}</td>
                      <td className="py-4 px-6 text-slate-400 text-sm">{lead.email}</td>
                      <td className="py-4 px-6">
                        <span className={`text-sm ${
                          lead.score 
                            ? lead.score >= 8 ? 'text-green-400' : 'text-yellow-400'
                            : 'text-slate-500'
                        }`}>
                          {lead.score ? `${lead.score}/10` : 'sin score'}
                        </span>
                      </td>
                      <td className="py-4 px-6">
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-slate-800 text-slate-400 border border-slate-700">
                          Sin contactar
                        </span>
                      </td>
                      <td className="py-4 px-6">
                        <button className="text-slate-400 hover:text-white transition-colors">
                          <ExternalLink className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            {/* Pagination Info */}
            <div className="p-4 border-t border-slate-800 text-center">
              <p className="text-sm text-slate-400">
                {filteredLeads.length} de {allMockLeads.length} leads
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default Leads;
