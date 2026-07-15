# Challenge_Alura_Agent_bimbambuy_support
Asistente de conocimiento impulsado por IA que utiliza Generación Aumentada por Recuperación (RAG) para la documentación de atención al cliente de una e-commerce llamada: BimBam Buy.
Se utiliza Oracle Autonomous Database (vía Oracle APEX/ORDS) como servicio del ecosistema OCI para el registro de ejecución del agente, cumpliendo el requisito de despliegue con al menos un servicio OCI, mientras el hosting de la aplicación se realiza en Railway."

🤖 BimBam Buy Support
Asistente Inteligente para Atención al Cliente basado en RAG

Proyecto desarrollado para el Challenge Alura Agent del programa Oracle Next Education (ONE) en colaboración con Alura Latam.

📑 Tabla de contenido

Descripción del proyecto
Contexto del Challenge
Problema de negocio
Solución propuesta
Objetivos
Arquitectura de la solución
Flujo de funcionamiento del agente RAG
Tecnologías utilizadas
Base documental
Ejemplos de consultas
Beneficios de la solución
Instalación y ejecución
Estructura del proyecto
Mejoras futuras
Autora

📖 Descripción del proyecto

BimBam Buy Support es un asistente inteligente desarrollado para responder consultas en lenguaje natural sobre la documentación oficial de una empresa ficticia de comercio electrónico llamada BimBam Buy.

La solución implementa la arquitectura Retrieval-Augmented Generation (RAG), combinando búsqueda semántica con modelos de lenguaje para generar respuestas precisas y fundamentadas a partir de documentos corporativos.

El sistema fue desarrollado en Python, utiliza Cohere para la generación de embeddings y respuestas mediante IA, LangChain para la orquestación del flujo RAG, ChromaDB como base de datos vectorial y una interfaz web desarrollada con Streamlit, desplegada en Railway para facilitar el acceso desde cualquier navegador.

🎯 Contexto del Challenge

El Challenge Alura Agent busca aplicar los conocimientos adquiridos durante la formación en Inteligencia Artificial mediante la construcción de un asistente capaz de comprender documentos empresariales y responder preguntas utilizando modelos de lenguaje.

Durante el desarrollo se implementaron las principales etapas de una solución basada en IA Generativa:

Organización de la documentación.
Extracción y procesamiento de documentos PDF.
División del contenido en fragmentos (Chunking).
Generación de embeddings.
Almacenamiento en una base de datos vectorial.
Recuperación de información mediante RAG.
Generación de respuestas utilizando un modelo de lenguaje.
Desarrollo de una interfaz web interactiva.
Publicación de la aplicación en la nube.
💼 Problema de negocio

Las empresas administran una gran cantidad de documentos relacionados con políticas, garantías, procedimientos, envíos, devoluciones y preguntas frecuentes.

Cuando un colaborador o cliente necesita información específica, normalmente debe consultar múltiples documentos antes de encontrar la respuesta correcta, provocando:

Mayor tiempo de búsqueda.
Información inconsistente.
Sobrecarga del equipo de atención al cliente.
Disminución de la productividad.

💡 Solución propuesta

BimBam Buy Support centraliza el conocimiento corporativo en una base de conocimiento inteligente.

Mediante la arquitectura Retrieval-Augmented Generation (RAG), el asistente identifica automáticamente los fragmentos más relevantes de la documentación almacenada en la base vectorial y genera respuestas fundamentadas únicamente en la información disponible, proporcionando respuestas rápidas, consistentes y confiables.

🎯 Objetivos
Objetivo general

Desarrollar un asistente inteligente capaz de responder preguntas sobre la documentación corporativa de BimBam Buy mediante la arquitectura Retrieval-Augmented Generation (RAG).

Objetivos específicos
Automatizar la consulta de documentación corporativa.
Procesar documentos PDF utilizando Python.
Generar embeddings utilizando Cohere.
Implementar una base vectorial con ChromaDB.
Construir un flujo RAG mediante LangChain.
Generar respuestas utilizando modelos de lenguaje.
Desarrollar una interfaz web interactiva con Streamlit.
Publicar la aplicación utilizando Railway.

🏗 Arquitectura de la solución

<img width="310" height="660" alt="image" src="https://github.com/user-attachments/assets/f9aff738-f21d-4085-8db9-8cc8d40b90d6" />



🔄Flujo de funcionamiento del agente RAG

El funcionamiento del asistente sigue una arquitectura Retrieval-Augmented Generation (RAG) que combina recuperación de información y generación de lenguaje natural.

1️⃣ Ingesta de documentos

