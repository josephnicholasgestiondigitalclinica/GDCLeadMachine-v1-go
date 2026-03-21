import React from 'react';
import Layout from '../components/Layout';
import { Card, CardContent } from '../components/ui/card';
import { Target } from 'lucide-react';

const Prospeccion = () => {
  return (
    <Layout>
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="bg-slate-900 border-slate-800 max-w-md w-full">
          <CardContent className="p-12 text-center">
            <Target className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-white mb-2">Prospección</h2>
            <p className="text-slate-400">Esta sección está en desarrollo</p>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default Prospeccion;
