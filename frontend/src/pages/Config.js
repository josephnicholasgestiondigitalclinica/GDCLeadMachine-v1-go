import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Mail, Plus, Trash2, Eye, EyeOff, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { getEmailAccounts, addEmailAccount, getEmailQueue, getEmailStats } from '../services/api';
import { useToast } from '../hooks/use-toast';

const Config = () => {
  const [accounts, setAccounts] = useState([]);
  const [queue, setQueue] = useState([]);
  const [stats, setStats] = useState({ total_sent: 0, pending: 0, failed: 0 });
  const [showPassword, setShowPassword] = useState({});
  const [newAccount, setNewAccount] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [accountsData, queueData, statsData] = await Promise.all([
        getEmailAccounts(),
        getEmailQueue(),
        getEmailStats()
      ]);
      setAccounts(accountsData.accounts || []);
      setQueue(queueData.queue || []);
      setStats(statsData);
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const handleAddAccount = async (e) => {
    e.preventDefault();
    if (!newAccount.username || !newAccount.password) return;

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
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 mb-2">Configuración</h1>
          <p className="text-slate-600 text-sm">Gestión de cuentas de email y cola de envíos</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Card className="bg-emerald-50 border-emerald-200 shadow-sm">
            <CardContent className="p-4 sm:p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-semibold text-slate-600 uppercase">Enviados</p>
                <CheckCircle className="w-5 h-5 text-emerald-600" />
              </div>
              <p className="text-3xl font-bold text-slate-900">{stats.total_sent}</p>
            </CardContent>
          </Card>

          <Card className="bg-amber-50 border-amber-200 shadow-sm">
            <CardContent className="p-4 sm:p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-semibold text-slate-600 uppercase">En Cola</p>
                <Clock className="w-5 h-5 text-amber-600" />
              </div>
              <p className="text-3xl font-bold text-slate-900">{stats.pending}</p>
            </CardContent>
          </Card>

          <Card className="bg-red-50 border-red-200 shadow-sm">
            <CardContent className="p-4 sm:p-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-semibold text-slate-600 uppercase">Fallidos</p>
                <AlertCircle className="w-5 h-5 text-red-600" />
              </div>
              <p className="text-3xl font-bold text-slate-900">{stats.failed}</p>
            </CardContent>
          </Card>
        </div>

        {/* Email Accounts */}
        <Card className="bg-white border-slate-200 shadow-sm">
          <CardHeader className="border-b border-slate-200">
            <CardTitle className="text-lg font-bold text-slate-900">Cuentas de Email</CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            {/* Add Account Form */}
            <form onSubmit={handleAddAccount} className="mb-6 p-4 bg-slate-50 rounded-lg border border-slate-200">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                <div>
                  <Label className="text-slate-700 font-medium mb-2 block">Email</Label>
                  <Input
                    type="email"
                    value={newAccount.username}
                    onChange={(e) => setNewAccount({ ...newAccount, username: e.target.value })}
                    placeholder="info@tudominio.com"
                    className="bg-white border-slate-300 text-slate-900 focus:border-[#17a2b8] focus:ring-[#17a2b8]"
                  />
                </div>
                <div>
                  <Label className="text-slate-700 font-medium mb-2 block">Contraseña</Label>
                  <Input
                    type="password"
                    value={newAccount.password}
                    onChange={(e) => setNewAccount({ ...newAccount, password: e.target.value })}
                    placeholder="••••••••"
                    className="bg-white border-slate-300 text-slate-900 focus:border-[#17a2b8] focus:ring-[#17a2b8]"
                  />
                </div>
              </div>
              <Button
                type="submit"
                disabled={loading}
                className="bg-[#17a2b8] hover:bg-[#138a9d] text-white w-full sm:w-auto"
              >
                <Plus className="w-4 h-4 mr-2" />
                Añadir Cuenta
              </Button>
            </form>

            {/* Account List */}
            {accounts.length === 0 ? (
              <p className="text-center text-slate-500 py-8">No hay cuentas de email configuradas</p>
            ) : (
              <div className="space-y-3">
                {accounts.map((account, index) => (
                  <div key={index} className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3 flex-1 min-w-0">
                        <Mail className="w-5 h-5 text-[#17a2b8] flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <p className="font-semibold text-slate-900 truncate">{account.username}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <p className="text-sm text-slate-600">
                              {showPassword[index] ? account.password : '••••••••'}
                            </p>
                            <button
                              onClick={() => setShowPassword({ ...showPassword, [index]: !showPassword[index] })}
                              className="text-slate-400 hover:text-slate-600"
                            >
                              {showPassword[index] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                            </button>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          account.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-700'
                        }`}>
                          {account.is_active ? 'Activa' : 'Inactiva'}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Email Queue */}
        <Card className="bg-white border-slate-200 shadow-sm">
          <CardHeader className="border-b border-slate-200">
            <CardTitle className="text-lg font-bold text-slate-900">Cola de Emails ({queue.length})</CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            {queue.length === 0 ? (
              <p className="text-center text-slate-500 py-8">No hay emails en cola</p>
            ) : (
              <div className="space-y-3">
                {queue.slice(0, 10).map((item, index) => (
                  <div key={index} className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-slate-900 truncate">{item.clinic_data?.clinica}</p>
                        <p className="text-sm text-slate-600 truncate">{item.clinic_data?.email}</p>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap ${
                        item.status === 'sent' ? 'bg-emerald-100 text-emerald-700' :
                        item.status === 'pending' ? 'bg-amber-100 text-amber-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {item.status === 'sent' ? 'Enviado' : item.status === 'pending' ? 'Pendiente' : 'Fallido'}
                      </span>
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

export default Config;