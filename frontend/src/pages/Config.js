import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Mail, Plus, Trash2, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { getEmailAccounts, addEmailAccount, getEmailStats, getEmailQueue } from '../services/api';
import { useToast } from '../hooks/use-toast';

const Config = () => {
  const [emailAccounts, setEmailAccounts] = useState([]);
  const [stats, setStats] = useState({ total_sent: 0, pending: 0, failed: 0, active_accounts: 0 });
  const [queue, setQueue] = useState([]);
  const [newAccount, setNewAccount] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [accountsData, statsData, queueData] = await Promise.all([
        getEmailAccounts(),
        getEmailStats(),
        getEmailQueue()
      ]);
      setEmailAccounts(accountsData.accounts || []);
      setStats(statsData);
      setQueue(queueData.queue || []);
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const handleAddAccount = async () => {
    if (!newAccount.username || !newAccount.password) {
      toast({
        title: 'Error',
        description: 'Por favor completa todos los campos',
        variant: 'destructive'
      });
      return;
    }

    setLoading(true);
    try {
      await addEmailAccount(newAccount.username, newAccount.password);
      toast({
        title: 'Éxito',
        description: 'Cuenta de email añadida correctamente'
      });
      setNewAccount({ username: '', password: '' });
      loadData();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'No se pudo añadir la cuenta',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Configuración</h1>
          <p className="text-slate-400 text-sm">Gestión de cuentas de email y configuración del sistema</p>
        </div>

        {/* Email Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-[#17a2b8]/20 border-[#17a2b8]/30 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-medium text-slate-400 uppercase">Emails Enviados</p>
                <CheckCircle className="w-5 h-5 text-emerald-400" />
              </div>
              <p className="text-3xl font-bold text-white">{stats.total_sent}</p>
            </CardContent>
          </Card>

          <Card className="bg-amber-500/20 border-amber-500/30 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-medium text-slate-400 uppercase">En Cola</p>
                <Clock className="w-5 h-5 text-amber-400" />
              </div>
              <p className="text-3xl font-bold text-white">{stats.pending}</p>
            </CardContent>
          </Card>

          <Card className="bg-red-500/20 border-red-500/30 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-medium text-slate-400 uppercase">Fallidos</p>
                <AlertCircle className="w-5 h-5 text-red-400" />
              </div>
              <p className="text-3xl font-bold text-white">{stats.failed}</p>
            </CardContent>
          </Card>

          <Card className="bg-purple-500/20 border-purple-500/30 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-medium text-slate-400 uppercase">Cuentas Activas</p>
                <Mail className="w-5 h-5 text-purple-400" />
              </div>
              <p className="text-3xl font-bold text-white">{stats.active_accounts}</p>
            </CardContent>
          </Card>
        </div>

        {/* Add Email Account */}
        <Card className="bg-[#1e3a5f]/50 border-[#17a2b8]/20 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-white text-base font-medium flex items-center gap-2">
              <Plus className="w-5 h-5" />
              Añadir Cuenta de Email
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="username" className="text-slate-300 mb-2 block">Email</Label>
                <Input
                  id="username"
                  type="email"
                  placeholder="info@ejemplo.com"
                  value={newAccount.username}
                  onChange={(e) => setNewAccount({ ...newAccount, username: e.target.value })}
                  className="bg-slate-800 border-slate-700 text-white"
                />
              </div>
              <div>
                <Label htmlFor="password" className="text-slate-300 mb-2 block">Contraseña</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={newAccount.password}
                  onChange={(e) => setNewAccount({ ...newAccount, password: e.target.value })}
                  className="bg-slate-800 border-slate-700 text-white"
                />
              </div>
              <div className="flex items-end">
                <Button
                  onClick={handleAddAccount}
                  disabled={loading}
                  className="w-full bg-[#17a2b8] hover:bg-[#138a9d] text-white"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Añadir Cuenta
                </Button>
              </div>
            </div>
            <p className="text-xs text-slate-500 mt-4">
              ⚠️ Las cuentas añadidas enviarán 1 email cada 120 segundos automáticamente
            </p>
          </CardContent>
        </Card>

        {/* Active Email Accounts */}
        <Card className="bg-[#1e3a5f]/50 border-[#17a2b8]/20 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-white text-base font-medium">Cuentas de Email Activas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {emailAccounts.map((account, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg border border-[#17a2b8]/20">
                  <div className="flex items-center gap-3">
                    <Mail className="w-5 h-5 text-[#17a2b8]" />
                    <div>
                      <p className="text-white font-medium">{account.username}</p>
                      <p className="text-xs text-slate-400">
                        {account.last_sent 
                          ? `Último envío: ${new Date(account.last_sent).toLocaleString('es-ES')}`
                          : 'Sin envíos aún'}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-emerald-400 flex items-center gap-1">
                      <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                      Activa
                    </span>
                  </div>
                </div>
              ))}
              {emailAccounts.length === 0 && (
                <p className="text-center text-slate-500 py-8">No hay cuentas configuradas</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Email Queue */}
        <Card className="bg-[#1e3a5f]/50 border-[#17a2b8]/20 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-white text-base font-medium">Cola de Emails</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[#17a2b8]/20">
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-400 uppercase">Clínica</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-400 uppercase">Email</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-400 uppercase">Estado</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-400 uppercase">Añadido</th>
                  </tr>
                </thead>
                <tbody>
                  {queue.slice(0, 10).map((item, index) => (
                    <tr key={index} className="border-b border-[#17a2b8]/10">
                      <td className="py-3 px-4 text-white text-sm">{item.clinic_data?.clinica}</td>
                      <td className="py-3 px-4 text-slate-400 text-sm">{item.clinic_data?.email}</td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium ${
                          item.status === 'sent' ? 'bg-emerald-500/20 text-emerald-400' :
                          item.status === 'pending' ? 'bg-amber-500/20 text-amber-400' :
                          'bg-red-500/20 text-red-400'
                        }`}>
                          {item.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-400 text-sm">
                        {new Date(item.added_at).toLocaleString('es-ES')}
                      </td>
                    </tr>
                  ))}
                  {queue.length === 0 && (
                    <tr>
                      <td colSpan="4" className="py-8 text-center text-slate-500">
                        No hay emails en cola
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

export default Config;
