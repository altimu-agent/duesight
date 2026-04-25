# Hackathon Agent — Análisis de Ideas
**AI Agent Economy Hackathon · San Francisco · Abril 2026**

---

## Marco de análisis: ¿Qué validó YC W26?

El batch W26 (196 empresas, Demo Day 24 marzo 2026) muestra 5 arquetipos claros de agentes B2B que YC está financiando. Usamos esto como filtro principal — si YC ya lo validó como categoría, el mercado existe.

### Los 5 arquetipos YC W26

| Arquetipo | Empresas YC de referencia | Patrón |
|-----------|--------------------------|--------|
| **Vertical Operations Agent** | Korso (manufactura), Flott (logística), Corvera (CPG) | Automatiza un flujo operativo completo de una industria específica |
| **Intelligence & Monitoring Agent** | Pulsent (churn), Userlens (product usage), Hex (seguridad) | Monitorea señales continuamente y alerta con contexto |
| **Compliance Automation Agent** | Denki (auditoría financiera), Norm AI (compliance) | Reemplaza auditores y consultores de cumplimiento |
| **Sales Intelligence Agent** | Caretta (live coaching en llamadas) | Genera inteligencia accionable para equipos de ventas |
| **Supply Chain & Due Diligence Agent** | DiligenceSquared (due diligence), Ovlo (supply chain) | Automatiza evaluación de riesgo en cadena de valor |

---

## Las 20 Ideas — Clasificadas por arquetipo YC

| # | Idea | Arquetipo YC | Señal |
|---|------|-------------|-------|
| 1 | ISO Compliance Agent | Compliance Automation | ✅ Denki/Norm AI validan — gap: ISO específico + LATAM |
| 2 | Regulatory Compliance Oil & Gas | Compliance Automation + Vertical | ✅ Denki valida compliance — gap: vertical energía |
| 3 | Vendor/Supplier Due Diligence | Supply Chain & Due Diligence | ✅ DiligenceSquared/Ovlo validan — gap: proveedores operativos |
| 4 | Field Operations Intelligence O&G | Vertical Operations Agent | ✅ Korso/Flott validan — gap: vertical oil & gas |
| 5 | Licitaciones / Procurement Monitor | Intelligence & Monitoring | ✅ DiligenceSquared valida — gap: contratos públicos |
| 6 | Competitor Intelligence Monitor | Intelligence & Monitoring | ✅ Pulsent/Userlens validan — gap: competitive tracking SMB |
| 7 | Customer Churn Prevention | Intelligence & Monitoring | 🔴 Pulsent y Userlens lo hacen directamente |
| 8 | IT Incident Response Agent | Vertical Operations Agent | 🔴 Modern (YC W26) lo hace directamente |
| 9 | ERP Data Entry Agent | Vertical Operations Agent | 🔴 Korso lo hace para manufactura |
| 10 | Contract Review Agent | Compliance Automation | 🟡 No hay equiv. YC en español — sin validación directa |
| 11 | AI SDR Outreach | Sales Intelligence | 🔴 Saturado — múltiples YC y fuera de YC |
| 12 | Lead Enrichment Agent | Sales Intelligence | 🔴 Saturado — Arcade AI-CRM en W26 |
| 13 | Voice AI Call Center | Vertical Operations Agent | 🟡 Sin equiv. en W26 — mercado grande sin validación batch |
| 14 | Job Posting Intelligence | Intelligence & Monitoring | 🟡 Feature dentro de Pulsent, no producto standalone |
| 15 | Accounts Receivable Agent | Vertical Operations Agent | 🟡 Pace (accounting, YC W26) — adyacente |
| 16 | B2B Market Research Agent | Supply Chain & Due Diligence | 🟡 DiligenceSquared — adyacente |
| 17 | SEO Content Agent | — | 🔴 Sin arquetipo YC claro, saturado |
| 18 | Employee Onboarding Agent | Vertical Operations Agent | 🔴 Modern (YC W26) lo cubre |
| 19 | Sales Battle Card from Transcripts | Sales Intelligence | *(descartado — sin expertise de dominio)* |
| 20 | Sales Battle Card from Web | Sales Intelligence | *(descartado — sin expertise de dominio)* |

---

## Top 6 — Reencuadre YC

