import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Users, Mail, CheckCircle, Star, TrendingUp, Phone, Clock, ArrowRight, ExternalLink } from 'lucide-react';
import { getDashboardStats, getClinics } from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState({
    total_leads: 0,
    emails_sent: 0,
    responded: 0,
    clients: 0,
    high_score: 0,
    pending_followups: 0,
    response_rate: 0
  });
  const [recentLeads, setRecentLeads] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    // Refresh every 30 seconds
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [statsData, leadsData] = await Promise.all([
        getDashboardStats(),
        getClinics(0, 5)
      ]);
      setStats(statsData);
      setRecentLeads(leadsData.clinics || []);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };
  const kpiCards = [
    { title: 'TOTAL LEADS', value: stats.total_leads, icon: Users, color: 'from-[#17a2b8]/20 to-[#17a2b8]/5 border-[#17a2b8]/30', iconColor: 'text-[#17a2b8]' },
    { title: 'EMAILS ENVIADOS', value: stats.emails_sent, icon: Mail, color: 'from-purple-500/20 to-purple-500/5 border-purple-500/30', iconColor: 'text-purple-400' },
    { title: 'RESPONDIERON', value: stats.responded, icon: CheckCircle, color: 'from-emerald-500/20 to-emerald-500/5 border-emerald-500/30', iconColor: 'text-emerald-400' },
    { title: 'CLIENTES', value: stats.clients, icon: Star, color: 'from-amber-500/20 to-amber-500/5 border-amber-500/30', iconColor: 'text-amber-400' },
    { title: 'TASA RESPUESTA', value: `${stats.response_rate}%`, icon: TrendingUp, color: 'from-cyan-500/20 to-cyan-500/5 border-cyan-500/30', iconColor: 'text-cyan-400' },
    { title: 'SCORE ALTO (≥7)', value: stats.high_score, icon: TrendingUp, color: 'from-orange-500/20 to-orange-500/5 border-orange-500/30', iconColor: 'text-orange-400' },
    { title: 'LLAMADAS', value: 0, icon: Phone, color: 'from-blue-500/20 to-blue-500/5 border-blue-500/30', iconColor: 'text-blue-400' },
    { title: 'SEGUIMIENTOS PENDIENTES', value: stats.pending_followups, icon: Clock, color: 'from-red-500/20 to-red-500/5 border-red-500/30', iconColor: 'text-red-400' }
  ];

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-1">
              GDC <span className="text-[#17a2b8]">Lead Machine</span>
            </h1>
            <p className="text-slate-400 text-sm">Motor de outbound automatizado con IA</p>
          </div>
          <Link to="/leads">
            <Button className="bg-[#17a2b8] hover:bg-[#138a9d] text-white font-medium shadow-lg shadow-[#17a2b8]/30">
              Ver todos los leads
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </Link>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {kpiCards.map((kpi, index) => {
            const Icon = kpi.icon;
            return (
              <Card key={index} className={`bg-gradient-to-br ${kpi.color} border backdrop-blur-sm`}>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-2">
                    <p className="text-xs font-medium text-slate-400 uppercase tracking-wide">{kpi.title}</p>
                    <Icon className={`w-5 h-5 ${kpi.iconColor}`} />
                  </div>
                  <p className="text-3xl font-bold text-white">{kpi.value}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Pipeline Chart */}
          <Card className="bg-[#1e3a5f]/50 border-[#17a2b8]/20 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-white text-base font-medium">ESTADO DEL PIPELINE</CardTitle>
            </CardHeader>
            <CardContent className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="w-32 h-32 rounded-full border-8 border-[#17a2b8]/30 mx-auto mb-4 flex items-center justify-center">
                  <div className="w-24 h-24 rounded-full bg-[#1e3a5f]"></div>
                </div>
                <div className="flex items-center justify-center gap-2 text-sm text-slate-400">
                  <div className="w-3 h-3 bg-[#17a2b8]/50 rounded"></div>
                  <span>Sin contactar</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Score Distribution */}
          <Card className="bg-[#1e3a5f]/50 border-[#17a2b8]/20 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-white text-base font-medium">DISTRIBUCIÓN DE SCORE IA</CardTitle>
            </CardHeader>
            <CardContent className="flex items-center justify-center h-64">
              <p className="text-slate-500 text-sm">Sin scores aún</p>
            </CardContent>
          </Card>
        </div>

        {/* Recent Leads Table */}
        <Card className="bg-[#1e3a5f]/50 border-[#17a2b8]/20 backdrop-blur-sm">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-white text-base font-medium">LEADS RECIENTES</CardTitle>
            <Link to="/leads" className="text-[#17a2b8] hover:text-[#138a9d] text-sm font-medium flex items-center gap-1">
              Ver todos
              <ArrowRight className="w-4 h-4" />
            </Link>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[#17a2b8]/20">
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-400 uppercase">CLÍNICA</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-400 uppercase">CIUDAD</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-400 uppercase">SCORE</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-400 uppercase">ESTADO</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-400 uppercase">WEB</th>
                  </tr>
                </thead>
                <tbody>
                  {recentLeads.map((lead) => (
                    <tr key={lead._id || lead.id} className="border-b border-[#17a2b8]/10 hover:bg-[#17a2b8]/10 transition-colors">
                      <td className="py-3 px-4">
                        <div className="text-white text-sm font-medium">{lead.clinica}</div>
                      </td>
                      <td className="py-3 px-4 text-slate-400 text-sm">{lead.ciudad}</td>
                      <td className="py-3 px-4">
                        <span className={`text-sm ${
                          lead.score 
                            ? lead.score >= 8 ? 'text-emerald-400' : 'text-[#17a2b8]'
                            : 'text-slate-500'
                        }`}>
                          {lead.score ? `${lead.score}/10` : 'sin score'}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium bg-slate-800/50 text-slate-400 border border-[#17a2b8]/20">
                          {lead.estado || 'Sin contactar'}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <button className="text-slate-400 hover:text-[#17a2b8] transition-colors">
                          <ExternalLink className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                  {recentLeads.length === 0 && !loading && (
                    <tr>
                      <td colSpan="5" className="py-8 text-center text-slate-500">
                        No hay leads todavía
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default Dashboard;
