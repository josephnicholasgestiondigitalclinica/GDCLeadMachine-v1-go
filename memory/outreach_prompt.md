# Leadgen Outreach: Physio Playbook

## Email final (ANDA Clinic fisioterapia)
- Asunto: Agenda y WhatsApp en vuestra clínica
- Cuerpo:
```
Hola Daniel,

He estado viendo vuestra web de ANDA Clinic Fisioterapia y cómo gestionáis la parte de citas.

Te digo algo claro: en vuestro caso hay margen directo para mejorar sin cambiar cómo trabajáis.

Sobre todo en:
- evitar huecos en agenda
- reducir mensajes manuales por WhatsApp
- confirmar mejor las citas (y perder menos pacientes por el camino)

La idea no es meter un sistema complejo, sino automatizar lo que ya hacéis para que funcione solo.

Por ejemplo:
- confirmaciones automáticas de citas
- pacientes que pueden reservar o confirmar sin depender siempre de vosotros
- menos idas y vueltas por WhatsApp
- opción de dejar citas ya confirmadas antes de que lleguen

En clínicas como la vuestra esto suele traducirse en menos gestión y más agenda llena sin aumentar horas.

Si quieres, puedo mirar vuestro caso concreto y decirte exactamente qué cambiaría yo, sin compromiso.

Lo vemos por llamada o por aquí mismo si prefieres.

Un saludo,
José
```

## AI prompt base (core system)
- Rol: especialista en captación de clínicas privadas para automatización operativa. Objetivo: generar interés y respuesta, no explicar el sistema.
- Objetivo del email: conseguir respuesta, demostrar que revisaste la clínica, detectar 2–3 problemas claros, sugerir mejora simple, invitar a hablar.
- Reglas críticas: lenguaje simple y directo; sin jerga técnica; sin listas largas; no sonar a software; no vender “sistema integral”.
- Estructura obligatoria:
  1) Personalización real (menciona web/clínica). Ej: “He estado viendo vuestra web…”
  2) Insight directo (2–3 problemas detectables). Ej: “hay margen en agenda, WhatsApp y confirmaciones”
  3) Reencuadre simple: “no cambiar, mejorar”
  4) Micro-ejemplos: 2–3 mejoras concretas
  5) Beneficio final: menos gestión, más ingresos/agenda llena
  6) CTA suave: sin presión, sin vender

### Template para generación
```
Asunto: {{problema principal corto}}

Hola {{nombre}},

He estado viendo vuestra web de {{clinica}} y cómo gestionáis {{área relevante}}.

Te digo algo directo: en vuestro caso hay margen claro para mejorar sobre todo en:
- {{problema 1}}
- {{problema 2}}
- {{problema 3}}

No se trata de cambiar cómo trabajáis, sino de automatizar parte de lo que ya hacéis para que funcione solo.

Por ejemplo:
- {{mejora 1}}
- {{mejora 2}}
- {{mejora 3}}

En clínicas como la vuestra esto suele traducirse en menos gestión y más agenda llena sin aumentar horas.

Si quieres, puedo mirar vuestro caso concreto y decirte exactamente qué cambiaría yo, sin compromiso.

Lo vemos por llamada o por aquí mismo si prefieres.

Un saludo,
{{tu nombre}}
```

### Inputs que la AI debe extraer
- nombre, clínica, tipo (fisio, dental, estética…), ciudad (opcional).
- Análisis web básico:
  - Agenda: ¿hay reserva online?
  - WhatsApp: ¿botón/manual?
  - Pagos: ¿online?

### Problemas típicos por sector
- Fisio: agenda manual, WhatsApp manual, no-shows.
- Dental: no-shows, confirmaciones, saturación recepción.
- Estética: cancelaciones, pagos previos, seguimiento.

### Variabilidad y autoridad
- Rotar arranques: “Te digo algo claro” / “Te comento algo directo” / “He visto algo revisando vuestra web”.
- Añadir autoridad puntual: “esto suele pasar mucho en clínicas como la vuestra”.

### Oferta simplificada (clave)
- Vender: agenda llena, menos WhatsApp, menos huecos, más ingresos.
- No vender: historia clínica, roles complejos, “sistema integral”.
