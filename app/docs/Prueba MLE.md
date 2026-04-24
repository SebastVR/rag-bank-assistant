PRUEBA TÉCNICA 
SISTEMA RAG CON WEB SCRAPING 
Rol: Machine Learning Engineer / AI Emngineer 
Modalidad: Individual, entrega en repositorio (GitHub, GitLab, Bitbucket o similar) 
Tiempo estimado: 2 – 3 días 
CONTEXTO 
BBVA Colombia necesita un asistente conversacional que permita a usuarios internos consultar 
información publicada en su sitio web institucional (https://www.bbva.com.co/), sin depender 
de búsquedas manuales.  
¿QUÉ DEBES HACER? 
Un sistema RAG (Retrieval-Augmented Generation) en Python que tenga las siguientes 
funcionalidades: 
1. Extraer información del sitio https://www.bbva.com.co/ mediante Web Scraping. (Puede 
ser de otro banco) 
2. Almacenar los datos scrapeados en local (Crudos y limpios). 
3. Vectorizar e indexar ese contenido en una base de datos vectorial de tu elección. 
4. Exponer una interfaz conversacional minimalista donde el usuario pueda hacer 
preguntas sobre el contenido del sitio. 
5. Mantener el historial de conversación de acuerdo a un ID, teniendo en cuenta los N 
mensajes anteriores (N configurable). 
REQUISITOS OBLIGATORIOS 
• Lenguaje: Python. El resto del stack es completamente libre. 
• Dockerización: El proyecto debe correr completamente con Docker. Se espera al 
menos un Dockerfile y un docker-compose.yml que levante todos los servicios 
necesarios si aplica (aplicación, base de datos vectorial, etc.) con un solo comando. 
• Repositorio con historial: El código debe estar en un repositorio público (GitHub, 
GitLab, Bitbucket o similar). Se evaluará el historial de commits: se espera ver una 
progresión lógica del trabajo, no un único commit con todo el código. Los mensajes de 
commit deben ser descriptivos. 
• Patrones de diseño: Implementa al menos 3 patrones de diseño (creacionales, 
estructurales o comportamentales). Documentar cuáles se usó y por qué, en el 
README. 
• Historial de conversación: El sistema debe recordar el contexto de mensajes previos 
dentro de una sesión y persistir el historial de conversaciones. 
• Interfaz: Puede ser CLI, una UI web sencilla o un notebook interactivo. Lo importante 
es que sea funcional y limpia, no que sea bonita. 
• Herramientas sin costo preferidas: Se valoran positivamente opciones como modelos 
open source, embeddings gratuitos y bases de datos vectoriales con tier gratuito o self
hosted. El uso de APIs de pago es válido, pero no suma puntos adicionales. 
• Análisis de datos: Se debe incluir una funcionaldiad que me permita recorrer el 
histórico de conversaciones para extraer métricas y valores de impacto. 
• README: El README debe permitir que cualquier persona pueda levantar y usar el 
sistema desde cero. Como mínimo debería incluir: 
• Requisitos previos (Docker, variables de entorno necesarias, etc.). 
• Instrucciones paso a paso para clonar el repo, configurar el entorno y levantar el 
sistema con Docker. 
• Cómo usar la interfaz conversacional una vez el sistema está corriendo. 
• Patrones de diseño usados: cuáles son, dónde están aplicados y por qué se 
eligieron. 
• Stack tecnológico elegido y justificación breve de cada decisión. 
• Limitaciones conocidas o decisiones de diseño relevantes. 
• Futuras mejoras del sistema 
BONUS (SUMA PUNTOS) 
• Implementación de un reranker para mejorar la relevancia de los resultados 
recuperados antes de pasarlos al LLM. 
• Manejo de errores. 
• Configuración externalizada (variables de entorno o archivo .env) para parámetros como 
N mensajes, modelo, chunk size, etc. 
ENTREGABLES 
1. Repositorio con el código fuente y el historial de commits visible. 
2. README completo según lo descrito arriba. 
FECHA DE ENTREGA: A más tardar miércoles 15 de abril a las 11:59 PM 
Notas finales 
• No hay una única solución correcta. Se valora la capacidad de tomar decisiones 
técnicas razonadas y defenderlas. 
• Si tomaste un atajo o dejaste algo sin implementar, menciónalo en el README. La 
honestidad cuenta. 
• Ante cualquier ambigüedad en los requerimientos, documenta el supuesto que asumiste 
y sigue adelante.