### 🥇 #1 — ISO Compliance Acceleration Agent
**Arquetipo YC:** Compliance Automation Agent (= Denki + Norm AI)
**Gap:** Denki hace auditoría financiera; Norm AI es horizontal. Nadie hace ISO 27001/9001 específico para SMBs en LATAM y en español.

| Forcing Question | Respuesta |
|-----------------|-----------|
| Demand Reality | CTO de startup SaaS que perdió un deal enterprise porque el cliente pedía ISO 27001 |
| Status Quo | Vanta cuesta $15K+/año (solo inglés); consultoras cobran $30-50K y tardan 9 meses |
| Desperate Specificity | Empresa de 50 personas en Quito/Bogotá/Lima que necesita ISO para entrar a un cliente banco |
| Narrowest Wedge | Gap analysis + plan de acción priorizado + templates de documentación en 10 minutos |
| Observation & Surprise | 77% de empresas enterprise exigen ISO a proveedores; el mercado LATAM no tiene solución accesible |
| Future-Fit | Plataforma multiestándar: ISO 9001, ISO 14001, SOC2, GDPR — compliance-as-a-service |

**Demo para el hackathon:** "Soy una startup SaaS de 40 personas, quiero ISO 27001" → reporte de brechas + roadmap de 90 días.
**Revenue:** $2,000/mes vs $30,000 de consultora.

---

### 🥈 #2 — Field Operations Intelligence Agent (Oil & Gas)
**Arquetipo YC:** Vertical Operations Agent (= Korso para manufactura, Flott para logística)
**Gap:** Korso automatiza quote-to-order para manufactura; nadie hace el equivalente para operaciones de campo en energía.

| Forcing Question | Respuesta |
|-----------------|-----------|
| Demand Reality | Gerente de operaciones de campo en EP Petroecuador, Repsol Ecuador, Traceoil |
| Status Quo | Reportes manuales en Excel, inspecciones en papel, coordinación por WhatsApp |
| Desperate Specificity | Superintendente de campo que necesita saber si una cuadrilla cumplió el checklist de seguridad antes de iniciar perforación |
| Narrowest Wedge | Agente que recibe reporte de campo (texto/imagen) y genera resumen estructurado + alertas de cumplimiento |
| Observation & Surprise | AltimuERP ya tiene los datos — el agente puede ser la capa de inteligencia encima del ERP |
| Future-Fit | Integración nativa con AltimuERP → ventaja competitiva real y moat de datos |

**Demo para el hackathon:** "Aquí el reporte de campo de hoy de la plataforma X" → análisis de cumplimiento, alertas y siguiente acción.
**Revenue:** $3,000-8,000/mes por empresa operadora.

---

### 🥉 #3 — Vendor/Supplier Due Diligence Agent
**Arquetipo YC:** Supply Chain & Due Diligence Agent (= DiligenceSquared + Ovlo)
**Gap:** DiligenceSquared hace due diligence de inversiones; Ovlo es supply chain interno. Nadie hace evaluación de proveedores operativos, especialmente en LATAM.

| Forcing Question | Respuesta |
|-----------------|-----------|
| Demand Reality | Gerente de compras en empresa oil & gas que evalúa 30-50 proveedores de campo al año |
| Status Quo | Proceso manual: formulario PDF + llamadas + Google + registro mercantil = 2-3 semanas |
| Desperate Specificity | Traceoil necesita calificar un proveedor de servicios de perforación antes de firmar contrato de $500K |
| Narrowest Wedge | Dado nombre de empresa: web + LinkedIn + registro mercantil + score de riesgo en 5 minutos |
| Observation & Surprise | Dun & Bradstreet no cubre bien LATAM; nadie hace esto verticalmente para oil & gas |
| Future-Fit | Integración con AltimuERP → vendor management automatizado dentro del ERP |

**Demo para el hackathon:** "Evalúa a [empresa proveedora]" → reporte con score, red flags, certificaciones, contacto.
**Revenue:** $1,500-3,000/mes para empresas con supply chain activo.

---

### 4️⃣ #4 — Regulatory Compliance Monitor (Oil & Gas)
**Arquetipo YC:** Compliance Automation + Intelligence Agent (= Denki verticalmente)
**Gap:** Denki automatiza auditoría financiera; nadie monitorea cumplimiento regulatorio para el sector energético.

