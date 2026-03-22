import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Users, Target, Mail, Settings, LogOut, Upload } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Button } from './ui/button';

const Layout = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/leads', label: 'Leads', icon: Users },
    { path: '/import', label: 'Importar', icon: Upload },
    { path: '/prospeccion', label: 'Prospección', icon: Target },
    { path: '/outreach', label: 'Outreach', icon: Mail },
    { path: '/config', label: 'Config', icon: Settings }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Top Navigation */}
      <nav className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
        <div className="container mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <img 
                src="https://customer-assets.emergentagent.com/job_ecstatic-knuth-2/artifacts/u25di08h_GDC%20LOGO.jpg" 
                alt="GDC Logo" 
                className="h-10 w-auto"
              />
              <div className="hidden sm:block">
                <div className="text-slate-900 font-bold text-sm">GESTIÓN</div>
                <div className="text-[#17a2b8] font-bold text-xs -mt-1">DIGITAL CLÍNICA</div>
              </div>
            </div>

            {/* Nav Items - Desktop */}
            <div className="hidden md:flex items-center gap-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      isActive
                        ? 'bg-[#17a2b8] text-white shadow-md'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    {item.label}
                  </Link>
                );
              })}
            </div>

            {/* Logout Button */}
            <Button
              onClick={handleLogout}
              variant="ghost"
              size="sm"
              className="text-slate-600 hover:text-slate-900 hover:bg-slate-50"
            >
              <LogOut className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Logout</span>
            </Button>
          </div>

          {/* Nav Items - Mobile */}
          <div className="md:hidden flex items-center gap-1 overflow-x-auto pb-3 -mx-2 px-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex flex-col items-center gap-1 px-3 py-2 rounded-lg text-xs font-medium transition-all whitespace-nowrap ${
                    isActive
                      ? 'bg-[#17a2b8] text-white'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </Link>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 sm:px-6 py-6 sm:py-8">
        {children}
      </main>
    </div>
  );
};

export default Layout;