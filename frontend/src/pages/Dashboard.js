import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Users, Mail, CheckCircle, Star, TrendingUp, Phone, ArrowRight } from 'lucide-react';
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
    { title: 'TOTAL LEADS', value: stats.total_leads, icon: Users, color: 'bg-blue-50 border-blue-200', iconColor: 'text-blue-600' },
    { title: 'EMAILS ENVIADOS', value: stats.emails_sent, icon: Mail, color: 'bg-purple-50 border-purple-200', iconColor: 'text-purple-600' },
    { title: 'RESPONDIERON', value: stats.responded, icon: CheckCircle, color: 'bg-emerald-50 border-emerald-200', iconColor: 'text-emerald-600' },
    { title: 'CLIENTES', value: stats.clients, icon: Star, color: 'bg-amber-50 border-amber-200', iconColor: 'text-amber-600' },
    { title: 'TASA RESPUESTA', value: `${stats.response_rate}%`, icon: TrendingUp, color: 'bg-cyan-50 border-cyan-200', iconColor: 'text-cyan-600' },
    { title: 'SCORE ALTO (≥7)', value: stats.high_score, icon: TrendingUp, color: 'bg-orange-50 border-orange-200', iconColor: 'text-orange-600' }
  ];

  return (
    <Layout>
      <div className="space-y-6 sm:space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 mb-2">Dashboard</h1>
          <p className="text-slate-600 text-sm sm:text-base">Panel de control y métricas principales</p>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3 sm:gap-4">
          {kpiCards.map((kpi, index) => {
            const Icon = kpi.icon;
            return (
              <Card key={index} className={`${kpi.color} border shadow-sm hover:shadow-md transition-shadow`}>
                <CardContent className="p-4 sm:p-6">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-[10px] sm:text-xs font-semibold text-slate-600 uppercase tracking-wide">{kpi.title}</p>
                    <Icon className={`w-4 h-4 sm:w-5 sm:h-5 ${kpi.iconColor}`} />
                  </div>
                  <p className="text-xl sm:text-3xl font-bold text-slate-900">{kpi.value}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Recent Leads */}
        <Card className="bg-white border-slate-200 shadow-sm">
          <CardHeader className="border-b border-slate-200">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
              <CardTitle className="text-base sm:text-lg font-bold text-slate-900">Últimos Leads</CardTitle>
              <Link to="/leads">
                <Button size="sm" className="bg-[#17a2b8] hover:bg-[#138a9d] text-white w-full sm:w-auto">
                  Ver todos <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent className="p-4 sm:p-6">
            {loading ? (
              <div className="text-center py-8 text-slate-500">Cargando...</div>
            ) : recentLeads.length === 0 ? (
              <div className="text-center py-8 text-slate-500">No hay leads recientes</div>
            ) : (
              <div className="overflow-x-auto -mx-4 sm:mx-0">
                <div className="inline-block min-w-full align-middle">
                  <table className="min-w-full">
                    <thead>
                      <tr className="border-b border-slate-200">
                        <th className="text-left py-3 px-4 text-xs font-semibold text-slate-600 uppercase">Clínica</th>
                        <th className="hidden sm:table-cell text-left py-3 px-4 text-xs font-semibold text-slate-600 uppercase">Ciudad</th>
                        <th className="hidden md:table-cell text-left py-3 px-4 text-xs font-semibold text-slate-600 uppercase">Email</th>
                        <th className="text-left py-3 px-4 text-xs font-semibold text-slate-600 uppercase">Score</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentLeads.map((lead, index) => (
                        <tr key={index} className="border-b border-slate-100 hover:bg-slate-50">
                          <td className="py-3 px-4 text-sm font-medium text-slate-900">{lead.clinica}</td>
                          <td className="hidden sm:table-cell py-3 px-4 text-sm text-slate-600">{lead.ciudad}</td>
                          <td className="hidden md:table-cell py-3 px-4 text-sm text-slate-600">{lead.email}</td>
                          <td className="py-3 px-4">
                            <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold ${
                              lead.score >= 7 ? 'bg-emerald-100 text-emerald-700' :
                              lead.score >= 5 ? 'bg-amber-100 text-amber-700' :
                              'bg-slate-100 text-slate-700'
                            }`}>
                              {lead.score}/10
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default Dashboard;