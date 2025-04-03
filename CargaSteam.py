import psycopg2
import streamlit as st
import base64
import io
from PIL import Image

# Cargar imagen para el logo
logo_path = "logo.png"  # Ruta relativa
logo_image = Image.open(logo_path)
st.image(logo_image, width=200)

# Cargar imagen para el fondo
fondo_path = "pexels-karolina-grabowska-8092510.jpg"  # Nombre correcto
fondo_image = Image.open(fondo_path)

# Convertir la imagen a base64
buffer = io.BytesIO()
fondo_image.save(buffer, format="JPEG")
fondo_base64 = base64.b64encode(buffer.getvalue()).decode()

# Establecer el fondo de la aplicación
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{fondo_base64}");
        background-size: cover;
    }}
    </style>
    """,
    unsafe_allow_html=True
)


# Función para conectar a la base de datos
def conectar_db():
    try:
        conexion = psycopg2.connect(
            host="localhost",
            database="bd_admin",
            user="postgres",
            password="Admin1234"
        )
        return conexion
    except Exception as e:
        st.error(f"❌ Error al conectar a la base de datos: {e}")
        return None
# Función para ver la carga de trabajo de un funcionario por su ID
def ver_carga_trabajo():
    # Ingreso del ID del funcionario
    user_id = st.text_input("ID del funcionario:")

    # Botón para realizar la búsqueda
    if st.button("Buscar Carga de Trabajo"):
        if user_id:
            # Conectar a la base de datos
            conexion = conectar_db()
            if conexion:
                cursor = conexion.cursor()
                try:
                    # Realizar la consulta para obtener los datos de la carga de trabajo
                    cursor.execute(f"SELECT funcionario_id, carga_total_trabajo FROM tb_carga_trabajo WHERE funcionario_id = {user_id}")
                    row = cursor.fetchone()

                    if row:
                        # Si se encuentra el registro, mostrarlo
                        funcionario_id, carga_total_trabajo = row
                        resultado = f"Carga de trabajo del funcionario con ID {funcionario_id} es: {carga_total_trabajo} horas"
                        st.success(resultado)
                    else:
                        st.info("No se encontraron registros para este ID.")
                except Exception as e:
                    st.error(f"Error al consultar la base de datos: {e}")
                finally:
                    cursor.close()
                    conexion.close()
# Función para ver todas las cargas de trabajo con filtro
def ver_todas_cargas_trabajo():
    # Función para mostrar las cargas de trabajo con el orden deseado
    def mostrar_cargas(orden="ASC"):
        # Conectar a la base de datos
        conexion = conectar_db()
        if conexion:
            cursor = conexion.cursor()
            try:
                # Realizar la consulta con orden dinámico
                cursor.execute(f"SELECT funcionario_id, carga_total_trabajo FROM tb_carga_trabajo ORDER BY funcionario_id {orden}")
                rows = cursor.fetchall()

                # Mostrar los resultados
                if rows:
                    for row in rows:
                        funcionario_id, carga_total_trabajo = row
                        st.write(f"Funcionario ID: {funcionario_id}, Carga Total de Trabajo: {carga_total_trabajo} horas")
                else:
                    st.info("No se encontraron registros.")
            except Exception as e:
                st.error(f"Error al consultar la base de datos: {e}")
            finally:
                cursor.close()
                conexion.close()

    # Título de la sección
    st.title("Ver Todas las Cargas de Trabajo")

    # Botones para filtrar por orden ascendente o descendente
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Orden Ascendente"):
            mostrar_cargas("ASC")
    with col2:
        if st.button("Orden Descendente"):
            mostrar_cargas("DESC")
# Función para agregar un nuevo funcionario
def agregar_funcionario():
    st.title("Agregar Funcionario")

    # Campos de entrada
    funcionario_id = st.text_input("Id del funcionario")
    nombre = st.text_input("Nombre")
    dependencia = st.text_input("Dependencia")
    puesto = st.text_input("Puesto")
    jornada = st.number_input("Jornada (Horas/día)", min_value=0.0)
    feriados = st.number_input("Feriados (Días)", min_value=0.0)
    horas_extra = st.number_input("Horas extra (Horas)", min_value=0.0)
    vacaciones = st.number_input("Vacaciones (Días)", min_value=0.0)
    incapacidades = st.number_input("Incapacidades (Días)", min_value=0.0)
    permiso = st.number_input("Permiso (Días)", min_value=0.0)
    comentarios = st.text_area("Comentarios")

    # Botón para agregar el funcionario
    if st.button("Agregar Funcionario"):
        # Validaciones básicas
        if not funcionario_id.isdigit():
            st.warning("El Id debe ser un número.")
            return
        if not nombre or not dependencia or not puesto:
            st.warning("Los campos Nombre, Dependencia y Puesto son obligatorios.")
            return

        # Paso 1: Multiplicar la jornada laboral por 260 (días laborales del año)
        dias_laborales = 260  # Número de días laborales por año
        total_laborable_base = jornada * dias_laborales  # Jornada multiplicada por los días laborales
        st.write(f"Total Laborable Base (Jornada * Días Laborales): {total_laborable_base}")

        # Paso 2: Sumar vacaciones, feriados, incapacidades y permiso, multiplicados por la jornada laboral
        horas_no_laborables = (vacaciones + feriados + incapacidades + permiso) * jornada
        st.write(f"Total Horas No Laborables (Vacaciones + Feriados + Incapacidades + Permiso * Jornada): {horas_no_laborables}")

        # Paso 3: Sumar las horas extra al total laborable
        total_laborable = total_laborable_base + horas_extra
        st.write(f"Total Laborable después de agregar Horas Extra: {total_laborable}")

        # Paso 4: Restar horas no laborables del total laborable
        total_laborable -= horas_no_laborables
        st.write(f"Total Laborable después de restar Horas No Laborables: {total_laborable}")

        # Conectar a la base de datos
        conexion = conectar_db()
        if conexion:
            cursor = conexion.cursor()
            try:
                # Verificar si el Id ya existe en la tabla tb_funcionarios
                cursor.execute("SELECT * FROM tb_funcionarios WHERE \"Id\" = %s", (funcionario_id,))
                if cursor.fetchone():
                    st.warning(f"El Id {funcionario_id} ya está en uso.")
                    return

                # Insertar el nuevo funcionario en la base de datos
                cursor.execute(
                    """INSERT INTO tb_funcionarios 
                    ("Id", "Nombre", "Dependencia", "Puesto", "Jornada", "Feriados", "Horas_extra", 
                    "Vacaciones", "Incapacidades", "Permiso", "Otro/Comentarios")
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (funcionario_id, nombre, dependencia, puesto, jornada, feriados, horas_extra, 
                     vacaciones, incapacidades, permiso, comentarios)
                )

                # Verificar si el funcionario ya existe en la tabla tb_carga_trabajo
                cursor.execute("SELECT * FROM tb_carga_trabajo WHERE \"funcionario_id\" = %s", (funcionario_id,))
                if cursor.fetchone():
                    # Si ya existe, actualizar el campo horas_trabajo
                    cursor.execute(
                        """
                        UPDATE tb_carga_trabajo 
                        SET horas_trabajo = %s
                        WHERE funcionario_id = %s
                        """,
                        (total_laborable, funcionario_id)
                    )
                else:
                    # Si no existe, insertar un nuevo registro
                    cursor.execute(
                        """
                        INSERT INTO tb_carga_trabajo (funcionario_id, horas_trabajo)
                        VALUES (%s, %s)
                        """,
                        (funcionario_id, total_laborable)
                    )

                # Verificar y actualizar el valor de carga_total_trabajo
                cursor.execute("SELECT tiempo_laborado, horas_trabajo FROM tb_carga_trabajo WHERE funcionario_id = %s", (funcionario_id,))
                row = cursor.fetchone()
                if row:
                    tiempo_laborado = row[0] if row[0] else 0  # Asegurarse de que no sea None o vacío
                    horas_trabajo = row[1] if row[1] else 1  # Asegurarse de que no sea 0 para evitar división por cero
                    if horas_trabajo > 0:  # Para evitar división por cero
                        carga_total_trabajo = (tiempo_laborado / horas_trabajo) * 100
                        carga_total_trabajo = round(carga_total_trabajo, 2)  # Redondear a 2 decimales
                        cursor.execute(
                            """
                            UPDATE tb_carga_trabajo
                            SET carga_total_trabajo = %s
                            WHERE funcionario_id = %s
                            """,
                            (carga_total_trabajo, funcionario_id)
                        )
                        st.write(f"Carga total de trabajo actualizada: {carga_total_trabajo}%")
                
                conexion.commit()
                st.success("Funcionario agregado correctamente.")
            except Exception as e:
                st.error(f"Error al agregar funcionario: {e}")
            finally:
                cursor.close()
                conexion.close()


