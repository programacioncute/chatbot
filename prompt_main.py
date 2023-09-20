prompts = {
    "prompt_sql":"""
    Cree consultas de postgresql basadas en la pregunta del usuario, la información sobre las variables y sus columnas y la siguiente información que conoce sobre la base de datos.

    Informacion de la tabla:
        TABLE NAME: change_request
        Columnas:
            numero[str]: Numero unico del ticket o folio.
            creado [datetime]: Fecha de creacion del ticket o folio
            estado [str]: Estado en el que se encuentra el ticket
            efectividad_del_cambio [str]: Indica si cambio o modificación tuvo exito o fracaso
            ubicacion_ci [str]: Lugar en el que se realizo el cambio
            tipo [str]: Tipo de solicitud
            categoria [str]: Categoria del tipo solicitud
            sub_categoria [str]: Subcategoria del tipo de solicitud
            suspension_del_servicio [str]: Indica si se tiene que suspender algun servidor o aplicación
            inicio_de_suspension [datetime]: Fecha en la que se iniciara la suspension del servicio
            fin_de_la_suspension [datetime]: Fecha en la que se finalizara la suspension del servicio
            clasificacion [str]: Indica si es un cambio que esta dentro de una categoria
            cumplio_con_la_documentacion_requerida [str]: Indicardor de si el ticket presenta la documentación requerida
            fecha_de_inicio [datetime]: Fecha en la que se iniciara el cambio
            fecha_de_fin [datetime]: Fecha en la que se finalizara el cambio
            area [str]: Area que solicito el cambio
            solicitado_por [str]: Nombre de la persona que solicito el cambio
            riesgo [str]: Nivel de riesgo que tiene la modificación o actualización
            respeto_la_ventana_de_suspension [str]: Menciona si se realizo en el intervalo de tiempo programado
            numero_de_contingencias [int]: Cantidad de incidentes por el cambio.
            servicios_operando_correctamente [str]: Se menciona si los servicios que dependientes estan funcionando correctamente
            impacto_en_otros_servicios [str]: Se menciona si existio algun problema con la actualización o modificación
            matriz_de_usuarios [str]: Indicador de si se tiene una matriz de usuarios
            impacto [str]: Descripcion del impacto que tuvieron las contigencias
            urgencia [str]: Descripcion de la urgencia de las contingencias
            prioridad [str]: Categoria de la prioridad del cambio
            fecha_de_evaluacion_del_cambio [datetime]: Fecha de evaluación del cambio
            primero_responsable_de_autorizar [str]: Nombre del grupo que autorizo el ticket, su dominio es [ECAB, CAB, ""]
            ultimo_responsable_de_autorizar [str]: Nombre del ultimo grupo o persona que autorizo el ticket, su dominio es [CAB,  CAB CONTIENGENCIA,  ECAB,  ECAB SUBDIRECCION,  ""]
            nombre_del_responsable_de_autorizar [str]: Nombre de la persona o grupo de personas que autorizo el ticket
            usuarios [str]: Nombre de las personas que levantaron el ticket
            subdireccion [str]: Subdirección a la que pertenece el area donde se realizara la modificación o el cambio
            estado_de_conflicto [str]: Se determina si el cambio entra en conflicto con otros cambios o modificaciones
            grupo_de_asignacion [str]: Equipo al que se le asignara el cambio o modificación
            asignado_a [str]: Nombre de la persona al que se le asignara el cambio o modificación
            se_aplico_plan_de_contingencia [str]: Campo que indica si al tener un problema en la modificación o cambio se aplico el plan de contingencia
    
    Informacion:
        Al finalizar las consultas SQL se debe usar el caracter ";"
        No generes consultas que no esten relacionadas con la informacion que no este mencionada en la pregunta
        El formato de las fechas esta en dd/mm/yyyy HH:MM:SS
        No debes de colocar alias en las consultas SQL
        No quites los acentos de las preguntas
        Si la pregunta contiene la palabra "tiene" o "esta" debes de usar LIKE

        Puedes usar las siguientes funciones: [AVG(), SUM(), COUNT(), FIRST(), LAST(), MAX(), MIN(), ROUND, LIKE]

        Ejemplo:
            Pregunta: Cual es el ticket mas reciente
            Reason: El usuario quiere saber cual es el ultimo ticket que se genero
            Query: SELECT numero AS Ticket, MAX(creado) AS Fecha_Creacion FROM change_request GROUP BY numero ORDER BY Fecha_Creacion DESC LIMIT 1;
        
        Basado en la informacion previa, genera una consulta SQL que se conecte a la base de datos que el usuario esa preguntando.

        Una consulta para responder lo que el usuario quiere saber: {question}\nSELECT
""",
"prompt_response":"""
- Role: Eres un especialista en datos que tiene excelentes habilidades de responsabilidad y es capaz de explicar los resultados de las consultas a los usuarios comerciales en función de sus preguntas y la información de la tabla.

    - Data:
            - Query: {query};
            - Query Respuesta: {result};

    - Instrucciones:
            - Responde unicamente preguntas relacionadas con la pregunta
            - Si la consulta es vacia, di lo siguiente: 'Lo siento, puedes intentar describir mejor la pregunta o escribirla de otra manera'.
            - Si la respuesta tiene mas de diez resultados, entonces muestra los primeros diez valores;
            - Especifica el resultado de la consulta tanto como pueda para el usuario.
            - Siempre debes de decir: `De acuerdo a la pregunta este es el resultado, `;
            - No hagas saltos de linea o uses '\n';
            - Da contexto de la informacion.

    - Note: Si el resultado probable es Ninguno, recomiende al usuario que repita la pregunta diciendo también que tal vez no existe información suficiente en los datos.

    - AL FINAL DE LA RESPUESTA, AÑADIR:: "Para más información, por favor especifique la pregunta."

    Explicar los términos seleccionados en base a la pregunta.

    - PON TU RESULTADO EN UNA ORACIÓN CON UN MÁXIMO DE 80 PALABRAS. NO SALTE LINEAS

    - {question}
    - Respuesta:
""",
"semi_prompt_1":"""

        Below we have some SQL datatable columns with their unique values 

        Valores unicos para estado:
                        [Autorizacion, Closed, Canceled,  Evaluar,  Implementar, Review,  Nuevo, Programado]

        Valores unicos para efectividad_del_cambio:
                        [Exitoso, No exitoso, Null]
        
        Valores unicos para tipo:
                        [Emergencia, Normal]
        
        Valores unicos para categoria:
                        [Infraestructura, BCP, Aplicaciones, Servicios a inmuebles]
        
        Valores unicos para suspension_del_servicio:
                        [Si, No, No Aplica]
        
        Valores unicos para clasificacion:
                        [Proyecto, Continuidad, No aplica]
        
        Valores unicos para cumplio_con_la_documentacion_requerida:
                        [Si, No, No aplica, ""]
        
        Valores unicos para area:
                        [Arquitectura Empresarial, Arquitectura IT, Arquitectura y Soporte de Afilacion, Arquitectura Soluciones de Negocio, 
                        Competitividad Comercial, Competitividad Comercial, Desarrollo Móvil, Desarrollo y Soporte, Devops, Innovación y Desarrollo Digital, 
                        Innovacion y microservicios, Operación IT, Soporte Técnico, Planeacion IT, Producción y Control de Cambios, Seguridad IT, 
                        Servicios a Inmuebles, Seguridad de la informacion, Sistemas Administrativos, Soporte Técnico]
        
        Algunos valores de solicitado_por:
                        [MARTIN FRANCISCO GUZMAN ULLOA,ALEJANDRO  MUÑOZ  NAJERA, JOSE DANIEL GLORIA BECERRIL, ANA LAURA RODRIGUEZ LOZANO, GERARDO CERVANTES GASCON]
        
        Valores unicos para riesgo:
                        [Ato, Bajo, Moderado]
        
        Valores unicos para respeto_la_ventana_de_suspension:
                        [Si, No, No Aplica,Null]

        Valores unicos para servicios_operando_correctamente:
                        [Si, No, No se confirmo, ""]
        
        Valores unicos para impacto_en_otros_servicios:
                        [Si, No, ""]
        
        Valores unicos para matriz_de_usuarios:
                        [Si, No, No Aplica, ""]
        
        Valores unicos para impacto:
                        [1. No conlleva impactos severos,  2.Puede repercutir en la calidad ofrecida, 3.Causa pérdidas significativas en ingresos e incapacita servicios]
        
        Valores unicos para urgencia:
                        [1. Puede esperar a la siguiente versión, 2.No debe esperar la siguiente versión,  3.Requerimiento urgente]
        
        Valores unicos para prioridad:
                        [1 - Urgente,  2 - Alta,  Media, Baja]

        Valores unicos para primero_Responsable_de_Autorizar:
                        [ECAB, CAB, ""]
        
        Algunos valores de ultimo_Responsable_de_autorizar:
                        [CAB,  CAB CONTIENGENCIA,  ECAB,  ECAB SUBDIRECCION,  ""]
        
        Algunos valores de nombre_del_responsable_de_autorizar:
                        [LEVY JASEF PONCE MARTINEZ, PAULA DANIELA ORTIZ LOPEZ, DAVID RAMON HERNANDEZ LEON, JUAN ALBERTO MENDEZ QUINTANA]

        Valores unicos para subdireccion:
                        [Desarrollo, Infraestructura, Digital,Servicios a inmuebles, Arquitectura, ""]
        
        Valores unicos para estado_de_conflicto:
                        [Sin conflicto, Conflicto, No ejecutar]
        
        Valores unicos para grupo_de_asignacion:
                        [Change Management, DevOps]
        
        Algunos valores de asignado_a:
                        [BEATRIZ GUADALUPE VALTIERRA ROMERO, PAULA DANIELA ORTIZ LOPEZ, HUGO BECERRA TRUJILLO]
        
        Valores unicos para se_aplico_plan_de_contingencia:
                        [Si, No, ""]

Basado en la información anterior comprueba si la {query} es correcta para 
resolver la pregunta {question} y genera de 
nuevo la respuesta:\nSELECT
""",
"prompt_response_2":"""
Instrucciones:
Responda únicamente preguntas relacionadas con la pregunta.
Si la respuesta a la consulta es nula, NULL, Null, None, NONE o none, no puede especificar información para ese término y recomienda al usuario que repita la pregunta y también diga que tal vez no haya información suficiente en los datos.
Si su respuesta tiene más de una información, cite al menos un valor
Sea útil, especifique tanta información como pueda para el usuario.
RESPONDA SIEMPRE AL USUARIO EXPLICANDO LAS RELACIONES ENTRE LAS VARIABLES Y LA PREGUNTA

AL INICIO DE SU RESPUESTA ACLARE SIEMPRE LA PREGUNTA REALIZADA

SIEMPRE ESPECIFICA FECHAS EN LAS RESPUESTAS

SIEMPRE SEA CONCISO EN SUS RESPUESTAS ASEGURÁNDOSE DE QUE TODA LA INFORMACIÓN NECESARIA ESTÉ ALLÍ

SI EL RESULTADO DE UNA CONSULTA ES NINGUNO O 0, SIEMPRE DICE QUE FALTA LA INFORMACIÓN DE LA PREGUNTA EN LA BASE DE DATOS. EN ESTE CASO EVITE INFORMAR VALORES. INFORMAR SOLO QUE FALTA LA INFORMACIÓN

Texto:

    Cosulta: {query}
    Respuesta de la consulta: {result} 

ANSWER ONLY THE QUESTION

SIEMPRE AL FINAL DE LA RESPUESTA EXPLICA ALGUNA INFORMACIÓN RELACIONADA CON LA PREGUNTA E INVITA AL USUARIO A INVESTIGAR MÁS CON OTRA PREGUNTA
RESPONDA SIEMPRE EN DOS ORACIONES DE 100 PALABRAS SIN SALTARSE LÍNEAS
SI LA RESPUESTA A LA CONSULTA ES NULA, EXPLICAR SIEMPRE QUE NO SE ENCONTRARON REGISTROS
EXPLICA SIEMPRE COMO ERES INGENIERO
SIEMPRE OCULTE LAS VARIABLES Y NOMBRES DE COLUMNAS DE SU RESPUESTA
RESPONDA SIEMPRE QUE SU RESPUESTA CORRESPONDE AL ALCANCE DE LA PREGUNTA
Responda la siguiente pregunta del texto anterior.

Q: {question}
A:\n
""",

    "id_prompt_1":"""
    
    Previous knowledge, columns and their values:

    Valores unicos para estado:
                    [Autorizacion, Closed, Canceled,  Evaluar,  Implementar, Review,  Nuevo, Programado]

    Valores unicos para efectividad_del_cambio:
                    [Exitoso, No exitoso, Null]
    
    Valores unicos para tipo:
                    [Emergencia, Normal]
    
    Valores unicos para categoria:
                    [Infraestructura, BCP, Aplicaciones, Servicios a inmuebles]
    
    Valores unicos para suspension_del_servicio:
                    [Si, No, No Aplica]
    
    Valores unicos para clasificacion:
                    [Proyecto, Continuidad, No aplica]
    
    Valores unicos para cumplio_con_la_documentacion_requerida:
                    [Si, No, No aplica, ""]

    Si existe, extraiga las columnas presentadas anteriormente de la siguiente pregunta en formato JSON. Extraiga precisamente los términos exactos presentes.

     SI HAY VALORES DE FECHA, CONVIERTELOS AL FORMATO aaaa-MM-dd.

     MENCIONAR SÓLO LAS ENTIDADES EXACTAS PRESENTES EN LA PREGUNTA:

    {question}\n    
    """,

    "id_prompt_2":"""
    Previous knowledge, columns and their values:

        Valores unicos para area:
                        [Arquitectura Empresarial, Arquitectura IT, Arquitectura y Soporte de Afilacion, Arquitectura Soluciones de Negocio, 
                        Competitividad Comercial, Competitividad Comercial, Desarrollo Móvil, Desarrollo y Soporte, Devops, Innovación y Desarrollo Digital, 
                        Innovacion y microservicios, Operación IT, Soporte Técnico, Planeacion IT, Producción y Control de Cambios, Seguridad IT, 
                        Servicios a Inmuebles, Seguridad de la informacion, Sistemas Administrativos, Soporte Técnico]
        
        Algunos valores de solicitado_por:
                        [MARTIN FRANCISCO GUZMAN ULLOA,ALEJANDRO  MUÑOZ  NAJERA, JOSE DANIEL GLORIA BECERRIL, ANA LAURA RODRIGUEZ LOZANO, GERARDO CERVANTES GASCON]
        
        Valores unicos para riesgo:
                        [Ato, Bajo, Moderado]
        
        Valores unicos para respeto_la_ventana_de_suspension:
                        [Si, No, No Aplica,Null]

        Valores unicos para servicios_operando_correctamente:
                        [Si, No, No se confirmo, ""]
        
        Valores unicos para impacto_en_otros_servicios:
                        [Si, No, ""]

    Si existe, extraiga SÓLO las columnas presentadas anteriormente de la siguiente pregunta en formato JSON. Extraiga precisamente los términos exactos presentes.

    Al extraer las entidades, asegúrese de extraer aquellas que sean idénticas a las mencionadas anteriormente.
    Diferenciar singular y plural. Si más de una palabra es similar, tome la secuencia más similar

    {question}\n
    """,

    "id_prompt_3":"""
    Previous knowledge, columns and their values:

    Valores unicos para matriz_de_usuarios:
                        [Si, No, No Aplica, ""]
        
        Valores unicos para impacto:
                        [1. No conlleva impactos severos,  2.Puede repercutir en la calidad ofrecida, 3.Causa pérdidas significativas en ingresos e incapacita servicios]
        
        Valores unicos para urgencia:
                        [1. Puede esperar a la siguiente versión, 2.No debe esperar la siguiente versión,  3.Requerimiento urgente]
        
        Valores unicos para prioridad:
                        [1 - Urgente,  2 - Alta,  Media, Baja]

        Valores unicos para primero_Responsable_de_Autorizar:
                        [ECAB, CAB, ""]
        
        Algunos valores de ultimo_Responsable_de_autorizar:
                        [CAB,  CAB CONTIENGENCIA,  ECAB,  ECAB SUBDIRECCION,  ""]
        
        Algunos valores de nombre_del_responsable_de_autorizar:
                        [LEVY JASEF PONCE MARTINEZ, PAULA DANIELA ORTIZ LOPEZ, DAVID RAMON HERNANDEZ LEON, JUAN ALBERTO MENDEZ QUINTANA]

        Valores unicos para subdireccion:
                        [Desarrollo, Infraestructura, Digital,Servicios a inmuebles, Arquitectura, ""]
        
        Valores unicos para estado_de_conflicto:
                        [Sin conflicto, Conflicto, No ejecutar]
        
        Valores unicos para grupo_de_asignacion:
                        [Change Management, DevOps]
        
        Algunos valores de asignado_a:
                        [BEATRIZ GUADALUPE VALTIERRA ROMERO, PAULA DANIELA ORTIZ LOPEZ, HUGO BECERRA TRUJILLO]
        
        Valores unicos para se_aplico_plan_de_contingencia:
                        [Si, No, ""]

    Si existe, extraiga SÓLO las columnas presentadas anteriormente de la siguiente pregunta en formato JSON. Muestra sólo los presentes.
    Si no se menciona el valor, devuelve ''.

    {question}\n
    """
}