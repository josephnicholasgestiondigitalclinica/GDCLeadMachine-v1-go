import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Search, Phone, Mail, ExternalLink, MessageSquare } from 'lucide-react';
import { getClinics } from '../services/api';

const Leads = () => {
  const [leads, setLeads] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [scoreFilter, setScoreFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeads();
  }, []);

  const loadLeads = async () => {
    try {
      const data = await getClinics(0, 100);
      setLeads(data.clinics || []);
    } catch (error) {
      console.error('Error loading leads:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredLeads = leads.filter(lead => {
    const matchesSearch = lead.clinica?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          lead.ciudad?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          lead.email?.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || lead.estado === statusFilter;
    const matchesScore = scoreFilter === 'all' || 
                         (scoreFilter === '7+' && lead.score && lead.score >= 7) ||
                         (scoreFilter === '5-6' && lead.score && lead.score >= 5 && lead.score < 7) ||
                         (scoreFilter === '<5' && lead.score && lead.score < 5);
    
    return matchesSearch && matchesStatus && matchesScore;
  });

  const sendWhatsApp = (phone, clinicName) => {
    const cleanPhone = phone.replace(/[^0-9]/g, '');
    const message = encodeURIComponent(`Hola ${clinicName}, soy José Cabrejas de Gestión Digital Clínica. ¿Tienes un momento para hablar sobre cómo podemos ayudar a tu clínica?`);
    window.open(`https://wa.me/34${cleanPhone}?text=${message}`, '_blank');
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 mb-2">Leads</h1>
            <p className="text-slate-600 text-sm">{leads.length} clínicas en base de datos</p>
          </div>
        </div>

        {/* Filters */}
        <Card className="bg-white border-slate-200 shadow-sm">
          <CardContent className="p-4">
            <div className="flex flex-col lg:flex-row gap-4">
              {/* Search */}
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <Input
                  placeholder="Buscar clínica, ciudad, email..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 bg-white border-slate-300 text-slate-900 placeholder:text-slate-400 focus:border-[#17a2b8] focus:ring-[#17a2b8]"
                />
              </div>

              {/* Status Filter */}
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-full lg:w-[200px] bg-white border-slate-300 text-slate-900">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-white border-slate-200">
                  <SelectItem value="all">Todos los estados</SelectItem>
                  <SelectItem value="Sin contactar">Sin contactar</SelectItem>
                  <SelectItem value="Email enviado">Email enviado</SelectItem>
                  <SelectItem value="Respondió">Respondió</SelectItem>
                  <SelectItem value="Cliente">Cliente</SelectItem>
                </SelectContent>
              </Select>

              {/* Score Filter */}
              <Select value={scoreFilter} onValueChange={setScoreFilter}>
                <SelectTrigger className="w-full lg:w-[200px] bg-white border-slate-300 text-slate-900">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-white border-slate-200">
                  <SelectItem value="all">Todos los scores</SelectItem>
                  <SelectItem value="7+">Score 7+</SelectItem>
                  <SelectItem value="5-6">Score 5-6</SelectItem>
                  <SelectItem value="<5">Score menor a 5</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Leads Table */}
        <Card className="bg-white border-slate-200 shadow-sm">
          <CardContent className="p-0">
            {loading ? (
              <div className="text-center py-12 text-slate-500">Cargando leads...</div>
            ) : filteredLeads.length === 0 ? (
              <div className="text-center py-12 text-slate-500">No hay leads</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-50 border-b border-slate-200">
                    <tr>
                      <th className="text-left py-4 px-6 text-xs font-semibold text-slate-700 uppercase tracking-wide">Clínica</th>
                      <th className="hidden md:table-cell text-left py-4 px-6 text-xs font-semibold text-slate-700 uppercase tracking-wide">Ciudad</th>
                      <th className="hidden lg:table-cell text-left py-4 px-6 text-xs font-semibold text-slate-700 uppercase tracking-wide">Email</th>
                      <th className="text-left py-4 px-6 text-xs font-semibold text-slate-700 uppercase tracking-wide">Score</th>
                      <th className="text-right py-4 px-6 text-xs font-semibold text-slate-700 uppercase tracking-wide">Acciones</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {filteredLeads.map((lead, index) => (
                      <tr key={index} className="hover:bg-slate-50 transition-colors">
                        <td className="py-4 px-6">
                          <div className="font-semibold text-slate-900">{lead.clinica}</div>
                          <div className="text-sm text-slate-600 md:hidden">{lead.ciudad}</div>
                          <div className="text-sm text-slate-600 lg:hidden">{lead.email}</div>
                        </td>
                        <td className="hidden md:table-cell py-4 px-6 text-slate-700">{lead.ciudad}</td>
                        <td className="hidden lg:table-cell py-4 px-6 text-slate-700">{lead.email}</td>
                        <td className="py-4 px-6">
                          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-bold ${
                            lead.score >= 7 ? 'bg-emerald-100 text-emerald-800' :
                            lead.score >= 5 ? 'bg-amber-100 text-amber-800' :
                            'bg-slate-100 text-slate-800'
                          }`}>
                            {lead.score || 'N/A'}/10
                          </span>
                        </td>
                        <td className="py-4 px-6">
                          <div className="flex justify-end gap-2">
                            {lead.telefono && (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => sendWhatsApp(lead.telefono, lead.clinica)}
                                className="border-green-600 text-green-700 hover:bg-green-50"
                                title="Enviar WhatsApp"
                              >
                                <MessageSquare className="w-4 h-4" />
                              </Button>
                            )}
                            {lead.email && (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => window.location.href = `mailto:${lead.email}`}
                                className="border-slate-300 text-slate-700 hover:bg-slate-50"
                                title="Enviar Email"
                              >
                                <Mail className="w-4 h-4" />
                              </Button>
                            )}
                            {lead.website && (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => window.open(lead.website, '_blank')}
                                className="border-slate-300 text-slate-700 hover:bg-slate-50"
                                title="Ver Website"
                              >
                                <ExternalLink className="w-4 h-4" />
                              </Button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default Leads;