# Función para agregar actividad
def agregar_actividad():
    st.title("Agregar Actividad")

    # Campos del formulario
    funcionario_id = st.text_input("ID del funcionario:")
    numero_actividad = st.text_input("Número de actividad:")
    funcion = st.text_input("Función de la actividad:")
    cantidad = st.number_input("Cantidad de veces realizada:", min_value=1, step=1)
    tiempo_minimo = st.number_input("Tiempo mínimo:", min_value=0.0, step=0.1)
    tiempo_medio = st.number_input("Tiempo medio:", min_value=0.0, step=0.1)
    tiempo_maximo = st.number_input("Tiempo máximo:", min_value=0.0, step=0.1)
    unidad = st.selectbox("Unidad (minutos u horas):", ["minutos", "horas"])
    comentarios = st.text_area("Comentarios de la actividad:")

    if st.button("Agregar Actividad"):
        if not (funcionario_id and numero_actividad and funcion and cantidad and tiempo_minimo and tiempo_medio and tiempo_maximo and unidad):
            st.warning("Todos los campos deben ser completados.")
            return

        if unidad == "minutos":
            tiempo_minimo /= 60
            tiempo_medio /= 60
            tiempo_maximo /= 60

        tiempo_por_actividad = (tiempo_minimo + 4 * tiempo_medio + tiempo_maximo) / 6 * cantidad

        # Conectar a la base de datos
        conexion = conectar_db()
        if conexion:
            cursor = conexion.cursor()
            try:
                # Verificar si el ID del funcionario existe
                cursor.execute('SELECT * FROM tb_funcionarios WHERE "Id" = %s', (funcionario_id,))
                if not cursor.fetchone():
                    st.warning(f"El ID {funcionario_id} no existe en la base de datos.")
                    return

                # Insertar la actividad
                cursor.execute(
                    """
                    INSERT INTO tb_actividades 
                    (id_funcionario, numero_actividad, funcion, cantidad, tiempo_minimo, tiempo_medio, tiempo_maximo, unidad, comentarios)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (funcionario_id, numero_actividad, funcion, cantidad, tiempo_minimo, tiempo_medio, tiempo_maximo, unidad, comentarios)
                )

                # Actualizar el tiempo por actividad
                cursor.execute(
                    """
                    UPDATE tb_actividades
                    SET tiempo_por_actividad = %s
                    WHERE id_funcionario = %s AND numero_actividad = %s
                    """,
                    (tiempo_por_actividad, funcionario_id, numero_actividad)
                )

                # Actualizar el tiempo laborado en la tabla tb_carga_trabajo
                cursor.execute(
                    """
                    UPDATE tb_carga_trabajo
                    SET tiempo_laborado = (
                        SELECT SUM(tiempo_por_actividad)
                        FROM tb_actividades
                        WHERE id_funcionario = %s
                        GROUP BY id_funcionario
                    )
                    WHERE funcionario_id = %s;
                    """,
                    (funcionario_id, funcionario_id)
                )

                # Verificar si el funcionario ya tiene un registro en tb_carga_trabajo
                cursor.execute('SELECT * FROM tb_carga_trabajo WHERE funcionario_id = %s', (funcionario_id,))
                if not cursor.fetchone():
                    cursor.execute(
                        """
                        INSERT INTO tb_carga_trabajo (funcionario_id, tiempo_laborado)
                        VALUES (%s, (
                            SELECT SUM(tiempo_por_actividad)
                            FROM tb_actividades
                            WHERE id_funcionario = %s
                            GROUP BY id_funcionario
                        ));
                        """,
                        (funcionario_id, funcionario_id)
                    )

                # Actualizar el campo carga_total_trabajo después de agregar la actividad
                cursor.execute("SELECT horas_trabajo, tiempo_laborado FROM tb_carga_trabajo WHERE funcionario_id = %s", (funcionario_id,))
                row = cursor.fetchone()
                if row:
                    horas_trabajo = row[0] if row[0] else 1  # Evitar división por cero
                    tiempo_laborado = row[1] if row[1] else 0
                    carga_total_trabajo = (tiempo_laborado / horas_trabajo) * 100
                    carga_total_trabajo = round(carga_total_trabajo, 2)

                    # Actualizar el campo carga_total_trabajo en la base de datos
                    cursor.execute(
                        "UPDATE tb_carga_trabajo SET carga_total_trabajo = %s WHERE funcionario_id = %s",
                        (carga_total_trabajo, funcionario_id)
                    )

                # Confirmar la transacción
                conexion.commit()
                st.success("Actividad agregada correctamente y tiempo laborado actualizado.")
            except Exception as e:
                st.error(f"Error al agregar la actividad: {e}")
            finally:
                cursor.close()
                conexion.close()

def menu_principal():
    st.title("Menú Principal")
    
    # Menú desplegable para seleccionar la acción
    opcion = st.selectbox(
        "Selecciona una opción:",
        ["Ver Carga de Trabajo por ID", "Ver Todas las Cargas de Trabajo", "Agregar Funcionario", "Agregar Actividad"]
    )
    
    # Ejecutar la acción seleccionada
    if opcion == "Ver Carga de Trabajo por ID":
        ver_carga_trabajo()
    
    elif opcion == "Ver Todas las Cargas de Trabajo":
        ver_todas_cargas_trabajo()
    
    elif opcion == "Agregar Funcionario":
        agregar_funcionario()
    
    elif opcion == "Agregar Actividad":
        agregar_actividad()

if __name__ == "__main__":
    menu_principal()