Los documentos PDF de la empresa se almacenan dentro de la carpeta knowledge_base.

El script ingest.py:

Lee todos los documentos.
Extrae el texto.
Divide el contenido en fragmentos (chunks).
Genera embeddings utilizando Cohere.
Almacena los vectores en ChromaDB.

Este proceso solo se ejecuta cuando se agregan o actualizan documentos.

2️⃣ Consulta del usuario

El usuario realiza una pregunta desde la interfaz desarrollada con Streamlit.

Ejemplo:

¿Cuál es el plazo para solicitar un reembolso?

3️⃣ Búsqueda semántica

La pregunta del usuario también se transforma en un embedding mediante Cohere.

Posteriormente, LangChain consulta ChromaDB para recuperar únicamente los fragmentos de documentos con mayor similitud semántica.

4️⃣ Generación de la respuesta

Los fragmentos recuperados se envían junto con la consulta al modelo de lenguaje de Cohere.

El modelo genera una respuesta utilizando exclusivamente el contexto recuperado, reduciendo el riesgo de respuestas incorrectas o inventadas.

5️⃣ Presentación al usuario

Finalmente, la respuesta se muestra en la interfaz web desarrollada con Streamlit, ofreciendo una experiencia conversacional sencilla e intuitiva.

🛠 Tecnologías utilizadas

Tecnología	Función
Python	Desarrollo de la aplicación
LangChain	Orquestación del flujo RAG
Cohere	Generación de embeddings y respuestas mediante IA
ChromaDB	Base de datos vectorial
PyPDF	Procesamiento de documentos PDF
Streamlit	Interfaz web del asistente
Railway	Despliegue de la aplicación
Git	Control de versiones
GitHub	Gestión del repositorio
Visual Studio Code	Entorno de desarrollo
Oracle APEX	Herramienta utilizada como parte del ecosistema Oracle durante el desarrollo y presentación del Challenge

📚 Base documental

El conocimiento del asistente se construye a partir de documentación oficial de BimBam Buy:

Política de Reembolsos y Devoluciones.
Programa de Afiliados.
Guía de Envíos.
Métodos de Pago.
Manual de Garantías.
Customer Service and Claims Policy.

💬 Ejemplos de consultas

El asistente puede responder preguntas como:

¿Cómo puedo solicitar un reembolso?
¿Cuáles son los métodos de pago disponibles?
¿Qué cubre la garantía?
¿Cuánto tarda un envío internacional?
¿Cómo puedo presentar un reclamo?
¿Qué sucede si recibo un producto dañado?
¿Cómo funciona el programa de afiliados?

✅ Beneficios de la solución

Centraliza el conocimiento corporativo.
Reduce el tiempo de búsqueda de información.
Mejora la experiencia del cliente.
Disminuye la carga del equipo de soporte.
Facilita la incorporación de nuevos documentos.
Genera respuestas consistentes y fundamentadas.
Escala fácilmente conforme crece la organización.

🚀 Instalación y ejecución
1. Clonar el repositorio
   git clone <URL_DEL_REPOSITORIO>
2. Crear un entorno virtual
   python -m venv .venv
3. Activarlo
   Windows
   .venv\Scripts\activate
   
   Linux/macOS
   source .venv/bin/activate
4. Instalar dependencias
   pip install -r requirements.txt
6. Configurar variables de entorno
   Crear un archivo .env con las credenciales necesarias (por ejemplo, la API Key de Cohere).
7. Generar la base vectorial
   python src/ingest.py
8. Ejecutar la aplicación
   streamlit run app.py
Una vez iniciada, la aplicación podrá utilizarse desde el navegador o accederse mediante la versión desplegada en Railway.



🚀 Mejoras futuras
Historial de conversaciones.
Gestión de usuarios y autenticación.
Carga dinámica de nuevos documentos.
Actualización automática de la base documental.
Soporte para documentos Word, Excel y PowerPoint.
Panel de métricas y analítica de consultas.
Integración con Microsoft Teams y Slack.
Soporte para múltiples idiomas.
Incorporación de memoria conversacional.
Implementación de técnicas avanzadas de RAG, como Hybrid Search, Re-ranking o Self-RAG.


📂 Estructura del proyecto


<img width="445" height="597" alt="image" src="https://github.com/user-attachments/assets/623eacaf-6e5f-4ada-ac7a-308cec245d5c" />



👩‍💻 Autora

Priscila Castellón Vásquez

Proyecto desarrollado para el Challenge Alura Agent del programa Oracle Next Education (ONE) en colaboración con Alura Latam.

