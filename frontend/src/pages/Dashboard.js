import React from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Users, Mail, CheckCircle, Star, TrendingUp, Phone, Clock, ArrowRight, ExternalLink } from 'lucide-react';
import { mockLeads } from '../data/mockLeads';

const Dashboard = () => {
  const kpiCards = [
    { title: 'TOTAL LEADS', value: '500', icon: Users, color: 'from-blue-500/10 to-blue-500/5 border-blue-500/20', iconColor: 'text-blue-400' },
    { title: 'EMAILS ENVIADOS', value: '0', icon: Mail, color: 'from-purple-500/10 to-purple-500/5 border-purple-500/20', iconColor: 'text-purple-400' },
    { title: 'RESPONDIERON', value: '0', icon: CheckCircle, color: 'from-teal-500/10 to-teal-500/5 border-teal-500/20', iconColor: 'text-teal-400' },
    { title: 'CLIENTES', value: '0', icon: Star, color: 'from-amber-500/10 to-amber-500/5 border-amber-500/20', iconColor: 'text-amber-400' },
    { title: 'TASA RESPUESTA', value: '0%', icon: TrendingUp, color: 'from-cyan-500/10 to-cyan-500/5 border-cyan-500/20', iconColor: 'text-cyan-400' },
    { title: 'SCORE ALTO (≥7)', value: '0', icon: TrendingUp, color: 'from-orange-500/10 to-orange-500/5 border-orange-500/20', iconColor: 'text-orange-400' },
    { title: 'LLAMADAS', value: '0', icon: Phone, color: 'from-blue-500/10 to-blue-500/5 border-blue-500/20', iconColor: 'text-blue-400' },
    { title: 'SEGUIMIENTOS PENDIENTES', value: '0', icon: Clock, color: 'from-red-500/10 to-red-500/5 border-red-500/20', iconColor: 'text-red-400' }
  ];

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-1">
              GDC <span className="text-yellow-500">Lead Machine</span>
            </h1>
            <p className="text-slate-400 text-sm">Motor de outbound automatizado con IA</p>
          </div>
          <Link to="/leads">
            <Button className="bg-yellow-500 hover:bg-yellow-600 text-slate-900 font-medium">
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
              <Card key={index} className={`bg-gradient-to-br ${kpi.color} border`}>
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
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-white text-base font-medium">ESTADO DEL PIPELINE</CardTitle>
            </CardHeader>
            <CardContent className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="w-32 h-32 rounded-full border-8 border-slate-700 mx-auto mb-4 flex items-center justify-center">
                  <div className="w-24 h-24 rounded-full bg-slate-800"></div>
                </div>
                <div className="flex items-center justify-center gap-2 text-sm text-slate-400">
                  <div className="w-3 h-3 bg-slate-600 rounded"></div>
                  <span>Sin contactar</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Score Distribution */}
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-white text-base font-medium">DISTRIBUCIÓN DE SCORE IA</CardTitle>
            </CardHeader>
            <CardContent className="flex items-center justify-center h-64">
              <p className="text-slate-500 text-sm">Sin scores aún</p>
            </CardContent>
          </Card>
        </div>

        {/* Recent Leads Table */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-white text-base font-medium">LEADS RECIENTES</CardTitle>
            <Link to="/leads" className="text-yellow-500 hover:text-yellow-400 text-sm font-medium flex items-center gap-1">
              Ver todos
              <ArrowRight className="w-4 h-4" />
            </Link>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-800">
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-400 uppercase">CLÍNICA</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-400 uppercase">CIUDAD</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-400 uppercase">SCORE</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-400 uppercase">ESTADO</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-400 uppercase">WEB</th>
                  </tr>
                </thead>
                <tbody>
                  {mockLeads.slice(0, 5).map((lead) => (
                    <tr key={lead.id} className="border-b border-slate-800 hover:bg-slate-800/50">
                      <td className="py-3 px-4">
                        <div className="text-white text-sm font-medium">{lead.clinica}</div>
                      </td>
                      <td className="py-3 px-4 text-slate-400 text-sm">{lead.ciudad}</td>
                      <td className="py-3 px-4">
                        <span className="text-slate-500 text-sm">
                          {lead.score ? `${lead.score}/10` : 'sin score'}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium bg-slate-800 text-slate-400">
                          Sin contactar
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <button className="text-slate-400 hover:text-white">
                          <ExternalLink className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
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
