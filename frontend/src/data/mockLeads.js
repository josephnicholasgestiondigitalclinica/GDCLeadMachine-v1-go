export const mockLeads = [
  { id: 1, clinica: 'Centro Médico de Asturias', telefono: '985 22 22 22', ciudad: 'Oviedo', email: 'info@centromedicoasturias.com', score: null, estado: 'Sin contactar' },
  { id: 2, clinica: 'Policlínicas Oviedo', telefono: '985 22 22 22', ciudad: 'Oviedo', email: 'info@policlinicasoviedo.com', score: null, estado: 'Sin contactar' },
  { id: 3, clinica: 'Aevo Salud', telefono: '985 22 22 22', ciudad: 'Oviedo', email: 'info@aevo-salud.com', score: null, estado: 'Sin contactar' },
  { id: 4, clinica: 'Clínica Nova Oviedo', telefono: '985 22 22 22', ciudad: 'Oviedo', email: 'info@clinicanovaoviedo.com', score: null, estado: 'Sin contactar' },
  { id: 5, clinica: 'Clínica Rehberger López-Fanjul', telefono: '985 22 22 22', ciudad: 'Oviedo', email: 'info@clinicarehberger.com', score: null, estado: 'Sin contactar' },
  { id: 6, clinica: 'Clínica Oftalmológica Elche', telefono: '965 45 88 47', ciudad: 'Elche', email: 'info@oftalmologoenelche.com', score: 8, estado: 'Sin contactar' },
  { id: 7, clinica: 'Innova Ocular Clínica Dr. Soler', telefono: '965 45 00 00', ciudad: 'Elche', email: 'info@innovaocular.com', score: 7, estado: 'Sin contactar' },
  { id: 8, clinica: 'Hospital Ribera Povisa', telefono: '986 12 34 56', ciudad: 'Vigo', email: 'info@povisa.es', score: null, estado: 'Sin contactar' },
  { id: 9, clinica: 'Clínica Villoria Oftalmólogos Vigo', telefono: '986 12 34 56', ciudad: 'Vigo', email: 'info@clinicavilloria.com', score: 9, estado: 'Sin contactar' },
  { id: 10, clinica: 'Instituto Oftalmológico Bilbao', telefono: '944 750 000', ciudad: 'Bilbao', email: 'info@iob.es', score: null, estado: 'Sin contactar' }
];

export const allMockLeads = Array.from({ length: 919 }, (_, i) => {
  const cities = ['Oviedo', 'Elche', 'Vigo', 'Bilbao', 'Las Palmas', 'Málaga', 'Sevilla', 'Valencia', 'Barcelona', 'Madrid'];
  const types = ['Clínica', 'Hospital', 'Centro Médico', 'Policlínica', 'Instituto'];
  const specialties = ['Oftalmológica', 'Dental', 'Fisioterapia', 'Dermatológica', 'Traumatología', 'Psicología'];
  
  const city = cities[i % cities.length];
  const type = types[Math.floor(Math.random() * types.length)];
  const specialty = specialties[Math.floor(Math.random() * specialties.length)];
  const hasScore = Math.random() > 0.85;
  
  return {
    id: i + 1,
    clinica: `${type} ${specialty} ${city} ${i + 1}`,
    telefono: `9${Math.floor(10 + Math.random() * 89)} ${Math.floor(10 + Math.random() * 89)} ${Math.floor(10 + Math.random() * 89)} ${Math.floor(10 + Math.random() * 89)}`,
    ciudad: city,
    email: `info@clinica${i + 1}.com`,
    score: hasScore ? Math.floor(Math.random() * 4) + 7 : null,
    estado: 'Sin contactar'
  };
});
