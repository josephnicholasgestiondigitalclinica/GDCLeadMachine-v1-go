import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Mail, CheckCircle, Clock, AlertCircle, Search, Send } from 'lucide-react';
import { getEmailStats, getEmailQueue } from '../services/api';

const Outreach = () => {
  const [stats, setStats] = useState({ total_sent: 0, pending: 0, failed: 0, active_accounts: 0 });
  const [emails, setEmails] = useState([]);
  const [filteredEmails, setFilteredEmails] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    filterEmails();
  }, [emails, searchTerm, statusFilter]);

  const loadData = async () => {
    try {
      const [statsData, queueData] = await Promise.all([
        getEmailStats(),
        getEmailQueue()
      ]);
      setStats(statsData);
      setEmails(queueData.queue || []);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterEmails = () => {
    let filtered = emails;

    // Filter by status
    if (statusFilter !== 'all') {
      filtered = filtered.filter(email => email.status === statusFilter);
    }

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(email => 
        email.clinic_data?.clinica?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        email.clinic_data?.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        email.clinic_data?.ciudad?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredEmails(filtered);
  };

  const getStatusIcon = (status) => {
    switch(status) {
      case 'sent':
        return <CheckCircle className="w-4 h-4 text-emerald-600" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-amber-600" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-600" />;
      default:
        return <Mail className="w-4 h-4 text-slate-400" />;
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      sent: 'bg-emerald-100 text-emerald-700 border-emerald-200',
      pending: 'bg-amber-100 text-amber-700 border-amber-200',
      failed: 'bg-red-100 text-red-700 border-red-200'
    };
    return (
      <Badge className={`${styles[status]} text-xs font-semibold border`}>
        {status === 'sent' ? 'Enviado' : status === 'pending' ? 'Pendiente' : 'Fallido'}
      </Badge>
    );
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 mb-2">Outreach</h1>
          <p className="text-slate-600 text-sm sm:text-base">Gestión y seguimiento de emails enviados</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
          <Card className="bg-emerald-50 border-emerald-200 shadow-sm">
            <CardContent className="p-4 sm:p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-[10px] sm:text-xs font-semibold text-slate-600 uppercase">Enviados</p>
                <CheckCircle className="w-4 h-4 sm:w-5 sm:h-5 text-emerald-600" />
              </div>
              <p className="text-2xl sm:text-3xl font-bold text-slate-900">{stats.total_sent}</p>
            </CardContent>
          </Card>

          <Card className="bg-amber-50 border-amber-200 shadow-sm">
            <CardContent className="p-4 sm:p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-[10px] sm:text-xs font-semibold text-slate-600 uppercase">En Cola</p>
                <Clock className="w-4 h-4 sm:w-5 sm:h-5 text-amber-600" />
              </div>
              <p className="text-2xl sm:text-3xl font-bold text-slate-900">{stats.pending}</p>
            </CardContent>
          </Card>

          <Card className="bg-red-50 border-red-200 shadow-sm">
            <CardContent className="p-4 sm:p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-[10px] sm:text-xs font-semibold text-slate-600 uppercase">Fallidos</p>
                <AlertCircle className="w-4 h-4 sm:w-5 sm:h-5 text-red-600" />
              </div>
              <p className="text-2xl sm:text-3xl font-bold text-slate-900">{stats.failed}</p>
            </CardContent>
          </Card>

          <Card className="bg-blue-50 border-blue-200 shadow-sm">
            <CardContent className="p-4 sm:p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-[10px] sm:text-xs font-semibold text-slate-600 uppercase">Tasa Éxito</p>
                <Send className="w-4 h-4 sm:w-5 sm:h-5 text-blue-600" />
              </div>
              <p className="text-2xl sm:text-3xl font-bold text-slate-900">
                {stats.total_sent > 0 ? Math.round((stats.total_sent / (stats.total_sent + stats.failed)) * 100) : 0}%
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card className="bg-white border-slate-200 shadow-sm">
          <CardContent className="p-4">
            <div className="flex flex-col lg:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
                <Input
                  placeholder="Buscar por clínica, email o ciudad..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-white border-slate-200 focus:border-[#17a2b8] focus:ring-[#17a2b8]"
                />
              </div>
              <div className="flex gap-2 overflow-x-auto pb-2 lg:pb-0">
                {['all', 'sent', 'pending', 'failed'].map((status) => (
                  <button
                    key={status}
                    onClick={() => setStatusFilter(status)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
                      statusFilter === status
                        ? 'bg-[#17a2b8] text-white'
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    {status === 'all' ? 'Todos' : status === 'sent' ? 'Enviados' : status === 'pending' ? 'Pendientes' : 'Fallidos'}
                  </button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Email List */}
        <Card className="bg-white border-slate-200 shadow-sm">
          <CardHeader className="border-b border-slate-200">
            <CardTitle className="text-base sm:text-lg font-bold text-slate-900">
              Historial de Emails ({filteredEmails.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 sm:p-6">
            {loading ? (
              <div className="text-center py-8 text-slate-500">Cargando...</div>
            ) : filteredEmails.length === 0 ? (
              <div className="text-center py-8">
                <Mail className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                <p className="text-slate-500">No se encontraron emails</p>
              </div>
            ) : (
              <div className="space-y-3">
                {filteredEmails.map((email, index) => (
                  <div key={index} className="p-4 bg-slate-50 rounded-lg border border-slate-200 hover:border-slate-300 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 mb-2 flex-wrap">
                          {getStatusIcon(email.status)}
                          <h3 className="text-slate-900 font-semibold truncate">{email.clinic_data?.clinica || 'N/A'}</h3>
                          {getStatusBadge(email.status)}
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 text-sm">
                          <div className="text-slate-600 truncate">
                            <span className="text-slate-500 font-medium">Email:</span> {email.clinic_data?.email || 'N/A'}
                          </div>
                          <div className="text-slate-600">
                            <span className="text-slate-500 font-medium">Ciudad:</span> {email.clinic_data?.ciudad || 'N/A'}
                          </div>
                          <div className="text-slate-600">
                            <span className="text-slate-500 font-medium">Añadido:</span> {new Date(email.added_at).toLocaleDateString('es-ES')}
                          </div>
                        </div>
                        {email.sent_at && (
                          <div className="text-sm text-slate-600 mt-2">
                            <span className="text-slate-500 font-medium">Enviado:</span> {new Date(email.sent_at).toLocaleString('es-ES')}
                          </div>
                        )}
                        {email.attempts > 1 && (
                          <div className="text-sm text-amber-600 mt-2 font-medium">
                            ⚠️ Intentos: {email.attempts}
                          </div>
                        )}
                      </div>
                    </div>
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

export default Outreach;
