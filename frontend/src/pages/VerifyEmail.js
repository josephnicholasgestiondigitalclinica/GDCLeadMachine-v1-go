import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Shield, ArrowLeft } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const VerifyEmail = () => {
  const [code, setCode] = useState(['', '', '', '', '', '']);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { verifyEmail } = useAuth();
  const { toast } = useToast();
  const email = location.state?.email || 'test@example.com';

  const handleChange = (index, value) => {
    if (value.length > 1) value = value[0];
    const newCode = [...code];
    newCode[index] = value;
    setCode(newCode);

    // Auto-focus next input
    if (value && index < 5) {
      document.getElementById(`code-${index + 1}`)?.focus();
    }
  };

  const handleKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !code[index] && index > 0) {
      document.getElementById(`code-${index - 1}`)?.focus();
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    const verificationCode = code.join('');
    
    if (verificationCode.length !== 6) {
      toast({
        title: 'Error',
        description: 'Por favor ingrese el código completo',
        variant: 'destructive'
      });
      return;
    }

    setLoading(true);
    try {
      await verifyEmail(verificationCode);
      toast({
        title: 'Email verificado',
        description: 'Bienvenido a LeadMachine GDC'
      });
      navigate('/dashboard');
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Código inválido',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-lg p-8">
          {/* Back Button */}
          <Link
            to="/login"
            className="inline-flex items-center text-slate-600 hover:text-slate-900 mb-6 text-sm"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to sign in
          </Link>

          {/* Icon */}
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center">
              <Shield className="w-8 h-8 text-slate-700" />
            </div>
          </div>

          {/* Title */}
          <h1 className="text-2xl font-semibold text-center text-slate-900 mb-2">
            Verify your email
          </h1>
          <p className="text-center text-slate-600 mb-8 text-sm">
            We've sent a 6-digit code to <br />
            <span className="font-medium text-slate-900">{email}</span>
          </p>

          {/* Code Input */}
          <form onSubmit={handleVerify}>
            <div className="flex gap-2 justify-center mb-4">
              {code.map((digit, index) => (
                <Input
                  key={index}
                  id={`code-${index}`}
                  type="text"
                  maxLength={1}
                  value={digit}
                  onChange={(e) => handleChange(index, e.target.value)}
                  onKeyDown={(e) => handleKeyDown(index, e)}
                  className="w-12 h-12 text-center text-lg font-semibold border-slate-200"
                  required
                />
              ))}
            </div>

            <p className="text-center text-xs text-slate-500 mb-6">
              Enter the verification code sent to your email
            </p>

            <Button
              type="submit"
              className="w-full h-11 bg-slate-900 hover:bg-slate-800 text-white"
              disabled={loading}
            >
              {loading ? 'Verifying...' : 'Verify email'}
            </Button>
          </form>

          {/* Resend */}
          <div className="text-center mt-6 text-sm text-slate-600">
            Didn't receive the code?{' '}
            <button className="text-slate-900 font-medium hover:underline">
              Resend
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VerifyEmail;