| Forcing Question | Respuesta |
|-----------------|-----------|
| Demand Reality | Compliance manager en operadora de petróleo (Repsol, Andes Petroleum, Traceoil) |
| Status Quo | Abogados a $300/hora que revisan Registro Oficial manualmente; boletines manuales |
| Desperate Specificity | Empresa que recibe multa por no actualizar Plan de Manejo Ambiental antes del vencimiento |
| Narrowest Wedge | Monitor del Registro Oficial Ecuador / Diario Oficial Colombia + alertas por keyword sectorial |
| Observation & Surprise | Las multas regulatorias en oil & gas van de $50K a millones — el ROI del agente es inmediato |
| Future-Fit | Plataforma de GRC (Governance, Risk & Compliance) para el sector energético de LATAM |

**Demo para el hackathon:** "Qué cambió esta semana en regulación ambiental para petróleo en Ecuador" → reporte con impacto y acción requerida.
**Revenue:** $2,000-5,000/mes por empresa operadora.

---

### 5️⃣ #5 — Licitaciones / Government Procurement Monitor
**Arquetipo YC:** Intelligence & Monitoring Agent (patrón DiligenceSquared)
**Gap:** Ninguna empresa en YC W26 monitorea contratos públicos. Mercado de $200B+/año en LATAM completamente manual.

| Forcing Question | Respuesta |
|-----------------|-----------|
| Demand Reality | Director comercial de empresa que vende servicios al sector público o estatal |
| Status Quo | Revisar manualmente SAM.gov, SERCOP, Secop, Compranet cada semana — o contratar a alguien para eso |
| Desperate Specificity | Traceoil pierde licitaciones de EP Petroecuador porque se entera 2 días antes del cierre |
| Narrowest Wedge | Monitor de SERCOP (Ecuador) + SAM.gov + alertas diarias filtradas por categoría |
| Observation & Surprise | El gobierno publica todo — los datos son públicos. El problema es el volumen y el ruido |
| Future-Fit | Auto-draft de propuesta inicial basado en RFP + historial de precios ganadores |

**Demo para el hackathon:** "Encuentra licitaciones relevantes para servicios de campo en oil & gas esta semana" → lista rankeada con match score.
**Revenue:** $500-1,500/mes por empresa con equipo comercial.

---

### 6️⃣ #6 — Competitor Intelligence Monitor
**Arquetipo YC:** Intelligence & Monitoring Agent (= Pulsent, Userlens)
**Gap:** Pulsent/Userlens monitorean tus propios clientes. Nadie en W26 hace competitive intelligence externa para SMBs.

| Forcing Question | Respuesta |
|-----------------|-----------|
| Demand Reality | Product Manager o CMO de SaaS en crecimiento que necesita saber qué hace la competencia |
| Status Quo | Crayon o Klue cuestan $15K+/año; alternativa = alguien en el equipo googleando manualmente |
| Desperate Specificity | PM que se enteró por un cliente que un competidor lanzó una feature clave la semana pasada |
| Narrowest Wedge | Monitor semanal de pricing page + job posts + G2 reviews de 3 competidores → digest por email |
| Observation & Surprise | SMBs no tienen acceso a Crayon/Klue — el mercado sub-$1K/mes está completamente vacío |
| Future-Fit | Intel platform con análisis de tendencias, predicción de movimientos, alertas de pricing |

**Demo para el hackathon:** "Trackea a [competidor A] y [competidor B] esta semana" → reporte con cambios detectados.
**Revenue:** $500/mes por empresa.

---

## Recomendación según perfil

| Si quieres... | Idea |
|--------------|------|
| Máxima alineación con tu expertise (oil & gas + ERP) | **#2 Field Ops** o **#4 Regulatory Compliance** |
| Mayor mercado y más universal | **#1 ISO Compliance** |
| Demo más impactante para jueces SF | **#1 ISO Compliance** o **#3 Vendor Due Diligence** |
| Diferenciador único que nadie más va a tener | **#5 Licitaciones** o **#4 Regulatory O&G** |
| Mejor negocio post-hackathon | **#1 ISO Compliance** ($10B+ de mercado) |

---

*Análisis generado por altimu-agent · Abril 2026*
*Framework: YC W26 Archetypes (196 empresas, Demo Day 24 marzo 2026)*
